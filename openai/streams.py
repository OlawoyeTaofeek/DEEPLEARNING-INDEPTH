from openai import OpenAI
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with client.responses.stream(
    model="gpt-4.1-mini",
    input="Explain Python loops in simple terms"
) as stream:

    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta)