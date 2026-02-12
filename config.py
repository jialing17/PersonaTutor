# from asyncio.windows_events import NULL
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Change these for the official DeepSeek API
API_KEY = "ollama"  # local testing
BASE_URL = "http://localhost:11434/v1"  # Local Ollama Proxy

# to use the below lines for real deepseek api
# API_KEY = os.getenv("DEEPSEEK_API_KEY") 
# BASE_URL = "https://api.deepseek.com"

# Global Settings
MODEL_NAME = "deepseek-v3.2:cloud"





