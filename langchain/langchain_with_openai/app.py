import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Debug environment
model_name = os.getenv("OLLAMA_MODEL")
st.write(f"Using model: {model_name}")

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("user", "Question: {question}")
    ]
)

# Streamlit UI
st.title("LangChain Demo")
input_text = st.text_input("Ask a question:")

# LLM
llm = ChatOllama(model=model_name)
output_parser = StrOutputParser()

chain = prompt | llm | output_parser

if input_text:
    try:
        response = chain.invoke({"question": input_text})
        st.write(response)
    except Exception as e:
        st.error(f"Error: {e}")