from transformers import pipeline, AutoTokenizer
from wide_analysis.data import process_data #import prepare_dataset
from wide_analysis.data.collect_data_wikinews import collect_wikinews
from wide_analysis.data.collect_data_wikiquote import collect_wikiquote
from wide_analysis.data.collect_data_wikidata_ent import collect_wikidata_entity
from wide_analysis.data.collect_data_wikidata_prop import collect_wikidata 
import pandas as pd
import pysbd
import torch

def extract_response(text, model_name, access_token):
    label_mapping = {
            'delete': 0,
            'keep': 1,
            'merge': 2,
            'comment': 3
        }
    if access_token is None:
        raise ValueError("Please provide a valid access token")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    pipe = pipeline("text-classification", model=model_name, tokenizer=tokenizer, top_k=None,device= device,max_length = 512,truncation=True)
    
    # Tokenize and truncate the text
    tokens = tokenizer(text, truncation=True, max_length=512)
    truncated_text = tokenizer.decode(tokens['input_ids'], skip_special_tokens=True)
    
    results = pipe(truncated_text)
    
    final_scores = {key: 0.0 for key in label_mapping}
    for result in results[0]:
        for key, value in label_mapping.items():
            if result['label'] == f'LABEL_{value}':
                final_scores[key] = result['score']
                break
    
    return final_scores

def get_stance(url,mode='url', access_token='',platform='wikipedia', model_name=''):
    if mode == 'url':
        if platform == 'wikipedia':
            date = url.split('/')[-1].split('#')[0]
            title = url.split('#')[-1]
            df = process_data.prepare_dataset('title', start_date=date,url=url, title=title)
            text = df['discussion'].iloc[0]
        elif platform == 'wikinews':
            df = collect_wikinews(url=url, mode='url')
            text = df['discussion'].iloc[0]
        elif platform == 'wikiquotes':
            df = collect_wikiquote(url=url, mode='url')
            text = df['discussion'].iloc[0]
        elif platform == 'wikidata_entity':
            df = collect_wikidata_entity(url=url, mode='url')
            text = df['discussion'].iloc[0]
        elif platform == 'wikidata_property':
            df =  collect_wikidata(url =url, mode='url')
            text = df['discussion'].iloc[0]
    else:
        text = url
    if type(text)== list:
        text_list = text
    else:
        seg = pysbd.Segmenter(language="en", clean=False)
        text_list = seg.segment(text)
    model = model_name if model_name != '' else 'research-dump/bert-large-uncased_wikistance_v1'
    res_list = []
    
    for t in text_list:
        res = extract_response(t, model, access_token)
        highest_key = max(res, key=res.get)
        highest_score = res[highest_key]
        result = {'sentence': t, 'stance': highest_key, 'score': highest_score}
        res_list.append(result)
    
    return res_list
