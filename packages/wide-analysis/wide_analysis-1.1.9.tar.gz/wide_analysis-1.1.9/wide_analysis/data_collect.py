from datetime import datetime
from wide_analysis.data import process_data, collect_data, collect_data_wikidata_ent, collect_data_wikidata_prop, collect_data_wikinews, collect_data_wikiquote, collect_data_es, collect_data_gr
from datasets import load_dataset
from wide_analysis.utils.collect_editor_stats import collect_editor_info
import pandas as pd

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

def collect(mode, start_date=None, end_date=None, url=None, title=None, output_path=None,
            platform=None, lang=None,  dataset_name = None):
    if mode not in ['date_range', 'date', 'title', 'url', 'existing', 'editor_info']:
        raise ValueError("Invalid mode. Choose from ['date_range', 'date', 'title', 'url', 'existing', 'editor_info']")

    if mode == 'existing': #wide_2023':
        if dataset_name == 'wide_2023':
            dataset = load_dataset('hsuvaskakoty/wide_analysis')
            print('Dataset loaded successfully as huggingface dataset')
            print('The dataset has the following columns:', dataset.column_names)
            return dataset
        elif dataset_name == 'wiki-stance-policy':
            dataset = load_dataset("research-dump/wiki-stance-en", data_dir="en", split=None)
            
            train_dataset = dataset['train']
            test_dataset = dataset['test']
            val_dataset = dataset['validation']

            desired_columns = ['title', 'username', 'timestamp', 'comment', 'policy_title']
            policy_dataset = {
                    'train': train_dataset.remove_columns([col for col in train_dataset.column_names if col not in desired_columns]),
                    'test': test_dataset.remove_columns([col for col in test_dataset.column_names if col not in desired_columns]),
                    'validation': val_dataset.remove_columns([col for col in val_dataset.column_names if col not in desired_columns])
                }
            return policy_dataset
        elif dataset_name == 'wiki-stance-stance':
            dataset = load_dataset("research-dump/wiki-stance-en", data_dir="en", split=None)
            desired_columns = ['title', 'username', 'timestamp', 'decision', 'comment', 'topic']
            train_dataset = dataset['train']
            test_dataset = dataset['test']
            val_dataset = dataset['validation']
            stance_dataset = {
                    'train': train_dataset.remove_columns([col for col in train_dataset.column_names if col not in desired_columns]),
                    'test': test_dataset.remove_columns([col for col in test_dataset.column_names if col not in desired_columns]),
                    'validation': val_dataset.remove_columns([col for col in val_dataset.column_names if col not in desired_columns])
                }
            return stance_dataset
        elif dataset_name == 'wiki-stance-policy':
            dataset = load_dataset("research-dump/wiki-stance-en", data_dir="en", split=None)
            desired_columns = ['title', 'username', 'timestamp', 'comment','topic', 'policy_title']
            train_dataset = dataset['train']
            test_dataset = dataset['test']
            val_dataset = dataset['validation']
        else:
            raise ValueError("Invalid dataset_name. Choose from ['wide_2023', 'wiki-stance-policy', 'wiki-stance-stance']")

    if mode == "editor_info":
        editor_info = collect_editor_info(url, lang, title, date=start_date, platform=platform)
        df = pd.DataFrame(editor_info["User Statistics"])
        return df


    underlying_mode = mode if mode not in ['date', 'date_range'] else 'year'
    
    if platform is None and lang is None or (platform == 'wikipedia' and lang == 'en'):
        if mode in ['date_range', 'date', 'title']:
            return process_data.prepare_dataset(
                mode=mode,
                start_date=start_date,
                end_date=end_date,
                url=url,
                title=title,
                output_path=output_path
            )
        else:
            print("Invalid input. Choose from ['date_range', 'date', 'title', 'wide_2023']")
            return None

    if platform == 'wikidata_entity':
        if underlying_mode == 'title':
            if not title:
                raise ValueError("For 'title' mode in wikidata entity, 'title' must be provided.")
            return collect_data_wikidata_ent.collect_wikidata_entity(mode='title', title=title, years=[])
        elif underlying_mode == 'year':
            if start_date and end_date:
                start_year = int(datetime.strptime(start_date, "%Y-%m-%d").year)
                end_year = int(datetime.strptime(end_date, "%Y-%m-%d").year)
                return collect_data_wikidata_ent.collect_wikidata_entity(mode='year', years=[start_year, end_year])
            elif start_date:
                single_year = int(datetime.strptime(start_date, "%Y-%m-%d").year)
                return collect_data_wikidata_ent.collect_wikidata_entity(mode='year', years=single_year)
            else:
                raise ValueError("For 'year' mode in wikidata entity, start_date is required.")
        elif underlying_mode == 'url':
            if not url:
                raise ValueError("For 'url' mode in wikidata entity, 'url' must be provided.")
            return collect_data_wikidata_ent.collect_wikidata_entity(mode='url', url=url)
        else:
            raise ValueError("Invalid mode for wikidata entity. Use 'title', 'url', or 'year'.")

    elif platform == 'wikidata_property':
        if underlying_mode == 'title':
            if not title:
                raise ValueError("For 'title' mode in wikidata property, 'title' must be provided.")
            return collect_data_wikidata_prop.collect_wikidata(mode='title', title=title, years=[])
        elif underlying_mode == 'url':
            if not url:
                raise ValueError("For 'url' mode in wikidata property, 'url' must be provided.")
            return collect_data_wikidata_prop.collect_wikidata(mode='url', title='', url=url, years=[])
        elif underlying_mode == 'year':
            if start_date and end_date:
                start_year = int(datetime.strptime(start_date, "%Y-%m-%d").year)
                end_year = int(datetime.strptime(end_date, "%Y-%m-%d").year)
                return collect_data_wikidata_prop.collect_wikidata(mode='year', years=[start_year, end_year])
            elif start_date:
                single_year = int(datetime.strptime(start_date, "%Y-%m-%d").year)
                return collect_data_wikidata_prop.collect_wikidata(mode='year', years=single_year)
            else:
                raise ValueError("For 'year' mode in wikidata property, start_date is required.")
        else:
            raise ValueError("Invalid mode for wikidata property. Use 'title', 'url', or 'year'.")

    elif platform == 'wikinews':
        if underlying_mode == 'title':
            if not title:
                raise ValueError("For 'title' mode in wikinews, 'title' is required.")
            return collect_data_wikinews.collect_wikinews(mode='title', title=title)
        elif underlying_mode == 'url':
            if not url:
                raise ValueError("For 'url' mode in wikinews, 'url' is required.")
            return collect_data_wikinews.collect_wikinews(mode='url', url=url)
        elif underlying_mode == 'year':
            if start_date and end_date:
                start_y = int(datetime.strptime(start_date, "%Y-%m-%d").year)
                end_y = int(datetime.strptime(end_date, "%Y-%m-%d").year)
                return collect_data_wikinews.collect_wikinews(mode='year', year=[start_y, end_y])
            elif start_date:
                single_y = int(datetime.strptime(start_date, "%Y-%m-%d").year)
                return collect_data_wikinews.collect_wikinews(mode='year', year=single_y)
            else:
                raise ValueError("For 'year' mode in wikinews, start_date is required.")
        else:
            raise ValueError("Invalid mode for wikinews. Use 'title', 'url', or 'year'.")

    elif platform == 'wikiquote':
        if underlying_mode == 'title':
            if not title:
                title = 'all'
            return collect_data_wikiquote.collect_wikiquote(mode='title', title=title)
        elif underlying_mode == 'url':
            if not url:
                raise ValueError("For 'url' mode in wikiquote, 'url' must be provided.")
            return collect_data_wikiquote.collect_wikiquote(mode='url', url=url)
        else:
            raise ValueError("Wikiquote collection currently only supports 'title' or 'url' mode.")

    elif platform == 'wikipedia':
        if lang == 'es':
            if underlying_mode == 'title':
                if not title or (start_date and start_date.strip()):
                    raise ValueError("For 'title' mode in Spanish Wikipedia, 'title' must be provided and start_date must be empty.")
                return collect_data_es.collect_es(mode='title', title=title, date='')
            
            elif underlying_mode == 'url':
                if not url:
                    raise ValueError("For 'url' mode in Spanish Wikipedia, 'url' must be provided.")
                return collect_data_es.collect_es(mode='url', title='', url=url)
            
            elif underlying_mode == 'year':
                start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
                if not start_date:
                    raise ValueError("For 'year' mode in Spanish Wikipedia, start_date (dd/mm/yyyy) is required.")
                return collect_data_es.collect_es(mode='year', title='', date=start_date)
            else:
                raise ValueError("Invalid mode for Spanish Wikipedia. Use 'title' or 'year'.")

        elif lang == 'gr':
            if underlying_mode == 'title':
                if not title or not start_date or len(start_date.split('/')) != 2:
                    raise ValueError("For 'title' mode in Greek Wikipedia, 'title' and start_date='mm/yyyy' are required.")
                return collect_data_gr.collect_gr(mode='title', title=title, years=[start_date])
            elif underlying_mode == 'url':
                if not url:
                    raise ValueError("For 'url' mode in Greek Wikipedia, 'url' must be provided.")
                return collect_data_gr.collect_gr(mode='url', title='', url=url)
            elif underlying_mode == 'year':
                if start_date and end_date:
                    start_y = int(datetime.strptime(start_date, "%Y-%m-%d").year)
                    end_y = int(datetime.strptime(end_date, "%Y-%m-%d").year)
                    return collect_data_gr.collect_gr(mode='year', title='', years=[start_y, end_y])
                elif start_date:
                    single_y = int(datetime.strptime(start_date, "%Y-%m-%d").year)
                    return collect_data_gr.collect_gr(mode='year', title='', years=[single_y])
                else:
                    raise ValueError("For 'year' mode in Greek Wikipedia, start_date is required.")
            else:
                raise ValueError("Invalid mode for Greek Wikipedia. Use 'title' or 'year'.")

        else:
            raise ValueError("Invalid lang for wikipedia. Use 'en', 'es', or 'gr'.")

    else:
        raise ValueError("Invalid platform. Use 'wikipedia', 'wikidata_entity', 'wikidata_property', 'wikinews', or 'wikiquote'.")

