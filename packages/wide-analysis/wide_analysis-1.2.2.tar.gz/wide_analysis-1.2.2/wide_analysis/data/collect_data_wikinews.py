import requests
from bs4 import BeautifulSoup
import pandas as pd
import pysbd
import re


################################
# Year based data collection ###
################################

def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()  
    return BeautifulSoup(response.text, 'html.parser')

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

def extract_fallback_discussion(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    discussion_parts = []
    for element in soup.find_all(['p', 'li', 'dd', 'ol'], recursive=False):
        discussion_parts.append(element.get_text(separator=' ', strip=True))
    return ' '.join(discussion_parts).strip()

def process_html_to_plaintext(df):
    if df.empty:
        return df
    df['discussion_cleaned'] = df['discussion'].apply(html_to_plaintext)
    for index, row in df.iterrows():
        if not row['discussion_cleaned'].strip():
            df.at[index, 'discussion_cleaned'] = extract_fallback_discussion(row['discussion_uncleaned']) 
    return df

def extract_outcome_from_div(div):
    try:
        result_phrase = div.find(text=re.compile(r'The result was to'))
        if result_phrase:
            result = result_phrase.find_next('b')
            if result:
                outcome_text = result.text.strip()
                if outcome_text.lower() == "please do not modify it":
                    return extract_following_sentence(div) or 'unknown'
                elif validate_outcome(outcome_text):
                    return outcome_text  
        li_outcome = div.find('li')
        if li_outcome and li_outcome.find('b'):
            outcome_text = li_outcome.find('b').text.strip()
            if outcome_text.lower() == "please do not modify it":
                return extract_following_sentence(div) or 'unknown'
            elif validate_outcome(outcome_text):
                return outcome_text

        dl_outcome = div.find('dl')
        if dl_outcome and dl_outcome.find('b'):
            outcome_text = dl_outcome.find('b').text.strip()
            if outcome_text.lower() == "please do not modify it":
                return extract_following_sentence(div) or 'unknown'
            elif validate_outcome(outcome_text):
                return outcome_text

        outcome_italic = div.find('dd')
        if outcome_italic and outcome_italic.find('i'):
            outcome_text = outcome_italic.find('i').get_text(strip=True)
            if outcome_text.lower() == "please do not modify it":
                return extract_following_sentence(div) or 'unknown'
            elif validate_outcome(outcome_text):
                return outcome_text
        return extract_following_sentence(div) or 'unknown'

    except Exception as e:
        print(f"Error extracting outcome: {e}")
        return 'unknown'


def extract_following_sentence(div):
    try:
        phrases = [
            "No further edits should be made to this discussion",
            "Please do not add any more comments and votes to this request",
            "No further edits should be made to this discussion."
        ]
        
        for phrase in phrases:
            phrase_location = div.find(text=re.compile(phrase))
            if phrase_location:
                following_text = ""
                for sibling in phrase_location.find_all_next(string=True):
                    if "Please do not modify it" in sibling:
                        continue
                    following_text += sibling.strip() + " "
                    if "." in sibling:
                        break
                sentence = following_text.split('.')[0].strip()
                if validate_outcome(sentence):
                    return sentence
        
        return None 

    except Exception as e:
        print(f"Error extracting following sentence: {e}")
        return None

def validate_outcome(outcome_text):
    label_mapping = {
        'delete': [
            'delete', 'delete ... unanimous', 'deleted', 'deleted as abandoned',
            'speedy delete', 'Delete', 'delete as redundant to existing template',
            'delete as unlikely to be used', 'delete but no prejudice against recreation when needed',
            'delete after Ottawahitech chose not to provide a rationale',
            'Delete, with no objection to recreation when needed.', 'Deleted', 
            'delete the Cigarette redirect and keep the NHS redirect.', 'Delete all articles', 'Tentatively sending through the usual abandonment process',
            'Delete all articles','This was completed already.'
        ],
'speedy delete': [ 

            'speedy delete', 'speedy deleted', 'speedy deleted test page', 'Speedy-deleted', 'Speedy deleted', 'Speedy-deleted, no meaningful content',
            'Speeded as "old prep"', 'Speedied as "old prep"  -- Pi zero ( talk ) 23:42, 10 February 2020 (UTC)   [  reply  ]  __DTELLIPSISBUTTON__{"threadItem":{"timestamp":"2020-02-10T23:42:00'
],

        'keep': [
             'keep',
            'Do not undelete. The content should be kept by the author off-wiki, and can be included as a part of another story that is current',
            'Personal details have been redacted and hidden from public view together with a NOINDEX flag',

            ],
        'redirect': [
            'soft redirect'
        ],
        'merge': [
            'convert near-clone of mainspace article to use {{topic cat}}; apply {{correction}} to mainspace article'
        ],
        'no_consensus': [
            'No consensus to delete. However, there clearly is a consensus that if we are to have this template, we aren\'t to use it in its present form.',
            'no consensus', 'No consensus',
            "At this time, it's unclear if there's a consensus to keep but abundantly clear there isn't one to delete."
        ],
        'comment': [
            'Remove', 'SVT', 'withdraw the deletion request', 'On consideration, speedied as unused and lacking fair-use rationale',
            'Moved to userspace', 'Withdrawn to allow interview re-focus','More userspace drafts       This is the second batch of a large number of draft articles in userspace',
            'This was completed already ', 'Do not undelete. The content should be kept by the author off-wiki, and can be included as a part of another story that is current',

        ],
        'withdrawn': ['Withdrawn to allow interview re-focus', 
        ]
    }

    

    outcome_to_label = {outcome.lower(): label for label, outcomes in label_mapping.items() for outcome in outcomes}
    return outcome_to_label.get(outcome_text.lower(), 'unknown')


def update_unknown_outcomes(df):
    base_url = "https://en.wikinews.org/w/index.php?title="

    for i in df.index:
        if df.at[i, 'outcome'] == 'unknown':
            title = df.at[i, 'title'].replace(" ", "_") 
            url = f"{base_url}{title}&action=edit&redlink=1"
            print(f"Checking page: {url}")

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    page_soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for the specific warning div
                    warning_div = page_soup.find('div', class_='cdx-message cdx-message--block cdx-message--warning mw-warning-with-logexcerpt')
                    if warning_div:
                        df.at[i, 'outcome'] = 'delete'
                    else:
                        df.at[i, 'outcome'] = 'keep'
                else:
                    print(f"Failed to retrieve page: {url}")
            
            except Exception as e:
                print(f"Error accessing {url}: {e}")

    return df

    
def collect_wikinews_deletions(years=None):
    base_url = 'https://en.wikinews.org/wiki/Wikinews:Deletion_requests/Archives'
    response = requests.get(base_url)
    if response.status_code != 200:
        print("Failed to retrieve the archive page.")
        return None
    
    soup = get_soup(base_url)
    titles = []
    text_urls = []
    outcomes = []
    deletion_discussions = []  
    discussion_uncleaned = [] 
    year_links = []
    for a in soup.select('a[href^="/wiki/Wikinews:Deletion_requests/Archives/"]'):
        year_text = re.findall(r'\d{4}', a.get_text()) 
        if year_text:
            year_links.append((year_text[0], a['href']))
    if years:
        if len(years) == 1:
            start_year = end_year = years[0]
        elif len(years) == 2:
            start_year, end_year = min(years), max(years)
        else:
            print("Invalid years input. Provide one or two years.")
            return None
        year_links = [(year, link) for year, link in year_links if start_year <= int(year) <= end_year]
    for year, year_link in year_links:
        year_url = 'https://en.wikinews.org' + year_link
        print(f"Processing year: {year_url}")
        year_soup = get_soup(year_url)
        discussion_divs = year_soup.find_all('div', class_=lambda x: x and 'boilerplate metadata' in x)
        
        for div in discussion_divs:
            title_tag = div.find(['h2', 'h3'])
            if title_tag:
                link_tag = title_tag.find('a', title=True)
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    titles.append(title)
                    text_url = year_url + '#' + link_tag['title'].replace(' ', '_')
                    text_urls.append(text_url)
                else:
                    titles.append(title_tag.get_text(strip=True))
                    text_urls.append(year_url)
            else:
                dl_tag = div.find('dl')
                if dl_tag and dl_tag.find('b'):
                    titles.append(dl_tag.find('b').get_text(strip=True))
                else:
                    titles.append('No title found')
                text_urls.append(year_url)
            deletion_discussions.append(div.prettify())
            discussion_uncleaned.append(div.prettify())
            outcome = extract_outcome_from_div(div)
            outcomes.append(outcome)

    df = pd.DataFrame({
        'title': titles,
        'url': text_urls,
        'outcome': outcomes,
        'discussion': deletion_discussions,
        'discussion_uncleaned': discussion_uncleaned  
    })


    df = process_html_to_plaintext(df)
    for i in df.index:
        if df.at[i,'outcome'] == 'Please do not modify it' or df.at[i,'outcome'] == 'Please do not modify it.':
            df.at[i,'outcome'] = extract_following_sentence(BeautifulSoup(df.at[i,'discussion_uncleaned'], 'html.parser')) or 'unknown'
    df['outcome'] = df['outcome'].apply(lambda x: validate_outcome(x) if x else 'unknown')
    df = update_unknown_outcomes(df)
    return df

def collect_wikinews(years=None):
    df = collect_wikinews_deletions(years=years)
    if df is None:
        print('Error collecting Wikinews deletions.')
        return None
    return df


##################################
## Ttitle based data collection ##
##################################

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
        'merge', 'Merge', 'Not done', 'No consensus', 'no consensus', 'Done'
    ]
    for el in elements:
        b_tags = el.find_all('b')
        for b in b_tags:
            if b.text.strip() in consensus_keywords:
                return b.text.strip()
    return ''

