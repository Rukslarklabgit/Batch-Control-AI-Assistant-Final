import os
import google.generativeai as genai
from dotenv import load_dotenv

# ✅ Load the .env file
load_dotenv()

# ✅ Get your API key from environment
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in environment. Check your .env file or hardcode it temporarily.")

# ✅ Configure the SDK with API key
genai.configure(api_key=api_key)

# ✅ List models
models = genai.list_models()
for model in models:
    print(model.name)
