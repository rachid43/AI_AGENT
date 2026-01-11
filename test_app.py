import os
import tempfile
from embedchain import App
from dotenv import load_dotenv

load_dotenv()

def test_embedchain():
    """Test the core embedchain functionality"""
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False

    print("✅ OpenAI API key found")

    # Initialize app with same config as chat_pdf_openai.py
    db_path = os.path.join(os.getcwd(), "chroma_db")
    os.makedirs(db_path, exist_ok=True)

    print(f"📂 Using database path: {db_path}")

    try:
        app = App.from_config(
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
                "embedder": {"provider": "openai", "config": {"api_key": openai_api_key}}
            }
        )
        print("✅ App initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize app: {e}")
        return False

    # Create a test text file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as f:
        f.write("Python is a high-level programming language. It was created by Guido van Rossum.")
        test_file = f.name

    try:
        print(f"📄 Adding test document: {test_file}")
        app.add(test_file, data_type="text_file")
        print("✅ Document added successfully")
        os.remove(test_file)
    except Exception as e:
        print(f"❌ Failed to add document: {e}")
        os.remove(test_file)
        return False

    # Test querying
    try:
        print("💬 Testing query...")
        response = app.chat("Who created Python?")
        print(f"✅ Query successful!")
        print(f"📝 Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Embedchain with ChromaDB...\n")
    success = test_embedchain()
    print("\n" + "="*50)
    if success:
        print("✅ All tests passed! The app should work correctly.")
    else:
        print("❌ Tests failed. Check the errors above.")
