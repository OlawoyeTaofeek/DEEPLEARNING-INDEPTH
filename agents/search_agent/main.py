from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
import os

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

tavily = TavilyClient()

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
    # return ("Tokyo weather is sunny")
    return tavily.search(query=query)

llm = ChatOpenAI(model="gpt-5")
tools = [search_web] 
agent = create_agent(model=llm, tools=tools)

def main():
    result = agent.invoke({
        "messages": HumanMessage(content="What is the weather in tokyo")      
    })

    print(result)

if __name__ == "__main__":
    main()