import os
import tempfile
import streamlit as st
from embedchain import App

def embedchain_bot(db_path):
    return App.from_config(
        config={
            "llm": {"provider": "ollama", "config": {"model": "llama3:instruct", "max_tokens": 250, "temperature": 0.5, "stream": True, "base_url": 'http://localhost:11434'}},
            "vectordb": {"provider": "chroma", "config": {"dir": db_path}},
            "embedder": {"provider": "ollama", "config": {"model": "llama3:instruct", "base_url": 'http://localhost:11434'}},
        }
    )

st.title("Chat with PDF")
st.caption("This app allows you to chat with a PDF using Llama3 running locally with Ollama!")

db_path = tempfile.mkdtemp()
app = embedchain_bot(db_path)

pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

if pdf_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(pdf_file.getvalue())
        app.add(f.name, data_type="pdf_file")
    os.remove(f.name)
    st.success(f"Added {pdf_file.name} to knowledge base!")

prompt = st.text_input("Ask a question about the PDF")
if prompt:
    answer = app.chat(prompt)
    st.write(answer)