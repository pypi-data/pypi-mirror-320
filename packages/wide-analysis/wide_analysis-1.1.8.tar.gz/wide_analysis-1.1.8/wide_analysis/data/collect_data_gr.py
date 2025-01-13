import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import pysbd

###############################################
# Functions from Code 1 (collapsible approach)#
###############################################

def extract_result(sentence):
    match = re.search(r"(Διαγραφή|Παραμονή|Άλλο αποτέλεσμα|διαγραφή|Συγχώνευση|Διατήρηση)", sentence, flags=re.IGNORECASE)
    delete_cases = [
        'Μη εγκυκλοπαιδικό', 'Πράγματι δεν φαίνεται πως το λήμμα είναι εγκυκλοπαιδικό',
        'Δεν διαπιστώθηκε εγκυκλοπαιδικότητα', 'Μη εγκυκλοπαιδικό λήμμα',
        'Το λήμμα κρίθηκε ότι είναι καταλληλότερο για κάποιο άλλο αδελφό εγχείρημα, παρά για την Βικιπαίδεια + ατεκμηρίωτο.',
        'Δεν υπάρχουν επαρκείς αναφορές για την βιογραφούμενη'
    ]
    if match:
        outcome = match.group(1).strip()
    elif sentence in delete_cases:
        outcome = 'Διαγραφή'
    else:
        outcome = 'Δεν υπάρχει συναίνεση'
    return normalize_outcome(outcome)

def normalize_outcome(o):
    lowered = o.lower()
    if 'διαγρ' in lowered:  # covers 'διαγραφή'
        return 'Διαγραφή'
    elif 'διατήρη' in lowered or 'παραμονή' in lowered:
        return 'Διατήρηση'
    elif 'συγχών' in lowered:
        return 'συγχώνευση'
    else:
        # Covers 'Άλλο αποτέλεσμα' and unknown cases
        return 'Δεν υπάρχει συναίνεση'

def extract_discussions_from_page_collapsible(url):
    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame(columns=['title', 'discussion', 'result_sentence', 'result', 'text_url'])

    soup = BeautifulSoup(response.content, 'html.parser')
    discussion_sections = soup.find_all('div', class_='mw-heading mw-heading2 ext-discussiontools-init-section')
    titles = []
    for section in discussion_sections:
        try:
            h2_tag = section.find('h2')
            if not h2_tag:
                continue
            title_link = h2_tag.find('a')
            title = title_link.text.strip() if title_link else h2_tag.get_text(strip=True)
            titles.append(title)
        except:
            pass

    discussion_tables = soup.find_all('table')
    if not discussion_tables:
        return pd.DataFrame(columns=['title', 'discussion', 'result_sentence', 'result', 'text_url'])

    data = []
    for idx, table in enumerate(discussion_tables):
        try:
            decision_row = table.find('tr')
            decision_cell = decision_row.find('th') if decision_row else None
            if decision_cell:
                result_match = re.search(
                    r"Η συζήτηση τελείωσε, το αποτέλεσμα ήταν: <i>(.*?)</i>", str(decision_cell), re.DOTALL
                )
                result_sentence = result_match.group(1).strip() if result_match else "No result found"
            else:
                result_sentence = "No result found"

            discussion_row = decision_row.find_next_sibling('tr') if decision_row else None
            discussion_cell = discussion_row.find('td', class_='plainlinks') if discussion_row else None
            discussion_content = discussion_cell.get_text(separator="\n") if discussion_cell else "No discussion content found"
            discussion_content = discussion_content.split('\nμητρώο\n)\n\n\n\n\n')[-1].replace('\n','')

            title = titles[idx] if idx < len(titles) else f"Discussion {idx + 1}"
            data.append({
                "title": title,
                "discussion": discussion_content,
                "result_sentence": result_sentence,
                "result": extract_result(result_sentence),
                "text_url": url
            })
        except:
            pass

    return pd.DataFrame(data, columns=['title', 'discussion', 'result_sentence', 'result', 'text_url'])

###########################################
# Functions from Code 2 (non-collapsible) #
###########################################

def extract_discussions_from_page_non_collapsible(url):
    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame(columns=['title', 'discussion', 'result_sentence', 'result', 'text_url'])

    soup = BeautifulSoup(response.content, 'html.parser')
    discussion_sections = soup.find_all('div', class_='mw-heading mw-heading2 ext-discussiontools-init-section')
    titles = []
    for section in discussion_sections:
        try:
            h2_tag = section.find('h2')
            if not h2_tag:
                continue
            title_link = h2_tag.find('a')
            title = title_link.text.strip() if title_link else h2_tag.get_text(strip=True)
            titles.append(title)
        except:
            pass

    discussion_tables = soup.find_all('table', class_='pagediscussion')
    if not discussion_tables:
        return pd.DataFrame(columns=['title', 'discussion', 'result_sentence', 'result', 'text_url'])

    data = []
    for idx, table in enumerate(discussion_tables):
        try:
            decision_row = table.find('tr')
            decision_cell = decision_row.find('th') if decision_row else None
            if decision_cell:
                result_match = re.search(
                    r"Η συζήτηση τελείωσε, το αποτέλεσμα ήταν: <i>(.*?)</i>", str(decision_cell), re.DOTALL
                )
                result_sentence = result_match.group(1).strip() if result_match else "No result found"
            else:
                result_sentence = "No result found"

            discussion_row = decision_row.find_next_sibling('tr') if decision_row else None
            discussion_cell = discussion_row.find('td', class_='plainlinks') if discussion_row else None
            discussion_content = discussion_cell.get_text(separator="\n") if discussion_cell else "No discussion content found"
            discussion_content = discussion_content.split('\nμητρώο\n)\n\n\n\n\n')[-1].replace('\n','')

            title = titles[idx] if idx < len(titles) else f"Discussion {idx + 1}"
            data.append({
                "title": title,
                "discussion": discussion_content,
                "result_sentence": result_sentence,
                "result": extract_result(result_sentence),
                "text_url": url
            })
        except:
            pass

    return pd.DataFrame(data, columns=['title', 'discussion', 'result_sentence', 'result', 'text_url'])

