import os
from dotenv import load_dotenv

load_dotenv()

# Essential configuration variables loaded from the environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
WEBAPP_URL = os.getenv("WEBAPP_URL")

if not WEBAPP_URL:
    WEBAPP_URL = API_BASE_URL

print(f"DEBUG: WEBAPP_URL loaded as: '{WEBAPP_URL}'")

if not BOT_TOKEN:
    print("WARNING: BOT_TOKEN is not set in environment variables.")