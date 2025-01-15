import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

#################### Spanish Wikipedia ####################

###############
# Title based #
###############

def extract_result_resultado(sentence):
    match = re.search(r"(RESULTADO:|El resultado fue)\s*(\w+)", sentence, flags=re.IGNORECASE)
    return match.group(2).strip() if match else None

def extract_result(sentence):
    #print(f"Extracting result from sentence: {sentence}")  
    match = re.search(r"se\s+decidió\s+(\w+)", sentence, flags=re.IGNORECASE)
    if match:
        #print(f"Match found for 'se decidió': {match.groups()}")  
        return match.group(1).strip()
    #print("No match found for 'se decidió'.") 
    return None

def clean_comments_with_no_text_after_timestamp(content_div):
    for ol in content_div.find_all('ol'): 
        for li in ol.find_all('li'):  
            li_text = li.get_text(strip=True)
            if "(CEST)" in li_text or "(CET)" in li_text:
                match = re.search(r"\(C[ES]T\)\s*(.*)", li_text)
                if match:
                    after_timestamp = match.group(1).strip()
                    if not after_timestamp:  
                        li.decompose()
            else:
                li.decompose()
    return content_div

def extract_cleaned_spanish_discussion_and_result(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for URL: {url}")
        return pd.DataFrame(columns=['title', 'discussion_uncleaned', 'discussion', 'result_sentence', 'result', 'text_url', 'discussion_url'])

    soup = BeautifulSoup(response.content, 'html.parser')
    title = url.split('/')[-1].replace('_', ' ').replace(':', '')
    text_url = f"https://es.wikipedia.org/wiki/{url.split('/')[-1]}"
    discussion_url = url

    content_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
    if not content_div:
        print("Error: Main discussion container not found")
        return pd.DataFrame(columns=['title', 'discussion_uncleaned', 'discussion', 'result_sentence', 'result', 'text_url', 'discussion_url'])

    discussion_uncleaned = content_div.prettify()
    discussion = ''
    result_sentence = ''
    result = None

    try:
        result_p = next(
            (p for p in content_div.find_all('p') if "El resultado fue" in p.get_text() or "RESULTADO:" in p.get_text()), None
        )

        if result_p:
            result_sentence = result_p.get_text(strip=True)
            bold_tag = result_p.find('b')
            if bold_tag:
                result = bold_tag.get_text(strip=True)
            else:
                match = re.search(r"(El resultado fue|RESULTADO:)\s*(.+?)\.", result_sentence, flags=re.IGNORECASE)
                result = match.group(2).strip() if match else None
                #print(f"Extracted result from sentence: {result}")

        content_div = clean_comments_with_no_text_after_timestamp(content_div)
        discussion_text_parts = content_div.find_all(recursive=False)
        cleaned_text_parts = []
        for part in discussion_text_parts:
            cleaned_text_parts.append(part.get_text(strip=True))
        discussion = "\n".join(cleaned_text_parts)

        if not result:
            result_div = content_div.find('div', class_='messagebox')
            if result_div:
                result_dl = result_div.find('dl')
                if result_dl:
                    result_sentence = result_dl.get_text(strip=True)
                    #print(f"Extracted result sentence from messagebox: {result_sentence}")  
                    result = extract_result(result_sentence)
            if not result and not result_sentence:
                    result_p = next((p for p in content_div.find_all('p') if "RESULTADO:" in p.get_text() or "se decidió" in p.get_text()), None)
                    if result_p:
                        result_sentence = result_p.get_text(strip=True)
                        #print(f"Extracted result sentence from paragraph: {result_sentence}")  
                        result = extract_result(result_sentence)

            if not result and not result_sentence:
                    voting_sentence = next((p for p in content_div.find_all('p') if "se decidió" in p.get_text()), None)
                    if voting_sentence:
                        result_sentence = voting_sentence.get_text(strip=True)
                        #print(f"Extracted voting sentence: {result_sentence}")  
                        result = extract_result(result_sentence)

        # if result:
        #     print(f"Final extracted result: {result}")  

        if "Votación" in discussion:
            discussion = discussion.split("Votación", 1)[1].strip()

    except Exception as e:
        print(f"Error processing discussion: {e}")
    data = [[title, discussion_uncleaned, discussion, result_sentence, result, text_url, discussion_url]]
    df = pd.DataFrame(data, columns=['title', 'discussion_uncleaned', 'discussion', 'result_sentence', 'result', 'text_url', 'discussion_url'])
    df['result'] = df['result'].apply(lambda x: extract_result_resultado(x) if isinstance(x, str) and len(x.split()) > 1 else x)
    return df

# url = 'https://es.wikipedia.org/wiki/Wikipedia:Consultas_de_borrado/!Hispahack' #'https://es.wikipedia.org/wiki/Wikipedia:Consultas_de_borrado/:Country_Club_La_Planicie'
# df = extract_cleaned_spanish_discussion_and_result(url)
# df

###############
# Date based #
###############


def extract_result(sentence):
    match = re.search(r"(El resultado fue|RESULTADO:)\s*(\w+)", sentence, flags=re.IGNORECASE)
    return match.group(2).strip() if match else None

def extract_multiple_discussions(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for URL: {url}")
        return pd.DataFrame(columns=['title', 'discussion_uncleaned', 'discussion', 'result_sentence', 'result', 'text_url', 'discussion_url'])

    soup = BeautifulSoup(response.content, 'html.parser')
    content_div = soup.find('div', class_='mw-content-ltr mw-parser-output')
    if not content_div:
        print("Error: Main discussion container not found")
        return pd.DataFrame(columns=['title', 'discussion_uncleaned', 'discussion', 'result_sentence', 'result', 'text_url', 'discussion_url'])
    data = []
    headings = content_div.find_all('div', class_='mw-heading mw-heading3')
    for idx, heading in enumerate(headings):
        try:
            title_tag = heading.find('a', class_='new') or heading.find('a')
            if title_tag:
                title = title_tag.text.strip()
                text_url = f"https://es.wikipedia.org{title_tag['href']}"
            else:
                title = f"{url.split('/')[-1]}_{idx + 1}"
                text_url = f"https://es.wikipedia.org/wiki/{title}"
            previous_sibling = heading.find_previous_sibling()
            result_sentence = None
            result = None
            while previous_sibling:
                if previous_sibling.name == 'p' and "El resultado fue" in previous_sibling.get_text():
                    normalized_text = previous_sibling.get_text(separator=" ", strip=True)
                    result_sentence = normalized_text
                    result = extract_result(result_sentence)
                    break
                previous_sibling = previous_sibling.find_previous_sibling()
            if not result_sentence:
                result_p = content_div.find('p', string=lambda text: text and "RESULTADO:" in text)
                if result_p:
                    result_sentence = result_p.get_text(strip=True)
                    result = extract_result(result_sentence)
            discussion_html = ""
            current = heading.find_next_sibling()
            while current and not (current.name == 'div' and 'mw-heading mw-heading3' in current.get('class', [])):
                discussion_html += str(current)
                current = current.find_next_sibling()

            discussion_uncleaned = discussion_html
            discussion = BeautifulSoup(discussion_html, 'html.parser').get_text(strip=True)
            data.append([title, discussion_uncleaned, discussion, result_sentence, result, text_url, url])
        except Exception as e:
            print(f"Error processing heading: {e}")
    df = pd.DataFrame(data, columns=['title', 'discussion_uncleaned', 'discussion', 'result_sentence', 'result', 'text_url', 'discussion_url'])
    return df

# url = 'https://es.wikipedia.org/wiki/Wikipedia:Consultas_de_borrado/Registro/10_de_septiembre_de_2009'
# df = extract_multiple_discussions(url)
# df

###############
# Collect ES #
###############

def collect_es(mode='title', title='', url = '',date=''):
    if mode not in ['title', 'year', 'url']:
        raise ValueError("mode must be either 'title' or 'year'")

    if mode == 'title':
        if not title or date:
            raise ValueError("For 'title' mode, 'title' must be provided and 'date' must be empty.")
        url = f"https://es.wikipedia.org/wiki/Wikipedia:Consultas_de_borrado/{title}"
        df = extract_cleaned_spanish_discussion_and_result(url)
        if df.empty:
            print(f"No data found for url: {url}")
        return df
    elif mode == 'url':
        if title or date:
            raise ValueError("For 'url' mode, 'url' must be provided and 'title' must be empty.")
        df = extract_cleaned_spanish_discussion_and_result(url)
        return df

    elif mode == 'year':
        if title or not date:
            raise ValueError("For 'year' mode, 'date' must be provided and 'title' must be empty.")
        month_map = {
            '01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril', '05': 'mayo', '06': 'junio',
            '07': 'julio', '08': 'agosto', '09': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'
        }

        match = re.match(r'(\d{2})/(\d{2})/(\d{4})', date)
        if not match:
            raise ValueError("Date must be in the format dd/mm/yyyy")

        day, month, year = match.groups()
        if month not in month_map:
            raise ValueError("Invalid month in date")

        date_str = f"{int(day)}_de_{month_map[month]}_de_{year}"
        url = f"https://es.wikipedia.org/wiki/Wikipedia:Consultas_de_borrado/Registro/{date_str}"
        df = extract_multiple_discussions(url)
        return df