###########################################
# Title-based extraction with fallback    #
###########################################

def html_to_plaintext(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all(['p', 'li', 'dd', 'dl', 'ul']):
        tag.insert_before('\n')
        tag.insert_after('\n')
    for br in soup.find_all('br'):
        br.replace_with('\n')
    text = soup.get_text(separator=' ', strip=True)
    text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
    return text

def split_text_into_sentences(text):
    seg = pysbd.Segmenter(language="el", clean=False)
    sentences = seg.segment(text)
    return ' '.join(sentences)

def clean_discussion_text(text):
    return text.strip()

def extract_outcome_from_text(text):
    outcomes = ['Διαγραφή', 'Παραμονή', 'διαγραφή', 'Συγχώνευση', 'Διατήρηση', 'Άλλο αποτέλεσμα']
    lowered = text.lower()
    found_outcome = None
    for outcome in outcomes:
        if outcome.lower() in lowered:
            found_outcome = outcome
            break
    if not found_outcome:
        found_outcome = 'Δεν υπάρχει συναίνεση'
    return normalize_outcome(found_outcome)

def extract_discussion_section(soup, title):
    t = title.replace(' ', '_')
    h2_tag = soup.find('h2', id=t)
    if not h2_tag:
        return '', '', ''

    heading_div = h2_tag.find_parent('div', class_='mw-heading mw-heading2 ext-discussiontools-init-section')
    if not heading_div:
        return '', '', ''

    next_heading_div = heading_div.find_next('div', class_='mw-heading mw-heading2 ext-discussiontools-init-section')

    html_fragments = []
    current = heading_div.next_sibling
    while current and current != next_heading_div:
        if hasattr(current, 'prettify'):
            html_fragments.append(current.prettify())
        else:
            html_fragments.append(str(current))
        current = current.next_sibling

    discussion_html = ''.join(html_fragments).strip()
    if not discussion_html:
        return '', '', ''

    sub_soup = BeautifulSoup(discussion_html, 'html.parser')
    discussion_tags = sub_soup.find_all(['p', 'ul', 'dl'])

    if not discussion_tags:
        return '', '', ''

    cleaned_parts = []
    for tag in discussion_tags:
        for unwanted in tag.find_all(['span', 'img', 'a', 'div', 'table'], recursive=True):
            unwanted.decompose()
        text = tag.get_text(separator=' ', strip=True)
        if text:
            cleaned_parts.append(text)

    cleaned_discussion = ' '.join(cleaned_parts)
    label = extract_outcome_from_text(cleaned_discussion)

    return discussion_html, label, cleaned_discussion

def extract_fallback_discussion(url, title):
    response = requests.get(url)
    if response.status_code != 200:
        return '', None

    soup = BeautifulSoup(response.text, 'html.parser')
    discussion_tables = soup.find_all('table')
    if not discussion_tables:
        return '', None
    for table in discussion_tables:
        table_text = table.get_text(separator='\n', strip=True)
        if title in table_text:
            decision_row = table.find('tr')
            decision_cell = decision_row.find('th') if decision_row else None
            if decision_cell:
                result_match = re.search(r"Η συζήτηση τελείωσε, το αποτέλεσμα ήταν: <i>(.*?)</i>", str(decision_cell), re.DOTALL)
                result_sentence = result_match.group(1).strip() if result_match else "No result found"
            else:
                result_sentence = "No result found"

            discussion_row = decision_row.find_next_sibling('tr') if decision_row else None
            discussion_cell = discussion_row.find('td', class_='plainlinks') if discussion_row else None
            discussion_content = ''
            if discussion_cell:
                discussion_content = discussion_cell.get_text(separator=' ', strip=True)

            if discussion_content:
                outcome = extract_result(result_sentence)
                return discussion_content, outcome

    return '', None

def extract_div_from_title_with_fallback(title, url ='', date=''):
    if not date:
        raise ValueError("For 'title' mode, 'date' must be provided in the format: mm/yyyy")

    month_map = {
        '01': 'Ιανουαρίου', '02': 'Φεβρουαρίου', '03': 'Μαρτίου', '04': 'Απριλίου', '05': 'Μαΐου', '06': 'Ιουνίου',
        '07': 'Ιουλίου', '08': 'Αυγούστου', '09': 'Σεπτεμβρίου', '10': 'Οκτωβρίου', '11': 'Νοεμβρίου', '12': 'Δεκεμβρίου'
    }
    if '_' in date and date.split('_')[0] in month_map.values():
        # If date is already in 'Month_Year' format
        date_str = date
    else:
        # Try to parse date in 'mm/yyyy' format
        match = re.match(r'(\d{2})/(\d{4})', date)
        if not match:
            raise ValueError("Date must be in the format mm/yyyy or Month_Year")
        mm, yyyy = match.groups()
        if mm not in month_map:
            raise ValueError(f"Invalid month: {mm}")
        
        date_str = f"{month_map[mm]}_{yyyy}"  # Convert to 'Month_Year' format
    base_url = 'https://el.wikipedia.org/wiki/Βικιπαίδεια:Σελίδες_για_διαγραφή'
    url = f"{base_url}/{date_str}#{title}"

    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame(columns=['title', 'discussion_url', 'discussion', 'outcome'])

    soup = BeautifulSoup(response.content, 'html.parser')
    discussion_html, label, cleaned_discussion = extract_discussion_section(soup, title)

    text_url = f"{base_url}/{date_str}"
    discussion_url = text_url + '#' + title

    cleaned_discussion = html_to_plaintext(cleaned_discussion)
    cleaned_discussion = split_text_into_sentences(cleaned_discussion)
    cleaned_discussion = clean_discussion_text(cleaned_discussion)

    if not cleaned_discussion.strip():
        fallback_url = f"{base_url}/{date_str}"
        discussion_content, outcome = extract_fallback_discussion(fallback_url, title)
        cleaned_discussion = html_to_plaintext(discussion_content)
        cleaned_discussion = split_text_into_sentences(cleaned_discussion)
        cleaned_discussion = clean_discussion_text(cleaned_discussion)
        if outcome:
            label = normalize_outcome(outcome)

    df = pd.DataFrame([[title, discussion_url, cleaned_discussion, label]],
                      columns=['title', 'discussion_url', 'discussion', 'outcome'])
    return df

def normalize_outcome(o):
    lowered = o.lower()
    if 'διαγρ' in lowered:
        return 'Διαγραφή'
    elif 'διατήρη' in lowered or 'παραμονή' in lowered:
        return 'Διατήρηση'
    elif 'συγχών' in lowered:
        return 'συγχώνευση'
    else:
        return 'Δεν υπάρχει συναίνεση'

###################################
# The collect_gr() function       #
###################################

def collect_gr(mode='url', title='', url = '', years=[]):
    if mode not in ['title', 'year', 'url']:
        raise ValueError("mode must be either 'title' or 'year' or 'url'.")
    #title = url.split('#')[-1] if mode == 'url' else title
    if mode == 'title':
        if not title or not years or len(years) != 1:
            raise ValueError("For 'title' mode, 'title' must be provided and 'years' must be a single-element list like ['mm/yyyy'].")
        date = years[0]
        df = extract_div_from_title_with_fallback(title, date=date)
        return df[['title', 'discussion_url', 'discussion', 'outcome']]
    
    elif mode == 'url':
        if title or years:
            raise ValueError("For 'url' mode, 'title' must be empty and 'years' must be empty.")
        #collect the title and date from the url like: base_url = 'https://el.wikipedia.org/wiki/Βικιπαίδεια:Σελίδες_για_διαγραφή'/{date_str}#{title}
        match = re.search(r'Βικιπαίδεια:Σελίδες_για_διαγραφή/([^#]+)#(.+)', url)
        if not match:
            raise ValueError("URL format is incorrect.")
        date_str, title = match.groups()
        print(date_str, title)
        df = extract_div_from_title_with_fallback(title, date=date_str)
        return df[['title', 'discussion_url', 'discussion', 'outcome']]


    elif mode == 'year':
        if title or not years:
            raise ValueError("For 'year' mode, 'title' must be empty and 'years' must be provided.")
        if len(years) == 1:
            start_year = end_year = years[0]
        elif len(years) == 2:
            start_year, end_year = min(years), max(years)
        else:
            raise ValueError("Invalid years input. Provide one year or two years for a range.")

        all_data = []
        for year in range(start_year, end_year + 1):
            url = f"https://el.wikipedia.org/wiki/Βικιπαίδεια:Σελίδες_για_διαγραφή/Ιανουαρίου_{year}"
            df = extract_discussions_from_page_collapsible(url)
            if df.empty:
                df = extract_discussions_from_page_non_collapsible(url)

            if not df.empty:
                df['result'] = df['result'].apply(normalize_outcome)
                df['discussion_url'] = df.apply(lambda row: row['text_url'] + '#' + row['title'].replace(' ', '_'), axis=1)
                df = df.rename(columns={'result':'outcome'})
                all_data.append(df[['title', 'discussion_url', 'discussion', 'outcome']])

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame(columns=['title', 'discussion_url', 'discussion', 'outcome'])
