from dotenv import find_dotenv, load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from pydantic import BaseModel, Field
from typing import List 
from langchain_tavily import TavilySearch
import json
import os

load_dotenv("C:/Users/user/Documents/DeepLearning-Indepth/agents/search_agent/.env")

tavily = TavilySearch(tavily_api_key=os.getenv("TAVILY_API_KEY"))

class Source(BaseModel):
    """Schema for a source used by the agent"""
    url: str = Field(description="The URL of the source")


class AgentResponse(BaseModel):
    """Schema for agent response with answer and sources"""
    answer: str = Field(description="The agent's answer to the query")
    sources: List[Source] = Field(
        default_factory=list,
        description="List of sources used to generate the answer"
    )


@tool
def search_web(query: str) -> str:
    """
    A real time search agent

    Args: 
        query: The quesy to search for
    Returns:
        The search result
    """
    print(f"Searching for {query}")
    result = tavily.invoke(query)
    return str(result)

llm = ChatOpenAI(model="gpt-5")
tools = [search_web] 
agent = create_agent(
    model=llm, 
    tools=tools, 
    response_format=AgentResponse
)


def main():
    print("Hello from langchain-course!")
    result = agent.invoke(
        {
            "messages": HumanMessage(
                content="search for 3 job postings for an ai engineer using langchain in the Nigeria on linkedin and 3 from Glassdoor and list their details?"
            )
        }
    )
    print(result)
    print(json.dumps(result.get("answer"), indent=4))


if __name__ == "__main__":
    main()