# Wide-Analysis : Suite for Content Moderation Analysis of Wiki-Platforms

## Introduction

Wide-Analysis is a suite of tools for analyzing Wikipedia deletion discussions. It is designed to help researchers and practitioners to understand the dynamics of deletion discussions, and to develop tools for supporting the decision-making process in Wikipedia. The suite includes a set of tools for collecting, processing, and analyzing deletion discussions. The package contains the following functionalities
- **Data Collection and preprcoessing**: Collecting deletion discussions from Wikipedia and prepare a dataset. This can be done in article title level, or in date-range level.
- **Model based functionalities**: The suite includes a set of Language Model based tasks, such as: 
    - **Outcome Prediction**: Predicting the outcome of a deletion discussion, the outcome can be the decision made with the discussion (e.g., keep, delete, merge, etc.) (determined from the complete discussion)
    - **Stance Detection**: Identifying the stance of the participants in the discussion, in relation to the deletion decision.(determined from each individual comment in discussion)
    - **Policy Prediction**: Predicting the policy that is most relevant to the comments of the participants in the discussion.(determined from each individual comment in discussion)
    - **Sentiment Prediction**: Predicting the sentiment of the participants in the discussion, in relation to the deletion decision.(determined from each individual comment in discussion)
    - **Offensive Language Detection**: Detecting offensive language in the comments of the participants in the discussion.(determined from each individual comment in discussion)

Following gives an overview of the suite:

![WiDe-Analysis Overview](wide_analysis/asset/Wide_Analysis_overall.png)


## Get started 🚀

You can install the package from PyPI using the following command:

```pip install wide-analysis```

After the installation, you can import the package and start using the functionalities.



## Create dataset

The dataset creation funtionalities will return a dataframe. The data collection command contains the following parameters:
- mode : str
    - The mode of data collection. It can be 'article', 'date_range', or 'date' or 'existing'.
- start_date : str
    - The start date of the data collection. It should be in the format 'YYYY-MM-DD'(for example, '2021-01-01').
- end_date : str
    - The end date of the data collection. It should be in the format 'YYYY-MM-DD'(for example, '2021-01-01'). If left empty, the data collection will be done for a single date(start_date).
- url : str (optional)
    - The URL of the Wikipedia deletion discussion log page. Only needed for title based extraction. for example: https://en.wikipedia.org/wiki/Wikipedia:Articles_for_deletion/Log/2021_January_1
- title : str
    - The title of the Wikipedia article. only needed for title based extraction. for example: 'COVID-19_pandemic_in_India'
- output_path : str
    - The path to save the dataset.The dataset will be saved as 'csv' file. If not provided, the dataset will be returned as a dataframe.
- platform: str
    - The platform from which the data will be collected. It can be one of the following: 'wikipedia', 'wikidata_entity' 'wikidata_property', 'wikiquote', 'wikinews'.
-lang:str
    - The language of the data to be collected. Currently, it can be one of the following: 'en', 'es', 'gr'.
