import os
import tempfile
import streamlit as st
from embedchain import App
import base64
from streamlit_chat import message
from dotenv import load_dotenv

load_dotenv()

def embedchain_bot(db_path, openai_api_key, model="gpt-3.5-turbo"):
    return App.from_config(
        config={
            "llm": {
                "provider": "openai",
                "config": {
                    "model": model,
                    "temperature": 0.5,
                    "max_tokens": 500,
                    "api_key": openai_api_key
                }
            },
            "vectordb": {"provider": "chroma", "config": {"dir": db_path}},
            "embedder": {"provider": "openai", "config": {"api_key": openai_api_key}},
            "cache": {
                "similarity_evaluation": {
                    "strategy": "distance",
                    "max_distance": 0.2
                }
            }
        }
    )

def display_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.title("Chat with PDF using OpenAI")
st.caption("This app allows you to chat with a PDF using OpenAI's models (GPT-3.5-turbo or GPT-4o-mini) for fast, intelligent responses!")

if 'messages' not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("⚙️ Configuration")

    model_choice = st.selectbox(
        "Select Model",
        ["gpt-3.5-turbo", "gpt-4o-mini"],
        help="Choose between GPT-3.5-turbo (faster, cheaper) or GPT-4o-mini (more capable)"
    )

    env_api_key = os.getenv("OPENAI_API_KEY")
    if env_api_key:
        openai_api_key = env_api_key
        st.success("✅ Using OpenAI API key from environment")
    else:
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key for GPT-3.5-turbo and embeddings. Get one at https://platform.openai.com/api-keys"
        )

    if openai_api_key and 'app' not in st.session_state:
        with st.spinner("Initializing app..."):
            db_path = os.path.join(os.getcwd(), "chroma_db")
            os.makedirs(db_path, exist_ok=True)
            st.session_state.app = embedchain_bot(db_path, openai_api_key, model_choice)
            st.success(f"✅ App initialized with {model_choice}! Expect 2-3 second response times.")

    st.divider()
    st.header("📄 PDF Upload")

    if not openai_api_key:
        st.warning("⚠️ Please enter your OpenAI API key above to continue.")
        pdf_file = None
    else:
        pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

    if pdf_file:
        st.subheader("PDF Preview")
        display_pdf(pdf_file)
        
        if st.button("Add to Knowledge Base"):
            with st.spinner("Adding PDF to knowledge base..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                    f.write(pdf_file.getvalue())
                    st.session_state.app.add(f.name, data_type="pdf_file")
                os.remove(f.name)
            st.success(f"Added {pdf_file.name} to knowledge base!")

if 'app' in st.session_state:
    for i, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=msg["role"] == "user", key=str(i))

    if prompt := st.chat_input("Ask a question about the PDF"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        message(prompt, is_user=True)

        with st.spinner("Thinking..."):
            response = st.session_state.app.chat(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            message(response)
else:
    st.info("👈 Please enter your OpenAI API key in the sidebar to start chatting!")

if 'app' in st.session_state:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()