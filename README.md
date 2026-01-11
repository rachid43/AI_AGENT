# Chat with PDF - AI Assistant

## What Does This Do?

This application lets you upload any PDF document and ask questions about it in plain language. Think of it like having a smart assistant who has read your PDF and can answer questions about its contents.

For example:
- Upload a research paper and ask "What were the main findings?"
- Upload a manual and ask "How do I configure the settings?"
- Upload a report and ask "Summarize the key points"

## Recent Improvements

### Major Changes:
1. **Switched to OpenAI GPT Models** - Now uses cloud-based GPT-3.5-turbo or GPT-4o-mini instead of running models locally. This means:
   - Faster responses (2-3 seconds)
   - Better quality answers
   - No need for powerful computer hardware

2. **Improved User Interface** - The main app now has:
   - Modern chat-style interface (like ChatGPT)
   - PDF preview so you can see your document
   - Clear chat history
   - Thinking animation while processing

3. **Model Selection** - You can choose between two AI models:
   - GPT-3.5-turbo (faster, cheaper)
   - GPT-4o-mini (more capable, slightly slower)

4. **Faster Performance** - Added caching system for embeddings, which makes the app respond faster

## Available Apps

There are three versions in this project:

1. **chat_pdf_openai.py** (RECOMMENDED) - Full-featured version with:
   - Chat interface
   - PDF preview
   - Model selection
   - Conversation history
   - Thinking animations

2. **chat_pdf.py** - Simple, basic version for quick use

3. **chat_pdf_llama3.py** - Old version that runs AI locally (slower, but doesn't need API key)

## How to Use

### First Time Setup

1. Install the required software:
   ```bash
   pip install -r requirements.txt
   ```

2. Get an OpenAI API Key:
   - Go to https://platform.openai.com/api-keys
   - Sign up for an account
   - Create a new API key
   - Copy the key

3. Save your API key in a file called `.env`:
   ```
   OPENAI_API_KEY=your-key-here
   ```

### Running the App

1. Open terminal in this folder

2. Run the recommended version:
   ```bash
   streamlit run chat_pdf_openai.py
   ```

3. The app will open in your web browser automatically

4. Enter your OpenAI API key (if you didn't save it in .env)

5. Upload a PDF file

6. Click "Add to Knowledge Base"

7. Start asking questions in the chat box!

### Testing the App

To make sure everything works before uploading PDFs:
```bash
python test_app.py
```

This will test that your API key works and the system is set up correctly.

## What You Need

- Python 3.9 or higher
- An OpenAI API account (costs about $0.01-0.02 per 100 questions)
- Internet connection
- PDF files you want to analyze

## How It Works

1. You upload a PDF
2. The app breaks it into small pieces and stores them in a database
3. When you ask a question, it finds the relevant pieces
4. It sends those pieces to OpenAI's GPT model
5. GPT reads them and writes a natural answer to your question
6. You see the answer in seconds

## Cost

Using OpenAI's API costs money, but it's very affordable:
- About $0.001-0.002 per question
- Processing a PDF: $0.01-0.10 (depending on size)
- For typical use: ~$1-5 per month

## Privacy Note

Your PDF content is sent to OpenAI's servers to generate answers. Don't use this with confidential documents unless you're comfortable with OpenAI's privacy policy.
