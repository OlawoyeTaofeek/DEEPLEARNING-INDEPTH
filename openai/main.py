from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
_ = load_dotenv(find_dotenv())

api_key = os.getenv("OPENAI_API_KEY")


class ResponsesClient:

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def create_response(
        self,
        model,
        input,
        instructions=None,
        tools=None,
        response_format=None,
        reasoning=None,
        max_tokens=300
    ):

        response = self.client.responses.create(
            model=model,
            input=input,
            instructions=instructions,
            tools=tools,
            response_format=response_format,
            reasoning=reasoning,
            max_output_tokens=max_tokens
        )

        return response