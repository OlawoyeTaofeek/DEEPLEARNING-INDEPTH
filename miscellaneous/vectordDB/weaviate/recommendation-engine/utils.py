import os
from dotenv import load_dotenv, find_dotenv

class Utils:

    def __init__(self):
        pass

    def get_api_keys_and_url(self):
        _ = load_dotenv(find_dotenv(), override=True)
        openai_api_key = os.environ['OPENAI_KEY']
        weaviate_api_key = os.environ['WEAVIATE_API_KEY']
        weaviate_url = os.environ['WEAVIATE_URL']

        return openai_api_key, weaviate_api_key, weaviate_url

        