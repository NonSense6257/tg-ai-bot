from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GROQ_FAST_MODEL = "llama-3.1-8b-instant"     
GROQ_SMART_MODEL = "llama-3.3-70b-versatile" 

GEMINI_MODEL = "gemini-1.5-flash"           

SHORT_CONTEXT_LIMIT = 2000   
MEDIUM_CONTEXT_LIMIT = 8000  