def extract_discussion_section(soup, title):
    """Extracts discussion section, label, and cleaned text."""
    try:
        h3_id = title.replace(" ", "_") 
        h3_tag = soup.find('h3', {'id': h3_id})

        if not h3_tag:
            print(f"h3 tag with id '{h3_id}' not found.")
            return '', '', ''

        heading_div = h3_tag.parent

        if not heading_div:
            print("Parent div not found.")
            return '', '', ''

        next_heading_div = heading_div.find_next_sibling('div', class_='mw-heading mw-heading3')
        discussion_nodes = []
        for sibling in heading_div.next_siblings:
            if sibling == next_heading_div:
                break
            discussion_nodes.append(sibling)

        discussion_tags = []
        for node in discussion_nodes:
            if getattr(node, 'name', None) in ['p', 'ul', 'dl']:
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

    except Exception as e:
        print(f"Error processing title '{title}': {e}")
        import traceback
        traceback.print_exc()  
        return '', '', ''

def extract_div_from_title(title):
    base_url = 'https://en.wikinews.org/wiki/Wikinews:Deletion_requests'
    t = title.replace(' ', '_')
    url = base_url + '#' + t

    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame(columns=['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label'])

    soup = BeautifulSoup(response.content, 'html.parser')
    discussion_html, label, cleaned_discussion = extract_discussion_section(soup, title)
 
    text_url = base_url
    discussion_url = text_url + '#' + title.replace(' ', '_')

    df = pd.DataFrame([[title, text_url, discussion_url, cleaned_discussion, label]],
                      columns=['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label'])

    if label:
        df['label'] = df['label'].replace({
            'Deleted':'delete', 'Delete':'delete', 'delete':'delete', 'deleted':'delete', 
            'kept':'keep', 'keep':'keep', 'Keep':'keep', 'Kept':'keep', 
            'merge':'merge', 'Merge':'merge', 'Not done':'no_consensus', 
            'No consensus':'no_consensus', 'no consensus':'no_consensus', 'Done':'delete'
        })

    df['discussion_cleaned'] = df['discussion_cleaned'].apply(split_text_into_sentences)
    df = df.rename(columns={'discussion_cleaned':'discussion'})
    return df

