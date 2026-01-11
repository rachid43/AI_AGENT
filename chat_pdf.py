import os
import tempfile
import streamlit as st
from embedchain import App

def embedchain_bot(db_path, api_key):
    return App.from_config(
        config={
            "llm": {"provider": "openai", "config": {"api_key": api_key}},
            "vectordb": {"provider": "chroma", "config": {"dir": db_path}},
            "embedder": {"provider": "openai", "config": {"api_key": api_key}},
        }
    )

st.title("Chat with PDF")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "reset_prompt" not in st.session_state:
    st.session_state.reset_prompt = False

openai_access_token = st.text_input("OpenAI API Key", type="password")

if openai_access_token:
    db_path = tempfile.mkdtemp()
    app = embedchain_bot(db_path, openai_access_token)

    pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

    if pdf_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(pdf_file.getvalue())
            app.add(f.name, data_type="pdf_file")
        os.remove(f.name)
        st.success(f"Added {pdf_file.name} to knowledge base!")

    if st.session_state.reset_prompt:
        # Reset the question input before the widget renders again.
        st.session_state.prompt_input = ""
        st.session_state.reset_prompt = False

    if st.session_state.chat_history:
        st.subheader("Conversation history")
        for entry in st.session_state.chat_history:
            st.markdown(f"**Q:** {entry['question']}")
            st.markdown(f"**A:** {entry['answer']}")

    prompt = st.text_input("Ask a question about the PDF", key="prompt_input")
    ask_pressed = st.button("Ask")

    if ask_pressed and prompt:
        answer = app.chat(prompt)
        st.session_state.chat_history.append({"question": prompt, "answer": answer})
        st.write(answer)
        st.session_state.reset_prompt = True

        
