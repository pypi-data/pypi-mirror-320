# from .collect_data import collect_deletion_discussions, extract_div_contents_with_additional_columns, extract_div_contents_from_url
# from .process_data import process_data, prepare_dataset

from . import collect_data
from . import collect_data_es
from . import collect_data_gr
from . import collect_data_wikidata_ent
from . import collect_data_wikidata_prop
from . import collect_data_wikinews
from . import collect_data_wikiquote
from . import process_data

# Define the public API for the package
__all__ = [
    "collect_data",
    "collect_data_es",
    "collect_data_gr",
    "collect_data_wikidata_ent",
    "collect_data_wikidata_prop",
    "collect_data_wikinews",
    "collect_data_wikiquote",
    "process_data",
]




# from .collect_data_es import collect_es,extract_result_resultado, extract_result, clean_comments_with_no_text_after_timestamp, extract_cleaned_spanish_discussion_and_result,  extract_result,extract_multiple_discussions 
# from .collect_data_gr import collect_gr,  extract_result,  extract_discussions_from_page_collapsible, extract_discussions_from_page_non_collapsible, html_to_plaintext, split_text_into_sentences, clean_discussion_text, extract_outcome_from_text, extract_discussion_section,   extract_fallback_discussion, extract_div_from_title_with_fallback, normalize_outcome 
# from .collect_data_wikidata_ent import collect_wikidata_entity, get_soup,  get_year_urls, get_month_day_urls, extract_outcome_from_dd, extract_discussions, remove_first_sentence_if_q_number, process_discussions_by_url_list, html_to_plaintext, split_text_into_sentences,  clean_discussion_tag, extract_outcome_from_text_elements, extract_discussion_section,  extract_div_from_title
# from .collect_data_wikidata_prop import collect_wikidata,  html_to_plaintext, split_text_into_sentences, process_html_to_plaintext, process_split_text_into_sentences, extract_outcome_from_div, extract_cleaned_discussion, extract_div_contents_with_additional_columns, scrape_wikidata_deletions, extract_outcome_from_text_elements, clean_discussion_tag, extract_discussion_section, extract_div_from_title
# from .collect_data_wikinews import collect_wikinews, get_soup, html_to_plaintext, extract_fallback_discussion, process_html_to_plaintext, extract_outcome_from_div, extract_following_sentence, validate_outcome, update_unknown_outcomes, collect_wikinews_deletions, collect_wikinews,  html_to_plaintext,  split_text_into_sentences, clean_discussion_tag, extract_outcome_from_text_elements, extract_discussion_section, extract_div_from_title
# from .collect_data_wikiquote import collect_wikiquote, extract_outcome_from_div, html_to_plaintext, process_html_to_plaintext, split_text_into_sentences, process_split_text_into_sentences,  collect_wikiquote_title


# __all__ = [
#     'collect_deletion_discussions',
#     'extract_div_contents_with_additional_columns',
#     'extract_div_contents_from_url',
#     'process_data',
#     'prepare_dataset'
# ]

# __init__.py

# from .collect_data import (
#     collect_deletion_discussions, 
#     extract_div_contents_with_additional_columns as extract_div_contents_with_additional_columns_cd,
#     extract_div_contents_from_url
# )
# from .process_data import process_data, prepare_dataset
# from .collect_data_es import (
#     collect_es, 
#     extract_result_resultado, 
#     extract_result as extract_result_es, 
#     clean_comments_with_no_text_after_timestamp, 
#     extract_cleaned_spanish_discussion_and_result,  
#     extract_multiple_discussions
# )
# from .collect_data_gr import (
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
# from .collect_data_wikidata_ent import (
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
# from .collect_data_wikidata_prop import (
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
# from .collect_data_wikinews import (
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
# from .collect_data_wikiquote import (
#     collect_wikiquote, 
#     extract_outcome_from_div as extract_outcome_from_div_wq, 
#     html_to_plaintext as html_to_plaintext_wq, 
#     process_html_to_plaintext as process_html_to_plaintext_wq, 
#     split_text_into_sentences as split_text_into_sentences_wq, 
#     process_split_text_into_sentences as process_split_text_into_sentences_wq,  
#     collect_wikiquote_title
# )

# __all__ = [
#     'collect_deletion_discussions',
#     'extract_div_contents_from_url',
#     'process_data',
#     'prepare_dataset',
#     'collect_es',
#     'extract_result_resultado',
#     'extract_result_es',
#     'extract_cleaned_spanish_discussion_and_result',
#     'extract_multiple_discussions',
#     'collect_gr',
#     'extract_result_gr',
#     'extract_discussions_from_page_collapsible',
#     'extract_discussions_from_page_non_collapsible',
#     'html_to_plaintext_gr',
#     'split_text_into_sentences_gr',
#     'clean_discussion_text_gr',
#     'extract_outcome_from_text_gr',
#     'extract_discussion_section_gr',
#     'extract_fallback_discussion_gr',
#     'extract_div_from_title_with_fallback',
#     'normalize_outcome_gr',
#     'collect_wikidata_entity',
#     'get_soup_wde',
#     'get_year_urls',
#     'get_month_day_urls',
#     'extract_outcome_from_dd',
#     'extract_discussions',
#     'remove_first_sentence_if_q_number',
#     'process_discussions_by_url_list',
#     'html_to_plaintext_wde',
#     'split_text_into_sentences_wde',
#     'clean_discussion_tag_wde',
#     'extract_outcome_from_text_elements_wde',
#     'extract_discussion_section_wde',
#     'extract_div_from_title_wde',
#     'collect_wikidata',
#     'html_to_plaintext_wdp',
#     'split_text_into_sentences_wdp',
#     'process_html_to_plaintext',
#     'process_split_text_into_sentences',
#     'extract_outcome_from_div',
#     'extract_cleaned_discussion',
#     'extract_div_contents_with_additional_columns_wdp',
#     'scrape_wikidata_deletions',
#     'extract_outcome_from_text_elements_wdp',
#     'clean_discussion_tag_wdp',
#     'extract_discussion_section_wdp',
#     'extract_div_from_title_wdp',
#     'collect_wikinews',
#     'get_soup_wn',
#     'html_to_plaintext_wn',
#     'extract_fallback_discussion_wn',
#     'process_html_to_plaintext_wn',
#     'extract_outcome_from_div_wn',
#     'extract_following_sentence',
#     'validate_outcome',
#     'update_unknown_outcomes',
#     'collect_wikinews_deletions',
#     'split_text_into_sentences_wn',
#     'clean_discussion_tag_wn',
#     'extract_outcome_from_text_elements_wn',
#     'extract_discussion_section_wn',
#     'extract_div_from_title_wn',
#     'collect_wikiquote',
#     'extract_outcome_from_div_wq',
#     'html_to_plaintext_wq',
#     'process_html_to_plaintext_wq',
#     'split_text_into_sentences_wq',
#     'process_split_text_into_sentences_wq',
#     'collect_wikiquote_title'
# ]

