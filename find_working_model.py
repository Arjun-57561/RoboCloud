import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")

# Comprehensive list of Groq models
models_to_test = [
    # Llama 3.3
    "llama-3.3-70b-versatile",
    "llama-3.3-70b-specdec",
    
    # Llama 3.1
    "llama-3.1-70b-versatile", 
    "llama-3.1-8b-instant",
    "llama-3.1-70b-specdec",
    
    # Llama 3
    "llama3-70b-8192",
    "llama3-8b-8192",
    "llama3-groq-70b-8192-tool-use-preview",
    "llama3-groq-8b-8192-tool-use-preview",
    
    # Mixtral
    "mixtral-8x7b-32768",
    
    # Gemma
    "gemma-7b-it",
    "gemma2-9b-it",
]

print("🔍 Testing Groq models to find one that works...\n")
working_model = None

for model in models_to_test:
    try:
        print(f"Testing {model}...", end=" ")
        llm = ChatGroq(model=model, api_key=groq_key, temperature=0.1)
        response = llm.invoke("Say OK")
        print(f"✅ WORKS!")
        working_model = model
        break
    except Exception as e:
        error_str = str(e)
        if "model_not_found" in error_str or "does not exist" in error_str:
            print(f"❌ Not available")
        elif "rate_limit" in error_str:
            print(f"⚠️  Rate limited (but model exists)")
            working_model = model
            break
        else:
            print(f"⚠️  Error: {error_str[:80]}")

print("\n" + "="*50)
if working_model:
    print(f"✅ Found working model: {working_model}")
    print(f"\nUpdate agents.py with:")
    print(f'    model="{working_model}",')
else:
    print("❌ No working models found!")
    print("Please check your Groq API key or try a different key.")
print("="*50)
