import requests
from bs4 import BeautifulSoup
import pandas as pd
import pysbd
import re


########################
## Year based search   ##
########################

BASE_URL = "https://www.wikidata.org/wiki/Wikidata:Requests_for_deletions/Archive"

def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def get_year_urls():
    soup = get_soup(BASE_URL)
    year_urls = {}
    for link in soup.select('a[href^="/wiki/Wikidata:Requests_for_deletions/Archive/"]'):
        year_url = link['href']
        if year_url.endswith(tuple(str(year) for year in range(2012, 2025))):
            year = year_url.split('/')[-1]
            full_year_url = "https://www.wikidata.org" + year_url
            year_urls[year] = full_year_url
    return year_urls

def get_month_day_urls(year_url):
    soup = get_soup(year_url)
    month_day_urls = []
    for link in soup.select('a[href^="/wiki/Wikidata:Requests_for_deletions/Archive/"]'):
        date_url = link['href']
        if len(date_url.split('/')) >= 7:
            full_date_url = "https://www.wikidata.org" + date_url
            if full_date_url not in month_day_urls:
                month_day_urls.append(full_date_url)
    return month_day_urls

def extract_outcome_from_dd(dd):
    try:
        result_tag = dd.find('b')
        if result_tag:
            return result_tag.get_text().strip()
        return 'unknown'
    except:
        return 'unknown'

def extract_discussions(url):
    soup = get_soup(url)
    discussions = []
    for h2 in soup.find_all('h2'):
        title_tag = h2.find('a')
        if title_tag and 'Q' in title_tag.get_text():
            title = title_tag.get_text().strip()
            discussion_parts = []
            last_dd = None
            for sibling in h2.find_all_next():
                if sibling.name == 'h2':
                    break
                if sibling.name == 'p':
                    discussion_parts.append(sibling.get_text(separator=' ', strip=True))
                if sibling.name == 'dl':
                    dds = sibling.find_all('dd')
                    if dds:
                        for dd in dds[:-1]:
                            discussion_parts.append(dd.get_text(separator=' ', strip=True))
                        last_dd = dds[-1]
            discussion_text = ' '.join(discussion_parts) if discussion_parts else 'No discussion found'
            outcome = extract_outcome_from_dd(last_dd) if last_dd else 'Outcome not found'
            entity_url = url + '#' + title
            discussions.append({
                "title": title,
                "discussion": discussion_text,
                "outcome": outcome,
                "url": entity_url,
                'date': url.split('Archive/')[-1]
            })
    return discussions

def remove_first_sentence_if_q_number(text):
    seg = pysbd.Segmenter(language="en", clean=False)
    sentences = seg.segment(text)
    if sentences and sentences[0].startswith('Q') and sentences[0][1:].isdigit():
        return ' '.join(sentences[1:])
    return text

def process_discussions_by_url_list(url_list):
    all_discussions = []
    for url in url_list:
        discussions = extract_discussions(url)
        all_discussions.extend(discussions)
    df = pd.DataFrame(all_discussions)
    if not df.empty:
        df['discussion'] = df['discussion'].apply(remove_first_sentence_if_q_number)
    return df


########################
## Title based search ##
########################

import requests
from bs4 import BeautifulSoup
import pandas as pd
import pysbd

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

def clean_discussion_tag(tag):
    for unwanted in tag.find_all(['span', 'img', 'a', 'div'], recursive=True):
        unwanted.decompose()
    return tag.get_text(separator=' ', strip=True)

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
            if node.has_attr('class') and 'plainlinks' in node['class']:
                continue
            if node.get('style', '').lower() == 'visibility:hidden;display:none':
                continue
            if node.find('span', id=title):
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

