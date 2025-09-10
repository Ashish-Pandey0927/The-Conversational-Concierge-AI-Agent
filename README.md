# Conversational Concierge for Celestial Vines Estate

A conversational AI agent powered by Google Gemini and HuggingFace embeddings.  
Ask about the winery, search the web, get weather updates, or just chat!

---

## Features

- **Conversational Chat**: Friendly responses to greetings and general questions.
- **RAG Pipeline**: Retrieves winery info from local documents.
- **Weather Tool**: Real-time weather for any city.
- **Web Search**: Uses Tavily for up-to-date answers.
- **Powered by Gemini**: Uses Google Gemini for LLM responses.
- **Local Embeddings**: Uses HuggingFace for fast, quota-free document search.

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd Neepi
```

### 2. Create and Activate a Virtual Environment (Recommended)

```sh
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

**If you don’t have a `requirements.txt`, install manually:**

```sh
pip install gradio python-dotenv langchain langchain-google-genai langchain-tavily langchain-community sentence-transformers requests
```

### 4. Add Your API Keys

Create a `.env` file in the project root with:

```
GOOGLE_API_KEY=your-google-gemini-api-key
TAVILY_API_KEY=your-tavily-api-key
OPENWEATHERMAP_API_KEY=your-openweathermap-api-key
```

### 5. Add Winery Info Document

Place your winery info markdown file at:  
`data/wine_business_info.md`

---

## Run the App

```sh
python main.py
```

Open the Gradio link in your browser to chat with the agent.

---

## Example Questions

- "Hi!"
- "Tell me about your Cabernet Sauvignon."
- "What is the weather like in Napa today?"
- "Who was the 16th president of the United States?"

---

## Notes

- HuggingFace embeddings are used for document search (no API quota needed).
- Gemini API key is required for chat responses.
- Weather and web search require their respective API keys.

---

## License

MIT (or
