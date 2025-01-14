from wide_analysis.model import policy, outcome, stance, sentiment, offensive

def analyze(
    inp, 
    mode='url', 
    task='outcome', 
    openai_access_token='', 
    explanation=False, 
    lang='en', 
    platform='wikipedia', 
    explainer_model='gpt-4o-mini', 
    date='', 
    years=None,
    model  = ''
):
    if task == 'outcome':
        return outcome.get_outcome(
            input_text_or_url=inp, 
            mode=mode, 
            openai_access_token=openai_access_token, 
            explanation=explanation, 
            lang=lang, 
            platform=platform, 
            explainer_model=explainer_model,
            date=date,
            years=years,
            model = model
        )
    elif task == 'policy':
        return policy.get_policy(inp, mode, platform, model)
    elif task == 'offensive':
        return offensive.get_offensive_label(inp, mode, platform, model)
    elif task == 'sentiment':
        return sentiment.get_sentiment(inp, mode, platform, model)
    elif task == 'stance':
        return stance.get_stance(inp, mode, platform, model)
    else:
        raise ValueError("Invalid task. Choose from ['outcome', 'policy', 'offensive', 'sentiment', 'stance']")




# from wide_analysis.model.policy import get_policy
# from wide_analysis.model.outcome import get_outcome
# from wide_analysis.model.stance import get_stance
# from wide_analysis.model.sentiment import get_sentiment
# from wide_analysis.model.offensive import get_offensive_label

# # def analyze(inp, mode ='', task='', openai_access_token='', explanation=False, lang='en', platform='wikipedia', explainer_model='gpt-4o-mini',date=''):
# #     if task == 'outcome':   
# #         return get_outcome(inp, mode, openai_access_token, explanation, lang, platform, explainer_model,date) #get_outcome(inp, mode, openai_access_token, explanation=explanation)
# #     elif task == 'policy':
# #         return get_policy(inp,mode)
# #     elif task == 'offensive':
# #         return get_offensive_label(inp,mode)
# #     elif task == 'sentiment':
# #         return get_sentiment(inp,mode)
# #     elif task == 'stance':
# #         return get_stance(inp,mode)
# #     else:
# #         raise ValueError("Invalid task. Choose from ['outcome', 'policy', 'offensive', 'sentiment', 'stance']")


# def analyze(inp, mode='url', task='outcome', openai_access_token='', explanation=False, lang='en', platform='wikipedia', explainer_model='gpt-4o-mini', date='', years=None):
#     if task == 'outcome':
#         return get_outcome(
#             input_text_or_url=inp, 
#             mode=mode, 
#             openai_access_token=openai_access_token, 
#             explanation=explanation, 
#             lang=lang, 
#             platform=platform, 
#             explainer_model=explainer_model,
#             date=date,
#             years=years
#         )
#     elif task == 'policy':
#         return get_policy(inp, mode)
#     elif task == 'offensive':
#         return get_offensive_label(inp, mode)
#     elif task == 'sentiment':
#         return get_sentiment(inp, mode)
#     elif task == 'stance':
#         return get_stance(inp, mode)
#     else:
#         raise ValueError("Invalid task. Choose from ['outcome', 'policy', 'offensive', 'sentiment', 'stance']")
