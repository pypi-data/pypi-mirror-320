# from transformers import pipeline, AutoTokenizer
# from wide_analysis.data.process_data import prepare_dataset
# import pandas as pd
# import pysbd
# import torch

from transformers import pipeline, AutoTokenizer
from wide_analysis.data import process_data
from wide_analysis.data.collect_data_wikinews import collect_wikinews
from wide_analysis.data.collect_data_wikiquote import collect_wikiquote
from wide_analysis.data.collect_data_wikidata_ent import collect_wikidata_entity
from wide_analysis.data.collect_data_wikidata_prop import collect_wikidata 
import pandas as pd
import pysbd
import torch


def extract_response(text, model_name):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    label_mapping = {'Wikipedia:Notability': 0,
            'Wikipedia:What Wikipedia is not': 1,
            'Wikipedia:Neutral point of view': 2,
            'Wikipedia:Verifiability': 3,
            'Wikipedia:Wikipedia is not a dictionary': 4,
            'Wikipedia:Wikipedia is not for things made up one day': 5,
            'Wikipedia:Criteria for speedy deletion': 6,
            'Wikipedia:Deletion policy': 7,
            'Wikipedia:No original research': 8,
            'Wikipedia:Biographies of living persons': 9,
            'Wikipedia:Arguments to avoid in deletion discussions': 10,
            'Wikipedia:Conflict of interest': 11,
            'Wikipedia:Articles for deletion': 12
            }
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    pipe = pipeline("text-classification", model=model_name, tokenizer=tokenizer, top_k=None,device= device,max_length = 512,truncation=True)

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

def get_policy(url, mode='url',platform='wikipedia', model_name=''):
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
            raise ValueError("Invalid platform. Choose from ['wikipedia', 'wikinews', 'wikiquotes', 'wikidata_entity', 'wikidata_property']")


        # date = url.split('/')[-1].split('#')[0]
        # title = url.split('#')[-1]
        # df = process_data.prepare_dataset('title', start_date=date,url=url, title=title)
        # text = df['discussion'].iloc[0]
    else:
        text = url
    seg = pysbd.Segmenter(language="en", clean=False)
    text_list = seg.segment(text)
    model = model_name if model_name != '' else  'research-dump/bert-large-uncased_wikistance_policy_v1'
    res_list = []
    
    for t in text_list:
        res = extract_response(t, model)
        highest_key = max(res, key=res.get)
        highest_score = res[highest_key]
        result = {'sentence': t, 'policy': highest_key, 'score': highest_score}
        res_list.append(result)
    
    return res_list

