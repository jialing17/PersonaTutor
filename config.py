# from asyncio.windows_events import NULL
import json
from dotenv import load_dotenv
import streamlit as st
import os



try:
    API_KEY = st.secrets["DEEPSEEK_API_KEY"]
    if not API_KEY:
        raise ValueError("Secret is empty")
    BASE_URL = "https://api.deepseek.com"
    MODEL_NAME = "deepseek-chat" 
except Exception:
    # local host for testing   
    load_dotenv()
    API_KEY = "ollama"
    BASE_URL = "http://localhost:11434/v1"
    MODEL_NAME = "deepseek-v3.2:cloud"


