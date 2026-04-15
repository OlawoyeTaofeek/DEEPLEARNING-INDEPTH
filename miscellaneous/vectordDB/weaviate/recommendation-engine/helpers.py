from datasets import load_dataset
from collections.abc import Iterator
from weaviate import WeaviateClient
import weaviate
from enum import Enum
from typing import Dict, List, Optional, Union
from openai import OpenAI
from datetime import datetime, timezone
from utils import Utils
from weaviate.classes.init import Auth, AdditionalConfig, Timeout

openai_api_key, weaviate_api_key, weaviate_url = Utils().get_api_keys_and_url()



class CollectionName(str, Enum):
    '''Enum for weaviate collection name'''

    MOVIES = "Movies"

class CollectionPageSize(int, Enum):
    PAGE_SIZE = 20

    
def connect_to_weaviate() -> WeaviateClient:

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(
            api_key=weaviate_api_key
        ),
    additional_config=AdditionalConfig(
        timeout=Timeout(init=60, query=60, insert=60, stream=20)
    ),
    headers={
         "X-OpenAI-Api-Key": openai_api_key
        }
    )
    if not client.is_ready():
        raise RuntimeError("Weaviate is not ready")

    return client

def process_str_category(raw_string: Union[str, None]) -> Union[List[str], None]:
    if raw_string is None:
        process_data = None 
    else:
        process_data = raw_string.split("-")
    return process_data

def get_data() -> Iterator[Dict]:

    data = load_dataset("wykonos/movies", streaming=True)["train"]

    for movie in data:

        # Handle release date
        if movie["release_date"] is None:
            release_date = None
            year = None
        else:
            release_date = datetime.fromisoformat(movie["release_date"]).replace(tzinfo=timezone.utc)
            year = release_date.year

        yield {
            "properties": {
                "title": movie["title"],
                "original_language": movie["original_language"],
                "overview": movie["overview"],
                "genres": process_str_category(movie["genres"]),
                "keywords": process_str_category(movie["keywords"]),
                "credits": process_str_category(movie["credits"]),
                "movie_id": movie["id"],
                "popularity": movie['popularity'],
                "budget": int(movie["budget"]) if movie["budget"] else 0,
                "revenue": int(movie["revenue"]) if movie["revenue"] else 0,
                "vote_count": int(movie["vote_count"])  if movie["vote_count"] else 0,
                "runtime": int(movie["runtime"])  if movie["runtime"] else 0,
                "vote_average": movie['vote_average'] if movie['vote_average'] else 0,
                "year": year,
            }
        }

def call_openai(prompt: str) -> str:
    client = OpenAI(api_key=openai_api_key)

    response = client.responses.create(
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model= "gpt-4.1",
        stream=True,
        max_output_tokens=2000
    )

    full_text = ""
    for event in response:
        # Only capture text output events
        if event.type == "response.output_text.delta":
            chunk = event.delta
            print(chunk, end="", flush=True)  # streaming output
            full_text += chunk
        elif event.type == "response.completed":
            print("\n\nDone.")

    return full_text


def movie_occasion_to_query(occasion: str) -> str:

    prompt = f"""
    I would like to perform a vector search to find movies best matching this occasion

    ========== OCCASION INPUT FROM USER ==========
    {occasion}
    ========== END INPUT ==========

    What should my search string be?

    IMPORTANT: Only include the search string text in your response and nothing else.
    """
    return call_openai(prompt)   

