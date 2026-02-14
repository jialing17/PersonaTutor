import streamlit as st
import requests
import json

URL = st.secrets.get("TURSO_URL", "").replace("libsql://", "https://")
TOKEN = st.secrets.get("TURSO_AUTH_TOKEN", "")

def query_turso(sql, params=None):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # ensure all params are treated as strings for the API
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
        
        # st.write(data) 
        
        return data
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

def init_db():
    query_turso("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    query_turso("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, username TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    query_turso("CREATE INDEX IF NOT EXISTS users_profile ON history(username)")

def verify_user(username, password):
    resp = query_turso("SELECT * FROM users WHERE username=? AND password=?", [username, password])
    try:
        rows = resp["results"][0]["response"]["result"]["rows"]
        return len(rows) > 0
    except (KeyError, IndexError, TypeError):
        return False

def get_chat_history(username):
    resp = query_turso("SELECT role, content FROM history WHERE username=? ORDER BY timestamp ASC", [username])
    try:
        rows = resp["results"][0]["response"]["result"]["rows"]
        return [{"role": row[0]["value"], "content": row[1]["value"]} for row in rows]
    except (KeyError, IndexError, TypeError):
        return []

def create_user(username, password):
    resp = query_turso("INSERT INTO users (username, password) VALUES (?, ?)", [username, password])
    
    if not resp or "results" not in resp:
        # web request itself failed
        st.error("Connection failed. Please try again.")
        return False

    result = resp["results"][0]
    
    # success
    if result.get("type") == "ok":
        return True
    
    if result.get("type") == "error":
        error_msg = result.get("error", {}).get("message", "")
        if "UNIQUE constraint failed" in error_msg or "already exists" in error_msg.lower():
            st.error("Username already taken.")
        else:
            st.error(f"Database error: {error_msg}")
        return False

    return False

def get_next_turn_id(username):
    '''
    turn_id is a simple incrementing integer that tracks the sequence of messages for each user.
    '''
    resp = query_turso(
        "SELECT MAX(turn_id) as max_id FROM history WHERE username = ?",
        [username]
    )
    
    try:
        results = resp.get("results", [])
        if results and results[0].get("response", {}).get("result", {}).get("rows"):
            max_id = results[0]["response"]["result"]["rows"][0][0].get("value")
            if max_id is not None:
                return int(max_id) + 1
    except (IndexError, KeyError, TypeError):
        pass
        
    return 0 # no existing, start with turn_id 0

def save_complete_turn(username, student_input, qu_data, sm_data, sf_data, tutor_output):
    turn_id = get_next_turn_id(username)
    
    sql_statements = [
        # Chat History entries
        ("INSERT INTO history (turn_id, username, role, content) VALUES (?, ?, ?, ?)", 
         [turn_id, username, "user", student_input]),
        ("INSERT INTO history (turn_id, username, role, content) VALUES (?, ?, ?, ?)", 
         [turn_id, username, "assistant", tutor_output]),
        
        # for survey analysis 
        ("INSERT INTO qu_history (turn_id, username, qu_result_json) VALUES (?, ?, ?)", 
         [turn_id, username, json.dumps(qu_data)]),
        ("INSERT INTO sm_history (turn_id, username, sm_result_json) VALUES (?, ?, ?)", 
         [turn_id, username, json.dumps(sm_data)]),
        ("INSERT INTO sf_history (turn_id, username, sf_result_json) VALUES (?, ?, ?)", 
         [turn_id, username, json.dumps(sf_data)]),
         
        # update current profile
        ("INSERT OR REPLACE INTO student_profile (username, current_profile_json) VALUES (?, ?)", 
         [username, json.dumps(sm_data)])
    ]
    
    for sql, params in sql_statements:
        resp = query_turso(sql, params)
        if not resp or resp.get("results", [{}])[0].get("type") == "error":
            print(f"Warning: Failed execution for {username} on statement: {sql}")
            
    return turn_id


def load_chat_history(username):
    # 1 turn = 2 messages (user + assistant)
    resp = query_turso(
        "SELECT role, content FROM history WHERE username = ? ORDER BY turn_id DESC LIMIT 6",
        [username]
    )
    
    try:
        results = resp.get("results", [])
        if results and results[0].get("response", {}).get("result", {}).get("rows"):
            rows = results[0]["response"]["result"]["rows"]
            history = []
            for r in rows:
                history.append({
                    "role": r[0]["value"], 
                    "content": r[1]["value"]
                })
            
            # reverse the list from oldest to newest [User Q1, Tutor A1, User Q2, Tutor A2...]
            return list(reversed(history))
            
    except Exception as e:
        print(f"Error loading history: {e}")
        
    return []

def load_student_profile(username):
    resp = query_turso(
        "SELECT current_profile_json FROM student_profile WHERE username = ?",
        [username]
    )
    try:
        results = resp.get("results", [])
        if results and results[0].get("response", {}).get("result", {}).get("rows"):
            rows = results[0]["response"]["result"]["rows"]
            if rows:
                return json.loads(rows[0][0]["value"])
    except Exception as e:
        print(f"Error loading student profile: {e}")

    # default for new user
    return {"need_more_guidance": "Yes", "mastery_level": 0.00}
