from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
_ = load_dotenv(find_dotenv())

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
response = client.responses.create(
    model="gpt-5-mini",
    input="Explain machine learning in 3 sentences"
)

print(response.model_dump_json(indent=4))
print(response.output[1].content[0].text)
