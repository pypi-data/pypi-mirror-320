import tiktoken
from openai import OpenAI
import pandas as pd
import openai
import random
import time

def get_client(openai_key):
    client = OpenAI(api_key=openai_key)
    return client

def num_tokens_from_messages(messages):
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = 0
    for message in messages:
        num_tokens += 4 
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name": 
                num_tokens += -1
    num_tokens += 2 
    return num_tokens

# define a retry decorator
def retry_with_exponential_backoff(
        func,
        initial_delay: float = 1,
        exponential_base: float = 2,
        jitter: bool = True,
        max_retries: int = 10,
        errors: tuple = (openai.RateLimitError,),
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay
        while True:
            try:
                return func(*args, **kwargs)
            except errors as e:
                num_retries += 1
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper

@retry_with_exponential_backoff
def completions_with_backoff(client, **kwargs):
    return client.completions.create(**kwargs)

@retry_with_exponential_backoff
def chat_completions_with_backoff(client, **kwargs):
    return client.chat.completions.create(**kwargs)

def send_to_openai(title, engine, label, text, openai_key=''):
    if engine == '':
        return ''
    client = get_client(openai_key)
    engine = 'gpt-4o-mini'
    if engine == 'gpt-4o-mini':
        token_limit = 16385
    elif engine == 'gpt-4-turbo':
        token_limit = 4000
    elif engine == 'gpt-4':
        token_limit = 8192
    else:
        token_limit = 4096
    
    conversation = [{"role": "system",
                    "content": "You are an AI system that acts as an NLP pipeline."},
                    {"role": "user",
                    "content": f"""Given the following discussion, the outcome of the deletion discussion for the article {title} is: {label}.
                    \nDiscussion: {text}\n
                    \n Please return a brief two sentence explanation for the outcome of the deletion discussion, where you have to justify the reason behind choosing the label. You can use evidence present in the discussion. Do not state the label name or the score in your explanation(like in the start or so), just write the explanation in those two sentences. """   }
                    ]       
    conv_history_tokens = num_tokens_from_messages(conversation)
    max_response_tokens = 200  # min(500, token_limit - conv_history_tokens)
    
    response = chat_completions_with_backoff(client,
                                             model=engine,
                                             messages=conversation,
                                             max_tokens=max_response_tokens,
                                             top_p=1,
                                             temperature=0)
    
    out = response.choices[0].message.content
    return out