def extract_div_from_title(title, url=''):
    if url=='' or not url:
        base_url = 'https://www.wikidata.org/wiki/Wikidata:Requests_for_deletions'
        url = base_url + '#' + title
        text_url = base_url
        discussion_url = text_url + '#' + title


    response = requests.get(url)
    if response.status_code != 200:
        print(f"Could not fetch {url}")
        return pd.DataFrame(columns=['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label'])
    if title == '':
        title = url.split('#')[-1]

    soup = BeautifulSoup(response.content, 'html.parser')
    discussion_html, label, cleaned_discussion = extract_discussion_section(soup, title)

    text_url = 'https://www.wikidata.org/wiki/'+ url.split('#')[0]
    discussion_url = url

    df = pd.DataFrame([[title, text_url, discussion_url, cleaned_discussion, label]],
                      columns=['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label'])
    if label:
        df['label'] = df['label'].replace({
            'Deleted':'delete', 'Delete':'delete', 'delete':'delete', 'deleted':'delete', 
            'kept':'keep', 'keep':'keep', 'Keep':'keep', 'Kept':'keep', 
            'merge':'merge', 'Merge':'merge', 'Not done':'no_consensus', 
            'No consensus':'no_consensus', 'no consensus':'no_consensus'
        })
    df['discussion_cleaned'] = df['discussion_cleaned'].apply(split_text_into_sentences)

    return df


########################
## Collection function ##
########################


import pandas as pd

def collect_wikidata_entity(mode='year', title='', url='', years=[]):
    if mode not in ['title', 'year','url']:
        raise ValueError("mode must be either 'title' or 'year'")

    if mode == 'title':
        if not title or years:
            raise ValueError("For 'title' mode, 'title' must be provided and 'years' must be empty.")
        df = extract_div_from_title(title)
        df = df.rename(columns={'label':'outcome', 'discussion_cleaned':'discussion'})
        return df
    elif mode == 'url':
        if 'Archive' in url:
            archived_url = url.split('#')[0]
            title = url.split('#')[-1]
            disc_df = process_discussions_by_url_list([archived_url])
            disc_df['title'] = disc_df['title'].str.strip()
            title = title.strip()
            df = disc_df[disc_df['title'] == title]
            print(f"Found {len(df)} discussions for title {title}")
            if df.empty:
                return pd.DataFrame(columns=['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label'])
            df = df.rename(columns={'label':'outcome', 'discussion_cleaned':'discussion'})
            return df
        if title or years:
            raise ValueError("For 'url' mode, 'url' must be provided and 'title' must be empty.")
        df = extract_div_from_title('', url)
        df = df.rename(columns={'label':'outcome', 'discussion_cleaned':'discussion'})
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
            print(f"Processing year: {year}")

            year_urls = get_year_urls() 
            if str(year) not in year_urls:
                print(f"No URL found for year {year}")
                continue
            year_url = year_urls[str(year)]
            month_day_urls = get_month_day_urls(year_url)
            print(f"Found {len(month_day_urls)} month-day URLs for {year}")
            discussions_df = process_discussions_by_url_list(month_day_urls)
            
            if discussions_df.empty:
                continue

            discussions_df.rename(columns={'url':'discussion_url', 'outcome':'label', 'discussion':'discussion_cleaned'}, inplace=True)
            text_url = year_url
            discussions_df['text_url'] = text_url
            discussions_df['label'] = discussions_df['label'].replace({
                'Deleted':'delete', 'Delete':'delete', 'delete':'delete', 'deleted':'delete', 
                'kept':'keep', 'keep':'keep', 'Keep':'keep', 'Kept':'keep', 
                'merge':'merge', 'Merge':'merge', 'Not done':'no_consensus', 
                'No consensus':'no_consensus', 'no consensus':'no_consensus'
            })

            desired_columns = ['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label']
            for col in desired_columns:
                if col not in discussions_df.columns:
                    discussions_df[col] = ''
            discussions_df = discussions_df[desired_columns]

            df = pd.concat([df, discussions_df], ignore_index=True)
            df = df.rename(columns={'label':'outcome', 'discussion_cleaned':'discussion'})
        return df
    

