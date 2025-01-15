from transformers import pipeline, AutoTokenizer
from wide_analysis.data import process_data 
from wide_analysis.data.collect_data_wikinews import collect_wikinews
from wide_analysis.data.collect_data_wikiquote import collect_wikiquote
from wide_analysis.data.collect_data_wikidata_ent import collect_wikidata_entity
from wide_analysis.data.collect_data_wikidata_prop import collect_wikidata 
import pysbd
import torch

def extract_highest_score_label(res):
    flat_res = [item for sublist in res for item in sublist]
    highest_score_item = max(flat_res, key=lambda x: x['score'])
    highest_score_label = highest_score_item['label']
    highest_score_value = highest_score_item['score']    
    return highest_score_label, highest_score_value


def get_sentiment(url,mode='url',platform='wikipedia', model =''):
    if mode == 'url':
        if platform == 'wikipedia':
            date = url.split('/')[-1].split('#')[0]
            title = url.split('#')[-1]
            df = process_data.prepare_dataset('title', start_date=date,url=url, title=title)
            text = df['discussion'].iloc[0]
        elif platform == 'wikinews':
            df = collect_wikinews(url = url, mode='url')
            text = df['discussion'].iloc[0]
        elif platform == 'wikiquotes':
            df = collect_wikiquote(url =url, mode='url')
            text = df['discussion'].iloc[0]
        elif platform == 'wikidata_entity':
            df = collect_wikidata_entity(url, mode='url')
            text = df['discussion'].iloc[0]
        elif platform == 'wikidata_property':
            df =  collect_wikidata(url =url, mode='url')
            text = df['discussion'].iloc[0]
        else:
            raise ValueError("Invalid platform. Choose from ['wikipedia', 'wikinews', 'wikiquotes', 'wikidata_entity', 'wikidata_property']")

    else:
        text = url
        

    #sentiment analysis
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_name = model if model != '' else "cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = pipeline("text-classification", model=model_name, top_k= None,device= device,max_length = 512,truncation=True)

    #sentence tokenize the text using pysbd
    seg = pysbd.Segmenter(language="en", clean=False)
    text_list = seg.segment(text)

    res = []
    for t in text_list:
        results = model(t)
        highest_label, highest_score = extract_highest_score_label(results)
        result = {'sentence': t,'sentiment': highest_label, 'score': highest_score}
        res.append(result)
    return res
