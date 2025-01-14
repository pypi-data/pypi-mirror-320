import requests
from bs4 import BeautifulSoup
import pandas as pd
import pysbd
import re

def extract_outcome_from_div(div):
    try:
        # Extracting the decision from <b> tag that contains result like 'no consensus', 'deleted', etc.
        result = div.find(text=re.compile(r'The result was:')).find_next('b')
        if result:
            return result.text.strip()
        return 'no consensus'
    except Exception as e:
        print(f"Error extracting outcome: {e}")
        return 'unknown'

def html_to_plaintext(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all(['p', 'li', 'dd', 'dl']):
        tag.insert_before('\n')
        tag.insert_after('\n')
    for br in soup.find_all('br'):
        br.replace_with('\n')

    text = soup.get_text(separator=' ', strip=True)
    text = '\n'.join([line.strip() for line in text.splitlines() if line.strip() != ''])
    return text

def process_html_to_plaintext(df):
    if df.empty:
        return df
    df['discussion_cleaned'] = df['discussion'].apply(html_to_plaintext)
    return df

def split_text_into_sentences(text):
    seg = pysbd.Segmenter(language="en", clean=False)
    sentences = seg.segment(text)
    for i, sentence in enumerate(sentences):
        if 'The result was:' in sentence:
            return ' '.join(sentences[i+1:])
    return ' '.join(sentences[1:])


def process_split_text_into_sentences(df):
    if df.empty:
        return df
    df['discussion_cleaned'] = df['discussion_cleaned'].apply(split_text_into_sentences)
    df['discussion_cleaned'] = df['discussion_cleaned'].apply(lambda x: x.replace("The above discussion is preserved as an archive of the debate. Please do not modify it. Subsequent comments should be made on the appropriate discussion page (such as the article's talk page or in a deletion review ). No further edits should be made to this page.", ''))
    #df['discussion_cleaned'] = df['discussion_cleaned'].apply(cleanup_initial_sentences)
    return df

def collect_wikiquote_title(title='all', base_url='https://en.wikiquote.org/wiki/Wikiquote:Votes_for_deletion_archive'):
    titles = []
    text_urls = []
    labels = []
    deletion_discussions = []
    if title == 'all':
        url = base_url
    else:
        url = base_url + '#' + title.replace(' ', '_')
    
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        if title == 'all':
            divs = soup.find_all('div', class_='boilerplate metadata vfd')
        else:
            # For specific title, find a div that matches the title
            divs = soup.find_all('div', class_='boilerplate metadata vfd')
            divs = [div for div in divs if div.find('div', class_="mw-heading mw-heading2 ext-discussiontools-init-section") and title in div.find('div', class_="mw-heading mw-heading2 ext-discussiontools-init-section").text]

        no_divs = len(divs)
        print(f"Found {no_divs} div(s) with the expected classes.")

        if no_divs >= 1:
            for div in divs:
                heading_div = div.find('div', class_="mw-heading mw-heading2 ext-discussiontools-init-section")
                if heading_div:
                    found_title = heading_div.text.strip()
                    titles.append(found_title.replace('[edit]', ''))
                    text_url = base_url + '#' + found_title.replace(' ', '_') 
                    text_urls.append(text_url)
                    label = extract_outcome_from_div(div)
                    labels.append(label)
                    deletion_discussions.append(div.prettify())
                else:
                    print("No heading div found with the expected classes.")

            df = pd.DataFrame({'title': titles, 'text_url': text_urls, 'label': labels, 'discussion': deletion_discussions})
            df = process_html_to_plaintext(df)
            df = process_split_text_into_sentences(df)
            df['label'] = df['label'].replace({
                'Deleted':'delete', 'Delete':'delete', 'delete':'delete', 'deleted':'delete', 'deleted.':'delete', 'speedy deleted test page':'delete', 'Deleted and protected with a message':'delete',
                'delete both':'delete', 'delete everything':'delete', 'Deleted due to copyvio':'delete', 'delete after various merges':'delete', 'delete 3 quoteless, keep 1 redirect':'delete',
                'Consensus to remove from Wikiquote, but only if it is not merged into another article':'delete', 'Consensus to remove from Wikiquote, but not how':'delete', 'delete, pending technical fix':'delete', 'delete all':'delete', 'delete Portal:portal, no consensus/keep Template:Wikimedia':'delete',
                'Speedy-deleted':'delete', 'Speedy deleted':'delete', 'Speedy-deleted, no meaningful content':'delete',
                'kept':'keep', 'Kept.':'keep', 'Keep':'keep', 'keep':'keep', 'Kept':'keep', 'No consensus/keep':'keep', 'kept/no consensus':'keep', 'Kept; lack of consensus':'keep', 'kept after copyvio removal':'keep',
                'Speedy-kept':'keep', 'Speedy kept':'keep',
                'merge':'merge', 'Merge':'merge', 'merged':'merge', 'Merged':'merge', 'merged into Azerbaijani proverbs':'merge', 'Merge with Stephen Covey':'merge', 'Merge with Lyrics':'merge',
                'merge and redirect':'merge', 'merge with Crusade (TV series)':'merge', 'Merged to Health':'merge', 'merge with 3rd Rock from the Sun':'merge',
                'redirect to List of proverbs':'redirect', 'keep as redirect':'redirect', 'Redirect to Inuyasha':'redirect', 'Redirected to Humor':'redirect', 'Redirected to Doctor Who':'redirect',
                'Redirect without text':'redirect', 'Proverbs turned to redirect to List of proverbs':'redirect', 'redirect to Drugs':'redirect', 'redirect to Advertising slogans':'redirect',
                'redirect to Jalal al-Din Muhammad Rumi':'redirect', 'redirect':'redirect', 'Redirected':'redirect', 'move to Category:United States Marines':'redirect', 'move to Die Hard: With a Vengeance':'redirect',
                'move to Star Wars Jedi Knight: Jedi Academy':'redirect', 'move to Lucien Lévy-Bruhl':'redirect', 'move to Dave Finlay':'redirect', 'move to User:Quenzer':'redirect', 'moved':'redirect', 
                'moved to Monument inscriptions':'redirect', 'transwiki to Wikipedia, then delete':'redirect', 'Transwiki to Wikipedia':'redirect', 'Transwiki to Wikipedia':'redirect',
                'delete His Holiness the Dalai Lama, redirect Dalai Lama to Tenzin Gyatso, 14th Dalai Lama':'redirect',
                'move':'redirect', 'keep Just war theory, redirect Just war, delete Just War Theory':'no_consensus','move to Wikisource':'redirect',\
                'kept.':'keep', 'Keep as Redirect':'redirect', 'Deleted.':'delete', '1 delete, 1 redirect':'redirect', 'moved to User:Quenzer':'redirect',\
                'transwiki, then delete':'delete', 'merge with Lyrics':'redirect','Deleted all three images':'delete',\
                'No consensus':'no_consensus', 'no consensus':'no_consensus', 'inconclusive; no action taken.':'no_consensus', 'UNIDENTIFIED':'no_consensus'
            })
            return df
        else:
            print("No divs found with the expected classes.")
            return None
    else:
        print("Failed to retrieve the page.")
        return None

def collect_wikiquote(mode ='title',title = 'all', url = ''):
    if mode not in ['title', 'url']:
        raise ValueError("mode must be either 'title' or 'url'.")
    if mode == 'title' and title == 'all':
        base_url = 'https://en.wikiquote.org/wiki/Wikiquote:Votes_for_deletion_archive'
        df = collect_wikiquote_title(title, base_url)
        if df is not None:
            if 'discussion_cleaned' in df.columns:
                df = df[['title', 'text_url', 'label', 'discussion_cleaned']]
                df = df.rename(columns={'discussion_cleaned': 'discussion'})
            return df
    elif mode == 'url':
        df = collect_wikiquote_title('all', url)
        title = url.split('#')[-1].replace('_', ' ')
        df = df[df['title'].str.lower() == title.lower()].reset_index(drop=True)
        if not df.empty:
            if 'discussion_cleaned' in df.columns:
                df = df[['title', 'text_url', 'label', 'discussion_cleaned']]
                df = df.rename(columns={'discussion_cleaned': 'discussion'})
            return df
        else:
            raise ValueError(f"No data found for the url: {url}")
    else:
        base_url = 'https://en.wikiquote.org/wiki/Wikiquote:Votes_for_deletion'
        df = collect_wikiquote_title(title, base_url)
        if 'discussion_cleaned' in df.columns:
                df = df[['title', 'text_url', 'label', 'discussion_cleaned']]
                df = df.rename(columns={'discussion_cleaned': 'discussion'})
        return df
