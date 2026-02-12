<<<<<<< HEAD
import streamlit as st
import requests

# --- CONNECTION SETUP ---
# Ensure your URL starts with https://
URL = st.secrets.get("TURSO_URL", "").replace("libsql://", "https://")
TOKEN = st.secrets.get("TURSO_AUTH_TOKEN", "")

def query_turso(sql, params=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Updated to ensure all params are treated as strings for the API
    query_body = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql,
                    "args": [{"type": "text", "value": str(p)} for p in params] if params else []
                }
            },
            {"type": "close"}
        ]
    }
    
    try:
        response = requests.post(f"{URL}/v2/pipeline", headers=headers, json=query_body, timeout=10)
        
        if response.status_code != 200:
            st.error(f"HTTP Error {response.status_code}: {response.text}")
            return None
        
        data = response.json()
        
        # DEBUG: Uncomment the line below if you still get "Unknown error"
        # st.write(data) 
        
        return data
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

def init_db():
    query_turso("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    query_turso("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, username TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")

def verify_user(username, password):
    resp = query_turso("SELECT * FROM users WHERE username=? AND password=?", [username, password])
    try:
        # Navigate the new pipeline response structure
        rows = resp["results"][0]["response"]["result"]["rows"]
        return len(rows) > 0
    except (KeyError, IndexError, TypeError):
        return False

def get_chat_history(username):
    resp = query_turso("SELECT role, content FROM history WHERE username=? ORDER BY timestamp ASC", [username])
    try:
        rows = resp["results"][0]["response"]["result"]["rows"]
        # In the pipeline API, values are returned as {'type': 'text', 'value': '...'}
        return [{"role": row[0]["value"], "content": row[1]["value"]} for row in rows]
    except (KeyError, IndexError, TypeError):
        return []

def create_user(username, password):
    resp = query_turso("INSERT INTO users (username, password) VALUES (?, ?)", [username, password])
    
    if not resp or "results" not in resp:
        # If the web request itself failed
        st.error("Connection failed. Please try again.")
        return False

    result = resp["results"][0]
    
    # CASE A: Success
    if result.get("type") == "ok":
        return True
    
    # CASE B: Database Error (like "Username Taken")
    if result.get("type") == "error":
        error_msg = result.get("error", {}).get("message", "")
        if "UNIQUE constraint failed" in error_msg or "already exists" in error_msg.lower():
            st.error("Username already taken.")
        else:
            st.error(f"Database error: {error_msg}")
        return False

    return False

def save_chat_message(username, role, content):
    """Saves a new chat turn to the Turso cloud database."""
    resp = query_turso(
        "INSERT INTO history (username, role, content) VALUES (?, ?, ?)", 
        [username, role, content]
    )
    
    # Optional: Log if the save failed so you can debug in the Streamlit console
    if not resp or resp.get("results", [{}])[0].get("type") != "success":
        print(f"Warning: Failed to save message for {username}")
        return False
    return True

=======
import streamlit as st
import requests

# --- CONNECTION SETUP ---
# Ensure your URL starts with https://
URL = st.secrets.get("TURSO_URL", "").replace("libsql://", "https://")
TOKEN = st.secrets.get("TURSO_AUTH_TOKEN", "")

def query_turso(sql, params=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Updated to ensure all params are treated as strings for the API
    query_body = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql,
                    "args": [{"type": "text", "value": str(p)} for p in params] if params else []
                }
            },
            {"type": "close"}
        ]
    }
    
    try:
        response = requests.post(f"{URL}/v2/pipeline", headers=headers, json=query_body, timeout=10)
        
        if response.status_code != 200:
            st.error(f"HTTP Error {response.status_code}: {response.text}")
            return None
        
        data = response.json()
        
        # DEBUG: Uncomment the line below if you still get "Unknown error"
        # st.write(data) 
        
        return data
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

def init_db():
    query_turso("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    query_turso("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, username TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")

def verify_user(username, password):
    resp = query_turso("SELECT * FROM users WHERE username=? AND password=?", [username, password])
    try:
        # Navigate the new pipeline response structure
        rows = resp["results"][0]["response"]["result"]["rows"]
        return len(rows) > 0
    except (KeyError, IndexError, TypeError):
        return False

def get_chat_history(username):
    resp = query_turso("SELECT role, content FROM history WHERE username=? ORDER BY timestamp ASC", [username])
    try:
        rows = resp["results"][0]["response"]["result"]["rows"]
        # In the pipeline API, values are returned as {'type': 'text', 'value': '...'}
        return [{"role": row[0]["value"], "content": row[1]["value"]} for row in rows]
    except (KeyError, IndexError, TypeError):
        return []

def create_user(username, password):
    resp = query_turso("INSERT INTO users (username, password) VALUES (?, ?)", [username, password])
    
    if not resp or "results" not in resp:
        # If the web request itself failed
        st.error("Connection failed. Please try again.")
        return False

    result = resp["results"][0]
    
    # CASE A: Success
    if result.get("type") == "ok":
        return True
    
    # CASE B: Database Error (like "Username Taken")
    if result.get("type") == "error":
        error_msg = result.get("error", {}).get("message", "")
        if "UNIQUE constraint failed" in error_msg or "already exists" in error_msg.lower():
            st.error("Username already taken.")
        else:
            st.error(f"Database error: {error_msg}")
        return False

    return False

def save_chat_message(username, role, content):
    """Saves a new chat turn to the Turso cloud database."""
    resp = query_turso(
        "INSERT INTO history (username, role, content) VALUES (?, ?, ?)", 
        [username, role, content]
    )
    
    # Optional: Log if the save failed so you can debug in the Streamlit console
    if not resp or resp.get("results", [{}])[0].get("type") != "success":
        print(f"Warning: Failed to save message for {username}")
        return False
    return True

>>>>>>> 6ac9ddb (Initial commit with LFS databases)