########################
## Umbrella function  ##
########################

def collect_wikinews(mode, title=None, url ='', year=None):

    if mode == 'title':
        if not title:
            raise ValueError("Title is required for 'title' mode.")
        return extract_div_from_title(title)
    
    elif mode == 'url':
        if 'Archives' in url.split('/')[-2]:
            year = int(url.split('/')[-1].split('#')[0])
            print(f"Year extracted from URL: {year}")
            df = collect_wikinews_deletions(years=[year])
            #keep the row with the title only
            df = df[df['title'] == url.split('#')[-1].replace('_', ' ')]
            if df.empty:
                return pd.DataFrame(columns=['title', 'text_url', 'discussion_url', 'discussion_cleaned', 'label'])
            df = df[['title','url','discussion_cleaned','outcome']]
            df = df.rename(columns={'discussion_cleaned':'discussion'})   
            return df

        if not url:
            raise ValueError("URL is required for 'url' mode.")
        
        title = url.split('#')[-1].replace('_', ' ')
        print(f"Title extracted from URL: {title}")
        return extract_div_from_title(title)

    elif mode == 'year':
        if not year:
            raise ValueError("Year or year range is required for 'year' mode.")
        return collect_wikinews_deletions(years=year)

    else:
        raise ValueError("Invalid mode. Please specify 'title' or 'year' or 'url'.")

# year_df = collect_wikinews(mode='year', year=[2023]) 
# title_df = collect_wikinews(mode='title', title="NurMi spam") 

# print(year_df)
# print(title_df)
