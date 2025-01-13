
# from transformers import pipeline, AutoTokenizer
# from wide_analysis.data.process_data import prepare_dataset
# from wide_analysis.data_collect import collect
# from wide_analysis.utils.helper import send_to_openai
# import pandas as pd
# import torch

from transformers import pipeline, AutoTokenizer
from wide_analysis.data import process_data
from wide_analysis import data_collect
from wide_analysis.utils import helper
import pandas as pd
import torch


best_models_tasks = {
    'wikipedia': 'research-dump/roberta-large_deletion_multiclass_complete_final_v2',
    'wikidata_entity': 'research-dump/roberta-large_wikidata_ent_outcome_prediction_v1',
    'wikidata_property': 'research-dump/roberta-large_wikidata_prop_outcome_prediction_v1',
    'wikinews': 'research-dump/all-roberta-large-v1_wikinews_outcome_prediction_v1',
    'wikiquote': 'research-dump/roberta-large_wikiquote_outcome_prediction_v1'
}

best_models_langs = {
    'en': 'research-dump/roberta-large_deletion_multiclass_complete_final_v2',
    'es': 'research-dump/xlm-roberta-large_deletion_multiclass_es',
    'gr': 'research-dump/xlm-roberta-large_deletion_multiclass_gr'
}

label_mapping_wikipedia_en = {
    'delete': [0, 'LABEL_0'],
    'keep': [1, 'LABEL_1'],
    'merge': [2, 'LABEL_2'],
    'no consensus': [3, 'LABEL_3'],
    'speedy keep': [4, 'LABEL_4'],
    'speedy delete': [5, 'LABEL_5'],
    'redirect': [6, 'LABEL_6'],
    'withdrawn': [7, 'LABEL_7']
}

label_mapping_wikidata_ent = {
    'delete': [0, 'LABEL_0'],
    'no_consensus': [1, 'LABEL_1'],
    'merge': [2, 'LABEL_2'],
    'keep': [3, 'LABEL_3'],
    'comment': [4, 'LABEL_4'],
    'redirect': [5, 'LABEL_5']
}

label_mapping_wikidata_prop = {
    'deleted': [0, 'LABEL_0'],
    'keep': [1, 'LABEL_1'],
    'no_consensus': [2, 'LABEL_2']
}

label_mapping_wikinews = {
    'delete': [0, 'LABEL_0'],
    'no_consensus': [1, 'LABEL_1'],
    'speedy delete': [2, 'LABEL_2'],
    'keep': [3, 'LABEL_3'],
    'redirect': [4, 'LABEL_4'],
    'comment': [5, 'LABEL_5'],
    'merge': [6, 'LABEL_6'],
    'withdrawn': [7, 'LABEL_7']
}

label_mapping_wikiquote = {
    'merge': [0, 'LABEL_0'],
    'keep': [1, 'LABEL_1'],
    'no_consensus': [2, 'LABEL_2'],
    'redirect': [3, 'LABEL_3'],
    'delete': [4, 'LABEL_4']
}

label_mapping_es = {
    'Borrar': [0, 'LABEL_0'],
    'Mantener': [1, 'LABEL_1'],
    'Fusionar': [2, 'LABEL_2'],
    'Otros': [3, 'LABEL_3']
}

label_mapping_gr = {
    'Διαγραφή': [0, 'LABEL_0'],
    'Δεν υπάρχει συναίνεση': [1, 'LABEL_1'],
    'Διατήρηση': [2, 'LABEL_2'],
    'συγχώνευση': [3, 'LABEL_3']
}

def get_outcome(input_text_or_url, mode='url', openai_access_token=None, explanation=False, lang='en', platform='wikipedia', explainer_model='gpt-4o-mini', date='', years=None, model = ''):
    if lang == 'en':
        if platform not in best_models_tasks:
            raise ValueError(f"For lang='en', platform must be one of {list(best_models_tasks.keys())}")
        model_name = best_models_tasks[platform]
        if platform == 'wikipedia':
            label_mapping = label_mapping_wikipedia_en
        elif platform == 'wikidata_entity':
            label_mapping = label_mapping_wikidata_ent
        elif platform == 'wikidata_property':
            label_mapping = label_mapping_wikidata_prop
        elif platform == 'wikinews':
            label_mapping = label_mapping_wikinews
        elif platform == 'wikiquote':
            label_mapping = label_mapping_wikiquote
    elif lang in ['es', 'gr']:
        if platform != 'wikipedia':
            raise ValueError(f"For lang='{lang}', only platform='wikipedia' is supported.")
        model_name = model if model!= '' else best_models_langs[lang]
        label_mapping = label_mapping_es if lang == 'es' else label_mapping_gr
    else:
        raise ValueError("Invalid lang. Use 'en', 'es', or 'gr'.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = pipeline("text-classification", model=model_name, top_k=None, device=device, max_length=512, truncation=True)

    if mode == 'url':
        derived_date = input_text_or_url.split('/')[-1].split('#')[0]
        title = input_text_or_url.split('#')[-1]

        used_date = date if date else derived_date
        if lang == 'en' and platform == 'wikipedia':
            df = process_data.prepare_dataset('title', start_date=used_date, url=input_text_or_url, title=title)
        else:
            df = data_collect.collect(
                mode='title' if lang == 'gr' else 'url', 
                start_date=used_date, 
                url=input_text_or_url, 
                title=title, 
                platform=platform, 
                lang=lang,
                # date=used_date,
                # years=years 
            )

        if isinstance(df, str):
            raise ValueError("No data returned from collect function.")

        if df.empty:
            raise ValueError("No discussion data found for the given URL.")

        text = df['discussion'].iloc[0]
    else:
        text = input_text_or_url
        title = text.split('#')[-1] if '#' in text else 'Unknown'

    tokens = tokenizer(text, truncation=True, max_length=512)
    truncated_text = tokenizer.decode(tokens['input_ids'], skip_special_tokens=True)
    results = model(truncated_text)

    final_scores = {key: 0.0 for key in label_mapping.keys()}
    for result in results[0]:
        for key, value in label_mapping.items():
            if result['label'] == value[1]:
                final_scores[key] = result['score']
                break

    chosen_label = max(final_scores, key=final_scores.get)
    response = {'title': title, 'outcome': chosen_label, 'score': final_scores[chosen_label]}

    if explanation:
        try:
            expl = helper.send_to_openai(title = title, 
                                         engine = explainer_model, 
                                         label = chosen_label, 
                                         text = text, 
                                         openai_key=openai_access_token
                                        )
            response['explanation'] = expl
        except Exception as e:
            if not openai_access_token:
                print('Please provide an OpenAI access token to get an explanation')
            else:
                print(f"An error occurred while trying to get an explanation: {e}")

    return response














