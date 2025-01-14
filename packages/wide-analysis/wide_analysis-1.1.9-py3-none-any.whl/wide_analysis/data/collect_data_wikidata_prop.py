import requests
from bs4 import BeautifulSoup
import pandas as pd
import pysbd
import re

#####################
# Utility functions #
#####################

def html_to_plaintext(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all(['p', 'li', 'dd', 'dl', 'ul']):
        tag.insert_before('\n')
        tag.insert_after('\n')
    for br in soup.find_all('br'):
        br.replace_with('\n')

    text = soup.get_text(separator=' ', strip=True)
    text = '\n'.join([line.strip() for line in text.splitlines() if line.strip() != ''])
    return text

def split_text_into_sentences(text):
    seg = pysbd.Segmenter(language="en", clean=False)
    sentences = seg.segment(text)
    return ' '.join(sentences)

def process_html_to_plaintext(df):
    if df.empty:
        return df
    if 'discussion' in df.columns:
        df['discussion_cleaned'] = df['discussion'].apply(html_to_plaintext)
    return df

def process_split_text_into_sentences(df):
    if df.empty:
        return df
    if 'discussion_cleaned' in df.columns:
        df['discussion_cleaned'] = df['discussion_cleaned'].apply(split_text_into_sentences)
    return df

###########################
# Year-based extraction   #
###########################

def extract_outcome_from_div(div):
    try:
        consensus_keywords = ['Deleted', 'Delete', 'delete', 'deleted', 'kept', 'keep', 'Keep', 'Kept', 'merge', 'Merge', 'Not done', 'No consensus', 'no consensus']
        dd_tags = div.find_all('dd')
        for dd in dd_tags:
            b_tag = dd.find('b')
            if b_tag and b_tag.text.strip() in consensus_keywords:
                return b_tag.text.strip()
            img_tag = dd.find('img')
            if img_tag and 'X_mark.svg' in img_tag.get('src', ''):
                next_b_tag = dd.find_next('b')
                if next_b_tag and next_b_tag.text.strip() in consensus_keywords:
                    return next_b_tag.text.strip()

        return 'no consensus'
    except Exception as e:
        print(f"Error extracting outcome: {e}")
        return 'unknown'


def extract_cleaned_discussion(div):
    discussion_parts = []
    discussion_items = div.find_all(['li', 'dd'])
    
    for item in discussion_items:
        for tag in item.find_all(['span', 'img', 'a']):
            tag.decompose() 
        cleaned_text = item.get_text(separator=' ', strip=True)
        discussion_parts.append(cleaned_text)
    return ' '.join(discussion_parts)

def extract_div_contents_with_additional_columns(url):
    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame(columns=['title', 'text_url', 'deletion_discussion', 'label', 'confirmation', 'verdict', 'discussion'])

    soup = BeautifulSoup(response.content, 'html.parser')
    divs = soup.find_all('div', class_='boilerplate metadata discussion-archived mw-archivedtalk')
    if len(divs) == 0:
        print(f"No discussions found in {url}. Please check the structure.")
    
    data = []
    for i, div in enumerate(divs):
        try:
            heading_div = div.find_previous('div', class_='mw-heading mw-heading2 ext-discussiontools-init-section')
            if heading_div:
                h2_tag = heading_div.find('h2')
                if h2_tag:
                    id = h2_tag.get('id', 'Unknown ID')
                    if id:
                        text_url = url+'#' + id 
                        title = id.replace('(page does not exist)', '').strip()
                    else:
                        title = "Unknown Title"
                        text_url = "Unknown URL"
                else:
                    title = "Unknown Title"
                    text_url = "Unknown URL"
            else:
                # fallback for rare cases
                title = "Unknown Title"
                text_url = "Unknown URL"

            deletion_discussion = div.prettify()
            label = extract_outcome_from_div(div)
            cleaned_discussion = extract_cleaned_discussion(div)
            parts = deletion_discussion.split('<div class="mw-heading mw-heading3">')
            discussion = parts[0] if len(parts) > 0 else ''
            verdict = '<div class="mw-heading mw-heading3">' + parts[1] if len(parts) > 1 else ''

            data.append([title, text_url, deletion_discussion, label, '', cleaned_discussion, verdict])
        except Exception as e:
            print(f"Error processing div #{i} in {url}: {e}")
            continue

    df = pd.DataFrame(data, columns=['title', 'text_url', 'deletion_discussion', 'label', 'confirmation', 'discussion', 'verdict'])
    return df

def scrape_wikidata_deletions(wikidata_url):
    months_data = []
    month_found = False
    for month in range(1, 13):
        month_url = f"{wikidata_url}/{month}"
        print(f"Processing month: {month}")
        response = requests.get(month_url)
        if response.status_code == 200:
            df = extract_div_contents_with_additional_columns(month_url)
            if not df.empty:
                df = process_html_to_plaintext(df)
                df['discussion_cleaned'] = df['discussion_cleaned'].apply(lambda x: ' '.join(pysbd.Segmenter(language="en", clean=False).segment(x)[1:]) if x else x)
                months_data.append(df)
                month_found = True
        else:
            print(f"No month-specific page found for {month_url}.")

    if month_found and months_data:
        all_data = pd.concat(months_data, ignore_index=True)
        return all_data
    
    print(f"Attempting year-based extraction for base URL: {wikidata_url}")
    df = extract_div_contents_with_additional_columns(wikidata_url)
    if not df.empty:
        df = process_html_to_plaintext(df)
        df['discussion_cleaned'] = df['discussion_cleaned'].apply(lambda x: ' '.join(pysbd.Segmenter(language="en", clean=False).segment(x)[1:]) if x else x)
        return df

    print("No data found using month-specific or year-based extraction.")
    return pd.DataFrame()

############################
# Title-based extraction   #
############################

def extract_outcome_from_text_elements(elements):
    consensus_keywords = [
        'Deleted', 'Delete', 'delete', 'deleted', 
        'kept', 'keep', 'Keep', 'Kept', 
        'merge', 'Merge', 'Not done', 'No consensus', 'no consensus'
    ]
    for el in elements:
        b_tags = el.find_all('b')
        for b in b_tags:
            if b.text.strip() in consensus_keywords:
                return b.text.strip()
    return ''

def clean_discussion_tag(tag):
    for unwanted in tag.find_all(['span', 'img', 'a', 'div'], recursive=True):
        unwanted.decompose()
    return tag.get_text(separator=' ', strip=True)

def extract_discussion_section(soup, title):
    h2_tag = soup.find('h2', id=title)
    if not h2_tag:
        print(f"No heading found with id={title}")
        return '', '', ''
    heading_div = h2_tag.find_parent('div', class_='mw-heading mw-heading2 ext-discussiontools-init-section')
    if not heading_div:
        print(f"No heading div found for {title}")
        return '', '', ''

    next_heading_div = heading_div.find_next('div', class_='mw-heading mw-heading2 ext-discussiontools-init-section')
    discussion_nodes = []
    for sibling in heading_div.next_siblings:
        if sibling == next_heading_div:
            break
        discussion_nodes.append(sibling)

    discussion_tags = []
    for node in discussion_nodes:
        if getattr(node, 'name', None) in ['p', 'ul', 'dl']:
            if node.find('span', id=title) or node.get('style', '').lower() == 'visibility:hidden;display:none':
                continue
            discussion_tags.append(node)

    if not discussion_tags:
        return '', '', ''

    label = extract_outcome_from_text_elements(discussion_tags)
    discussion_html_parts = [str(tag) for tag in discussion_tags]
    cleaned_parts = []
    for tag in discussion_tags:
        text = clean_discussion_tag(tag)
        if text:
            cleaned_parts.append(text)

    cleaned_discussion = ' '.join(cleaned_parts)
    discussion_html = '\n'.join(discussion_html_parts)
    return discussion_html, label, cleaned_discussion

def extract_div_from_title(url, title):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Could not fetch {url}")
        return pd.DataFrame(columns=['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label'])

    soup = BeautifulSoup(response.content, 'html.parser')
    discussion_html, label, cleaned_discussion = extract_discussion_section(soup, title)

    text_url = 'https://www.wikidata.org/wiki/Wikidata:Properties_for_deletion'
    discussion_url = text_url + '#' + title

    data = [[title, text_url, discussion_url, cleaned_discussion, label]]
    df = pd.DataFrame(data, columns=['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label'])
    return df

############################
# Unified collect function #
############################

def collect_wikidata(mode='year', title='', url='', years=[]):
    df_list = []
    if mode not in ['title', 'year','url']:
        raise ValueError("mode must be either 'title' or 'year' or 'url'.")

    if mode == 'title':

        if not title or years:
            raise ValueError("For 'title' mode, 'title' must be provided and 'years' must be empty.")
        url = 'https://www.wikidata.org/wiki/Wikidata:Properties_for_deletion#' + title
        df = extract_div_from_title(url, title)
        if not df.empty and 'label' in df.columns and df['label'].notnull().any():
            df['label'] = df['label'].replace({
                'Deleted':'delete', 'Delete':'delete', 'delete':'delete', 'deleted':'delete', 
                'kept':'keep', 'keep':'keep', 'Keep':'keep', 'Kept':'keep', 
                'merge':'merge', 'Merge':'merge', 'Not done':'no_consensus', 
                'No consensus':'no_consensus', 'no consensus':'no_consensus'
            })
        df = df.rename(columns={'discussion_cleaned':'discussion'})
        return df
    
    elif mode == 'url':
        if title or years:
            raise ValueError("For 'url' mode, 'url' must be provided and 'title' must be empty.")
        df = extract_div_contents_with_additional_columns(url)
        if not df.empty and 'label' in df.columns and df['label'].notnull().any():
            df['label'] = df['label'].replace({
                'Deleted':'delete', 'Delete':'delete', 'delete':'delete', 'deleted':'delete', 
                'kept':'keep', 'keep':'keep', 'Keep':'keep', 'Kept':'keep', 
                'merge':'merge', 'Merge':'merge', 'Not done':'no_consensus', 
                'No consensus':'no_consensus', 'no consensus':'no_consensus'
            })
        else:
            return ValueError("No data found for the provided URL.")
        df = df.rename(columns={'discussion_cleaned':'discussion'})
        return df

    elif mode == 'year':
        if title or not years:
            raise ValueError("For 'year' mode, 'years' must be provided and 'title' must be empty.")

        if isinstance(years, list) and len(years) == 2:
            start_year, end_year = years
            years = list(range(start_year, end_year + 1))
        elif isinstance(years, int): 
            years = [years]

        df = pd.DataFrame()
        for year in years:
            wikidata_url = f'https://www.wikidata.org/wiki/Wikidata:Properties_for_deletion/Archive/{year}'  
            deletions_df = scrape_wikidata_deletions(wikidata_url)
            if deletions_df.empty:
                continue

            columns_to_drop = ['confirmation', 'discussion', 'verdict', 'deletion_discussion']
            deletions_df = deletions_df.drop(columns=[col for col in columns_to_drop if col in deletions_df.columns], errors='ignore')

            if 'label' in deletions_df.columns:
                deletions_df.rename(columns={'label':'label'}, inplace=True)
                deletions_df['label'] = deletions_df['label'].replace({
                    'Deleted':'delete', 'Delete':'delete', 'delete':'delete', 'deleted':'delete', 
                    'kept':'keep', 'keep':'keep', 'Keep':'keep', 'Kept':'keep', 
                    'merge':'merge', 'Merge':'merge', 'Not done':'no_consensus', 
                    'No consensus':'no_consensus', 'no consensus':'no_consensus'
                })


            if 'text_url' in deletions_df.columns:
                deletions_df.rename(columns={'text_url':'discussion_url'}, inplace=True)
            deletions_df['text_url'] = wikidata_url
            if 'label' not in deletions_df.columns:
                deletions_df['label'] = ''

            for col in ['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label']:
                if col not in deletions_df.columns:
                    deletions_df[col] = ''
            print(f"Year: {year}, Data shape: {deletions_df.columns}")
            deletions_df = deletions_df[['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label']]

            deletions_df['year'] = year
            df_list.append(deletions_df)
            # print(f"Year: {year}, Data shape: {deletions_df.shape}")
            # df = pd.concat([df, deletions_df], ignore_index=True)
            df = pd.concat(df_list, ignore_index=True)
            df = df.rename(columns={'discussion_cleaned':'discussion'})
        return df