- dataset_name : str
    - The name of the existing dataset. It can be `wide_2023` or `wiki_stance (_stance or _policy)`. If selected `wide_2023` as mode parameter, then the data will be collected from the existing Wide-analysis dataset available in huggingface('hsuvaskakoty/wide_analysis'). The function will return a HuggingFace dataset. If `wiki_stance` is selected, it will return the English dataset of the 'Wiki-stance' dataset (see [Kaffee et al., 2023](https://arxiv.org/abs/2310.05779)).

We show all the following examples in the context of **Wikipedia deletion discussions**.


Creation of dataset can be done in four ways:

- **Wide-analysis Dataset**: If selected 'wide_2023' as mode parameter, then the data will be collected from the existing Wide-analysis dataset available in huggingface('hsuvaskakoty/wide_analysis') and the function will return huggingface dataset.

```python
from wide_analysis import collect
data = collect(mode = 'existing', 
                            start_date=None, 
                            end_date=None, 
                            url=None, 
                            title=None, 
                            output_path=None,
                            platform='wikipedia',
                            lang='en',
                            dataset_name='wide_2023')
```
will return the existing dataset available in huggingface('hsuvaskakoty/wide_analysis').

```python
Datset loaded successfully as huggingfaece dataset
The dataset has the following columns: {'train': ['text', 'label'], 'validation': ['text', 'label'], 'test': ['text', 'label']}
```

- **Article level**: Collecting deletion discussions for a specific article.
```python
from wide_analysis import collect
data = collect(mode = 'title', 
                            start_date='YYYY-MM-DD', 
                            end_date=None, 
                            url='URL for the title', 
                            title='article title', 
                            output_path='save_path' or None)
```

Example:
To collect the deletion discussions for the article 'Raisul Islam Ador' for the date '2024-07-18', the following command can be used:

```python
from wide_analysis import collect
data = collect(mode = 'title', 
                            start_date='2024-07-18', 
                            end_date=None, 
                            url='https://en.wikipedia.org/wiki/Wikipedia:Articles_for_deletion/Log/2024_July_15#Raisul_Islam_Ador', 
                            title='Raisul Islam Ador', 
                            output_path= None)
```
This will return a dataframe with the data for the title 'Raisul Islam Ador' for the date '2024-07-18'. If the output_path is provided, the dataframe will be saved as a csv file in the provided path. The output looks like the following:

| Date       | Title               | URL                | Discussion             | Label         | Confirmation                  |
|------------|---------------------|--------------------|------------------------|---------------|-------------------------------|
| 2024-07-18 | Raisul Islam Ador   | [URL to article text](https://en.wikipedia.org/w/index.php?title=Raisul_Islam_Ador&action=edit&redlink=1) | Deletion discussion here | speedy delete | Please do not modify it.      |



- **Date range level**: Collecting deletion discussions for a specific date range.
```python
from wide_analysis importcollect
data = collect(mode = 'date_range', 
                            start_date='YYYY-MM-DD', 
                            end_date='YYYY-MM-DD', 
                            url=None, 
                            title=None, 
                            output_path='save_path' or None)
```
Example:
To collect the deletion discussions for the articles within the date range '2024-07-18' and '2024-07-20', the following command can be used:

```python
from wide_analysis import collect
data = collect(mode = 'date_range', 
                            start_date='2024-07-18', 
                            end_date='2024-07-20', 
                            url=None, 
                            title=None, 
                            output_path= None)
```

This will return a dataframe with the data for the articles within the date range '2024-07-18' and '2024-07-20'. The output looks like the same format as the article level data collection, just with more rows for each date within the date range.


- **Date level**: Collecting deletion discussions for a specific date.
```python
from wide_analysis import collect
data = collect(mode = 'date', 
                            start_date='YYYY-MM-DD', 
                            end_date=None, 
                            url=None, 
                            title=None, 
                            output_path= None)
```

Example:
To collect the deletion discussions for the articles within the date '2024-07-18', the following command can be used:

```python
from wide_analysis import collect
data = collect(mode = 'date', 
                            start_date='2024-07-18', 
                            end_date=None, 
                            url=None, 
                            title=None, 
                            output_path= None)
```

This will return a dataframe with the data for the articles within the date '2024-07-18'. The output looks like the same format as the article level data collection, just with more rows for each article within the date.


## Model based functionalities

We train a set of models and leverage some pretrained task based models from huggingface for the following tasks: Outcome Prediction, Stance Detection, Policy Prediction, Sentiment Prediction, and Offensive Language Detection. The functionalities will return a dictionary, with the predictions for each task and their individual probablity score. The model based functionalities contain the following parameters:

- inp: 'str'
    - The url or text of the Wikipedia article deletion discussion.
- mode: 'str'
    - The mode of the input. it can be 'url' or 'text'. If 'url' is selected, the input should be the URL of the Wikipedia article deletion discussion. If 'text' is selected, the input should be the text of the Wikipedia article deletion discussion in the following format: _Title: Deletion discussion Text_ where Title is the title of the article and Text is the deletion discussion. Default is 'url'.
- task: 'str'
    - The task to be performed. It can be 'outcome', 'stance', 'policy', 'sentiment', or 'offensive'.
- platform: str
    - The platform from which the data will be collected. It can be one of the following: 'wikipedia', 'wikidata_entity' 'wikidata_property', 'wikiquote', 'wikinews'.
-lang:str
    - The language of the data to be collected. Currently, it can be one of the following: 'en', 'es', 'gr'.
- model: 'str'
    - The model to be used for prediction. Default is the best performing task based Wiki model from [WiDe-Analysis collection](https://huggingface.co/collections/hsuvaskakoty/wide-analysis-675f425372181d3bd410425c). You can choose your own model from huggingface model hub from the collection.

It is worth noting that the model based functionalities are only available for the article level data collection. We also provide an explanation feature for _outcome prediction_ task, which will return the explanation of the prediction made by the model using Openai GPT4 model of user's chouce with default GPT 4o-mini model. You will need your own API key for this feature to work.

### Outcome Prediction

Apart from the input parameters, the outcome prediction function also contains the following parameters:

- openai_access_token: 'str'
    - The API key for Openai GPT 4o-mini model. If explanation is True, then it will ask for the API key for Openai GPT 4o-mini model. Default is None.
- explanation: 'bool'
    - If True, it will return the explanation of the prediction made by the model. Default is False.
- explainer model: 'str'
    - The model to be used for explanation. Default is 'gpt4o-mini'.


```python
from wide_analysis import analyze
predictions = analyze(inp='URL/text of the article',
                    mode='url or text',
                    task='outcome',
                    openai_access_token=None,
                    explanation=False,
                    platform = 'wikipedia',
                    lang='en',
                    explainer_model='gpt4o-mini',
                    model ='')
```
<!-- This will trigger a set of questions :
- Do you want an explanation?(True/False): If True, it will return the explanation of the prediction made by the model.
- If explanation is True, then it will ask for the API key for Openai GPT 3.5 model. -->

Example:
To predict the outcome of the deletion discussion for the article 'Raisul Islam Ador' using discussion url, the following command can be used:

```python
from wide_analysis import analyze
predictions = analyze(inp='https://en.wikipedia.org/wiki/Wikipedia:Articles_for_deletion/Log/2024_July_15#Raisul_Islam_Ador',
                mode= 'url', 
                task='outcome',
                openai_access_token=None,
                explanation=False,
                platform = 'wikipedia',
                lang='en',
                explainer_model='gpt4o-mini',
                model ='')
```
OR if using text:

```python
from wide_analysis import analyze
text_input = 'Raisul Islam Ador: None establish his Wikipedia:Notability. The first reference is almost identical in wording to his official web site.CambridgeBayWeather (solidly non-human), Uqaqtuq (talk) , Huliva 20:06, 15 July 2024 (UTC) [ reply ] Delete , if not a CSD under G11.' #sample input text
predictions = analyze(inp=text_input, 
                    mode= 'text', 
                    task='outcome', 
                    openai_access_token=None, 
                    explanation=False,
                    platform = 'wikipedia',
                    lang='en',
                    explainer_model='gpt4o-mini',
                    model ='')
```

Both of which will return the following output:
```python
{'prediction': 'speedy delete', 'probability': 0.99}
```

To predict the outcome of the deletion discussion for the article 'Raisul Islam Ador' with explanation, the following command can be used:
    
```python
from wide_analysis import analyze
predictions = analyze(inp='https://en.wikipedia.org/wiki/Wikipedia:Articles_for_deletion/Log/2024_July_15#Raisul_Islam_Ador',
                    mode='url', 
                    task='outcome',
                    openai_access_token='<OPENAI KEY>',
                    explanation=True,
                     platform = 'wikipedia',
                    lang='en',
                    explainer_model='gpt4o-mini',
                    model ='')
```
<!-- Then the following questions will be asked:

```python
Do you want an explanation?(True/False): True
Please enter your API key for Openai GPT: <OPENAI KEY>
``` -->

Returns:
```python
{'prediction': 'speedy delete', 
'probability': 0.99, 
'explanation': 'The article does not establish the notability of the subject. The references are not reliable and the article is not well written. '}
```

### Stance Detection

```python
from wide_analysis import analyze
predictions = analyze(inp='URL/text of the article',
                    mode='url or text', 
                    task='stance',
                    platform = 'platform name',
                    lang='en/es/gr',
                    model ='model name')
```

Example:
To predict the stance of the participants in the deletion discussion for the article 'Raisul Islam Ador', the following command can be used:

```python
from wide_analysis import analyze
predictions = analyze(inp='https://en.wikipedia.org/wiki/Wikipedia:Articles_for_deletion/Log/2024_July_15#Raisul_Islam_Ador'
                    mode = 'url', 
                    task='stance',
                    platform = 'wikipedia',
                    lang='en',
                    model ='')
```

OR if using text:

```python
from wide_analysis import analyze
text_input = 'Raisul Islam Ador: None establish his Wikipedia:Notability. The first reference is almost identical in wording to his official web site.CambridgeBayWeather (solidly non-human), Uqaqtuq (talk) , Huliva 20:06, 15 July 2024 (UTC) [ reply ] Delete , if not a CSD under G11.' #sample input text
predictions = analyze(inp=text_input, mode= 'text', task='stance')
```

Both of which will return the following output:
```python
[{'sentence': 'None establish his Wikipedia:Notability .  ', 'stance': 'delete', 'score': 0.9950249791145325}, 
{'sentence': 'The first reference is almost identical in wording to his official web site.  ', 'stance': 'delete', 'score': 0.7702090740203857}, 
{'sentence': 'CambridgeBayWeather (solidly non-human), Uqaqtuq (talk) , Huliva 20:06, 15 July 2024 (UTC) [ reply ] Delete , if not a CSD under G11.  ', 'stance': 'delete', 'score': 0.9993199110031128}]
```

### Policy Prediction

```python
from wide_analysis import analyze
predictions = analyze(inp='URL/text of the article',
                    mode='url or text', 
                    task='policy',
                    platform = 'platform name',
                    lang='en/es/gr',
                    model ='model name')
```

Example:
To predict the policy that is most relevant to the comments of the participants in the deletion discussion for the article 'Raisul Islam Ador', the following command can be used:

```python
from wide_analysis import analyze
predictions = analyze(inp='https://en.wikipedia.org/wiki/Wikipedia:Articles_for_deletion/Log/2024_July_15#Raisul_Islam_Ador'
                    mode = 'url', 
                    task='policy', 
                    platform = 'wikipedia',
                    lang='en',
                    model ='')
```
OR if using text:

```python
from wide_analysis import analyze
text_input = 'Raisul Islam Ador: None establish his Wikipedia:Notability. The first reference is almost identical in wording to his official web site.CambridgeBayWeather (solidly non-human), Uqaqtuq (talk) , Huliva 20:06, 15 July 2024 (UTC) [ reply ] Delete , if not a CSD under G11.' #sample input text
predictions = analyze(inp=text_input, mode= 'text', task='policy')
```

Both of which will return the following output:
```python
[{'sentence': 'None establish his Wikipedia:Notability .  ', 'policy': 'Wikipedia:Notability', 'score': 0.8100407719612122}, 
{'sentence': 'The first reference is almost identical in wording to his official web site.  ', 'policy': 'Wikipedia:Notability', 'score': 0.6429345607757568}, 
{'sentence': 'CambridgeBayWeather (solidly non-human), Uqaqtuq (talk) , Huliva 20:06, 15 July 2024 (UTC) [ reply ] Delete , if not a CSD under G11.  ', 'policy': 'Wikipedia:Criteria for speedy deletion', 'score': 0.9400111436843872}]
```

### Sentiment Prediction

```python
from wide_analysis import analyze
predictions = analyze(inp='URL/text of the article',
                    mode='url or text', 
                    task='sentiment')
```

Example:
To predict the sentiment of the participants in the deletion discussion for the article 'Raisul Islam Ador' with url, the following command can be used:

```python
from wide_analysis import analyze
predictions = analyze(inp='https://en.wikipedia.org/wiki/Wikipedia:Articles_for_deletion/Log/2024_July_15#Raisul_Islam_Ador',mode='url' task='sentiment')
```
OR if using text:

```python
from wide_analysis import analyze
text_input = 'Raisul Islam Ador: None establish his Wikipedia:Notability. The first reference is almost identical in wording to his official web site.CambridgeBayWeather (solidly non-human), Uqaqtuq (talk) , Huliva 20:06, 15 July 2024 (UTC) [ reply ] Delete , if not a CSD under G11.' #sample input text
predictions = analyze(inp=text_input, mode= 'text', task='sentiment')
```

Both of which will return the following output:
```python
[{'sentence': 'None establish his Wikipedia:Notability .  ', 'sentiment': 'negative', 'score': 0.515991747379303},
 {'sentence': 'The first reference is almost identical in wording to his official web site.  ', 'sentiment': 'neutral', 'score': 0.9082792401313782}, 
 {'sentence': 'CambridgeBayWeather (solidly non-human), Uqaqtuq (talk) , Huliva 20:06, 15 July 2024 (UTC) [ reply ] Delete , if not a CSD under G11.  ', 'sentiment': 'neutral', 'score': 0.8958092927932739}, ]
```

### Offensive Language Detection

```python
from wide_analysis import analyze
predictions = analyze(inp='URL/text of the article',mode='url or text', task='offensive')
```

Example:
To detect offensive language in the comments of the participants in the deletion discussion for the article 'Raisul Islam Ador', the following command can be used:

```python
from wide_analysis import analyze
predictions = analyze(inp='https://en.wikipedia.org/wiki/Wikipedia:Articles_for_deletion/Log/2024_July_15#Raisul_Islam_Ador',mode='url', task='offensive')
```
OR if using text:

```python
from wide_analysis import analyze
text_input = 'Raisul Islam Ador: None establish his Wikipedia:Notability. The first reference is almost identical in wording to his official web site.CambridgeBayWeather (solidly non-human), Uqaqtuq (talk) , Huliva 20:06, 15 July 2024 (UTC) [ reply ] Delete , if not a CSD under G11.' #sample input text
predictions = analyze(inp=text_input, mode= 'text', task='offensive')
```

Both of which will return the following output:
```python
[{'sentence': 'None establish his Wikipedia:Notability .  ', 'offensive_label': 'non-offensive', 'score': 0.8752073645591736}, 
{'sentence': 'The first reference is almost identical in wording to his official web site.  ', 'offensive_label': 'non-offensive', 'score': 0.9004920721054077},
{'sentence': 'CambridgeBayWeather (solidly non-human), Uqaqtuq (talk) , Huliva 20:06, 15 July 2024 (UTC) [ reply ] Delete , if not a CSD under G11.  ', 'offensive_label': 'non-offensive', 'score': 0.9054554104804993}]
```

