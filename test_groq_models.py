import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

# List of potential Groq models to test
models_to_test = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
    "gemma2-9b-it",
]

print("Testing Groq models...\n")

for model in models_to_test:
    try:
        llm = ChatGroq(model=model, api_key=groq_key, temperature=0.1)
        response = llm.invoke("Say 'OK'")
        print(f"✅ {model} - WORKS!")
        break  # Found a working model
    except Exception as e:
        if "model_not_found" in str(e) or "does not exist" in str(e):
            print(f"❌ {model} - Not available")
        else:
            print(f"⚠️  {model} - Error: {str(e)[:100]}")

print("\nDone!")
