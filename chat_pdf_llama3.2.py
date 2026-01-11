# Import necessary libraries
import os
import tempfile
import streamlit as st
from embedchain import App
import base64
from streamlit_chat import message
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Define the embedchain_bot function
def embedchain_bot(db_path, openai_api_key):
    return App.from_config(
        config={
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-3.5-turbo",
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

# Add a function to display PDF
def display_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.title("Chat with PDF using GPT-3.5")
st.caption("This app allows you to chat with a PDF using OpenAI's GPT-3.5-turbo for fast, intelligent responses!")

# Initialize session state for messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar for configuration and PDF upload
with st.sidebar:
    st.header("⚙️ Configuration")

    # OpenAI API Key input - check environment variable first
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

    # Initialize app only when API key is provided
    if openai_api_key and 'app' not in st.session_state:
        with st.spinner("Initializing app..."):
            # Use persistent directory for ChromaDB instead of temp directory
            db_path = os.path.join(os.getcwd(), "chroma_db")
            os.makedirs(db_path, exist_ok=True)
            st.session_state.app = embedchain_bot(db_path, openai_api_key)
            st.success("✅ App initialized with GPT-3.5-turbo! Expect 2-3 second response times.")

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

# Chat interface
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

# Clear chat history button
if 'app' in st.session_state:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()