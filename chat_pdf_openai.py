import os
import tempfile
import streamlit as st
from embedchain import App
import base64
from dotenv import load_dotenv
import time

# Must be the first Streamlit command
st.set_page_config(page_title="Chat with PDF", page_icon="📄", layout="wide")

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
            "embedder": {"provider": "openai", "config": {"api_key": openai_api_key}}
        }
    )

def display_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Custom CSS for thinking dots animation
st.markdown("""
    <style>
    .thinking-dots {
        display: inline-block;
        font-size: 24px;
        animation: thinking 1.4s infinite;
    }

    .thinking-dots::after {
        content: '...';
        animation: dots 1.4s steps(4, end) infinite;
    }

    @keyframes dots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60%, 100% { content: '...'; }
    }

    /* Improve chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 Chat with PDF using OpenAI")
st.caption("Ask questions about your PDF documents using GPT-3.5-turbo or GPT-4o-mini for fast, intelligent responses!")

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
    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("💭 Ask a question about your PDF..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Show thinking animation and get response
        with st.chat_message("assistant", avatar="🤖"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown('<div class="thinking-dots">Thinking</div>', unsafe_allow_html=True)

            response = st.session_state.app.chat(prompt)

            thinking_placeholder.empty()
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("👈 Please enter your OpenAI API key in the sidebar to start chatting!")

if 'app' in st.session_state:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()