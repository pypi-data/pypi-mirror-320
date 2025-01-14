
# Import sub-packages
from . import data
from . import model
from . import utils

# Import top-level modules
from .analyze import analyze
from .data_collect import collect

# Define the public API for the package
__all__ = [
    "data",
    "model",
    "utils",
    "analyze",
    "collect",
]






# from .data.collect_data import collect_deletion_discussions, extract_div_contents_with_additional_columns, extract_div_contents_from_url
# from .data.process_data import prepare_dataset
# from .data.collect_data_es import (
#     collect_es, 
#     extract_result_resultado, 
#     extract_result as extract_result_es, 
#     clean_comments_with_no_text_after_timestamp, 
#     extract_cleaned_spanish_discussion_and_result,  
#     extract_multiple_discussions
# )
# from .data.collect_data_gr import (
#     collect_gr,  
#     extract_result as extract_result_gr,  
#     extract_discussions_from_page_collapsible, 
#     extract_discussions_from_page_non_collapsible, 
#     html_to_plaintext as html_to_plaintext_gr, 
#     split_text_into_sentences as split_text_into_sentences_gr, 
#     clean_discussion_text as clean_discussion_text_gr, 
#     extract_outcome_from_text as extract_outcome_from_text_gr, 
#     extract_discussion_section as extract_discussion_section_gr,   
#     extract_fallback_discussion as extract_fallback_discussion_gr, 
#     extract_div_from_title_with_fallback, 
#     normalize_outcome as normalize_outcome_gr
# )
# from .data.collect_data_wikidata_ent import (
#     collect_wikidata_entity, 
#     get_soup as get_soup_wde,  
#     get_year_urls, 
#     get_month_day_urls, 
#     extract_outcome_from_dd, 
#     extract_discussions, 
#     remove_first_sentence_if_q_number, 
#     process_discussions_by_url_list, 
#     html_to_plaintext as html_to_plaintext_wde, 
#     split_text_into_sentences as split_text_into_sentences_wde,  
#     clean_discussion_tag as clean_discussion_tag_wde, 
#     extract_outcome_from_text_elements as extract_outcome_from_text_elements_wde, 
#     extract_discussion_section as extract_discussion_section_wde,  
#     extract_div_from_title as extract_div_from_title_wde
# )
# from .data.collect_data_wikidata_prop import (
#     collect_wikidata,  
#     html_to_plaintext as html_to_plaintext_wdp, 
#     split_text_into_sentences as split_text_into_sentences_wdp, 
#     process_html_to_plaintext, 
#     process_split_text_into_sentences, 
#     extract_outcome_from_div, 
#     extract_cleaned_discussion, 
#     extract_div_contents_with_additional_columns as extract_div_contents_with_additional_columns_wdp, 
#     scrape_wikidata_deletions, 
#     extract_outcome_from_text_elements as extract_outcome_from_text_elements_wdp, 
#     clean_discussion_tag as clean_discussion_tag_wdp, 
#     extract_discussion_section as extract_discussion_section_wdp, 
#     extract_div_from_title as extract_div_from_title_wdp
# )
# from .data.collect_data_wikinews import (
#     collect_wikinews, 
#     get_soup as get_soup_wn, 
#     html_to_plaintext as html_to_plaintext_wn, 
#     extract_fallback_discussion as extract_fallback_discussion_wn, 
#     process_html_to_plaintext as process_html_to_plaintext_wn, 
#     extract_outcome_from_div as extract_outcome_from_div_wn, 
#     extract_following_sentence, 
#     validate_outcome, 
#     update_unknown_outcomes, 
#     collect_wikinews_deletions, 
#     html_to_plaintext as html_to_plaintext_wn2,  # Duplicate name, consider removing one
#     split_text_into_sentences as split_text_into_sentences_wn, 
#     clean_discussion_tag as clean_discussion_tag_wn, 
#     extract_outcome_from_text_elements as extract_outcome_from_text_elements_wn, 
#     extract_discussion_section as extract_discussion_section_wn, 
#     extract_div_from_title as extract_div_from_title_wn
# )
# from .data.collect_data_wikiquote import (
#     collect_wikiquote, 
#     extract_outcome_from_div as extract_outcome_from_div_wq, 
#     html_to_plaintext as html_to_plaintext_wq, 
#     process_html_to_plaintext as process_html_to_plaintext_wq, 
#     split_text_into_sentences as split_text_into_sentences_wq, 
#     process_split_text_into_sentences as process_split_text_into_sentences_wq,  
#     collect_wikiquote_title
# )





# from .model.policy import get_policy
# from .model.outcome import get_outcome
# from .model.stance import get_stance
# from .model.sentiment import get_sentiment
# from .model.offensive import get_offensive_label
# from .analyze import analyze
# from .data_collect import collect
# __all__ = [
    
#     'collect_deletion_discussions',
#     'extract_div_contents_with_additional_columns',
#     'extract_div_contents_from_url',
#     'prepare_dataset',
#     'get_policy',
#     'get_outcome',
#     'get_stance',
#     'get_sentiment',
#     'get_offensive_label',
# ]
