from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langserve import add_routes
import os

load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

model = ChatGroq(model="llama-3.3-70b-versatile")

template = ChatPromptTemplate.from_messages([
    ("system", 
     "Write a beautiful poem in {language} about the given topic. "
     "Then provide a translation of the poem in {language2}. "
     "Format your response clearly with two sections:\n\n"
     "Poem ({language}):\n...\n\n"
     "Translation ({language2}):\n..."
    ),
    ("human", "{input}")
])

parser = StrOutputParser()

# Create chain
chain = template | model | parser

app = FastAPI(
    title="Langchain basic Server",
    version="1.0",
    description="A simple API server using Langchain runnable Interfaces"
) 

# app definitions
add_routes(
    app,
    chain, 
    path="/chain"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)