from dotenv import load_dotenv, find_dotenv
import os
import streamlit as st
import requests
import json
from openai import OpenAI

load_dotenv(find_dotenv())

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
news_api_key = os.getenv("NEWS_API_KEY")
print(news_api_key)


# -----------------------------
# News Function
# -----------------------------
def get_news(topic: str):

    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={news_api_key}&pageSize=5"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])

        final_news = []

        for article in articles:

            final_news.append({
                "title": article["title"],
                "author": article["author"],
                "description": article["description"],
                "url": article["url"]
            })

        return final_news

    return []


# -----------------------------
# Tool Definition
# -----------------------------
tools = [
    {
        "type": "function",
        "name": "get_news",
        "description": "Get latest news based on topic",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic to search news"
                }
            },
            "required": ["topic"]
        }
    }
]


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("📰 News Summarizer (Response API)")

topic = st.text_input("Enter Topic")

if st.button("Get News Summary"):

    response = client.responses.create(
        model="gpt-4.1-mini",
        tools=tools,
        input=f"Get latest news about {topic}"
    )

    tool_call = None

    for item in response.output:
        if item.type == "tool_call":
            tool_call = item
    print(tool_call)
  
    # ----------------------
    # If tool is called
    # ----------------------
    if tool_call:

        arguments = json.loads(tool_call.arguments)

        news_data = get_news(arguments["topic"])
        print(news_data)

        final_response = client.responses.create(
            model="gpt-4.1-mini",
            tools=tools,
            previous_response_id=response.id,
            input=[
                {
                    "type": "function_call_output",
                    "call_id": tool_call.id,
                    "output": json.dumps(news_data)
                }
            ]
        )
        
        st.markdown(final_response.output_text)

    # ----------------------
    # If tool not called
    # ----------------------
    else:

        st.markdown(response.output_text)