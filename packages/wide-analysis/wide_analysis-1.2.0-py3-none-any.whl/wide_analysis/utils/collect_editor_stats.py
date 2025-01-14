
import pandas as pd
import re
from wide_analysis import data_collect 

def extract_title(text):
    if ':' in text:
        title, new_text = text.split(':', 1)
        return title.strip(), new_text.strip()
    return None, text

def extract_usernames(text):
    timestamp_regex = r'\d{2}:\d{2}, \d{1,2} \w+ \d{4} \(UTC\) \[ reply \]'
    sentences = re.split(r'\.\s*', text)
    usernames = []
    for sentence in sentences:
        if re.search(timestamp_regex, sentence):
            part_before_timestamp = re.split(timestamp_regex, sentence)[0]
            potential_usernames = [name.strip() for name in part_before_timestamp.split(',')]
            if potential_usernames:
                usernames.append(potential_usernames[-1])

    cleaned_usernames = [
        re.sub(r'[^\w\s:]', '', username).strip() for username in usernames
    ]

    cleaned_usernames = list(dict.fromkeys(cleaned_usernames))
    cleaned_usernames = [re.sub(r'\s*talk\s*', '', username).strip() for username in cleaned_usernames]

    return cleaned_usernames

def fetch_user_stats(username):
    formatted_username = username.replace(" ", "_")
    url = f"https://xtools.wmcloud.org/api/user/edit_summaries/en.wikipedia.org/{formatted_username}"

    headers = {
        'User-Agent': 'WiDe-analysis/1.0 (your_email@example.com)'
    }

    try:
        import requests
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {username: f"User stats not found (status code {response.status_code})"}

        data = response.json()

        stats = {
            'Total edits': data.get('total_edits', 'Not available'),
            'Total summaries': data.get('total_summaries', 'Not available'),
            'Recent edits minor': data.get('recent_edits_minor', 'Not available'),
            'Recent edits major': data.get('recent_edits_major', 'Not available'),
            'Total edits minor': data.get('total_edits_minor', 'Not available'),
            'Total edits major': data.get('total_edits_major', 'Not available'),
            'Recent summaries minor': data.get('recent_summaries_minor', 'Not available'),
            'Recent summaries major': data.get('recent_summaries_major', 'Not available'),
            'Total summaries minor': data.get('total_summaries_minor', 'Not available'),
            'Total summaries major': data.get('total_summaries_major', 'Not available'),
        }

        return {username: stats}

    except Exception as e:
        return {username: f"Error fetching data: {str(e)}"}

def collect_user_stats(usernames):
    if not usernames:
        return [{"No username": "No user statistics found"}]
    return [fetch_user_stats(username) for username in usernames]

def collect_editor_info(url, lang, title=None, date=None, platform="wikipedia"):
    try:
        df = data_collect.collect(mode='url', url=url, platform=platform, lang=lang, start_date=date)
        if df is None or df.empty:
            return {"error": "No discussion data found for the given URL."}
    except Exception as e:
        return {"error": f"Failed to fetch the discussion data: {str(e)}"}
    discussion_text = df['discussion'].iloc[0]

    extracted_title, remaining_text = extract_title(discussion_text)
    usernames = extract_usernames(remaining_text)
    user_stats = collect_user_stats(usernames)

    editor_data = {
        "Title": title or extracted_title,
        "Platform": platform,
        "Language": lang,
        "Date": date,
        "URL": url,
        "User Statistics": user_stats
    }

    return editor_data


def collect(mode, start_date=None, end_date=None, url=None, title=None, output_path=None,
            platform=None, lang=None, task=None):
    if mode == "editor_extraction":
        editor_info = collect_editor_info(url, lang, title, date=start_date, platform=platform)

        if output_path:
            pd.DataFrame(editor_info["User Statistics"]).to_csv(output_path, index=False)

        return editor_info

    return {"error": "Unsupported mode"}



