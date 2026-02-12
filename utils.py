<<<<<<< HEAD
import re
import json

def safe_json_parse(text):
    try:
        # 1. Strip out DeepSeek <think> tags (if using R1/Reasoning models)
        text = re.sub(r'<think>[\s\S]*?</think>', '', text).strip()
        
        # 2. Remove Markdown code blocks like ```json ... ```
        text = re.sub(r'```json|```', '', text).strip()
        
        # 3. NEW: Remove the stray "json" word that DeepSeek-V3 often adds
        # This looks for "json" at the very start of the string (case insensitive)
        text = re.sub(r'^json\s+', '', text, flags=re.IGNORECASE).strip()

        # 4. FINAL SAFETY: Find the first '{' and last '}' 
        # This ignores any text the AI accidentally put outside the JSON object
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx + 1]

        return json.loads(text)
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"CRITICAL PARSE ERROR: {e}")
=======
import re
import json

def safe_json_parse(text):
    try:
        # 1. Strip out DeepSeek <think> tags (if using R1/Reasoning models)
        text = re.sub(r'<think>[\s\S]*?</think>', '', text).strip()
        
        # 2. Remove Markdown code blocks like ```json ... ```
        text = re.sub(r'```json|```', '', text).strip()
        
        # 3. NEW: Remove the stray "json" word that DeepSeek-V3 often adds
        # This looks for "json" at the very start of the string (case insensitive)
        text = re.sub(r'^json\s+', '', text, flags=re.IGNORECASE).strip()

        # 4. FINAL SAFETY: Find the first '{' and last '}' 
        # This ignores any text the AI accidentally put outside the JSON object
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx + 1]

        return json.loads(text)
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"CRITICAL PARSE ERROR: {e}")
>>>>>>> 6ac9ddb (Initial commit with LFS databases)
        return {"error": "parsing_failed", "raw": text}