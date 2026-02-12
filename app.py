import streamlit as st
from database import init_db, verify_user, create_user, get_chat_history, save_chat_message
from agent import QuestionUnderstandingAgent, StudentModelingAgent, StrategyFormulationAgent, QuestionGenerationAgent

@st.cache_resource
def init_agents():
    return (
        QuestionUnderstandingAgent(),
        StudentModelingAgent(),
        StrategyFormulationAgent(),
        QuestionGenerationAgent()
    )

qu_agent, sm_agent, sf_agent, qg_agent = init_agents()

if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# --- 1. GLOBAL INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "username" not in st.session_state:
    st.session_state.username = None

if "current_profile" not in st.session_state:
    st.session_state.current_profile = {"need_more_guidance": "Yes", "mastery_level": 0.0}


# login logic
if st.session_state.username is None:
    st.title("🎓 PersonaTutor")
    st.info("Please login or sign up to continue.")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")
        u_login = st.text_input("Username", key="login_user")
        p_login = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            if verify_user(u_login, p_login):
                st.session_state.username = u_login
                st.session_state.messages = get_chat_history(u_login)
                st.rerun()  # Forces a rerun to move past this if block
            else:
                st.error("Invalid credentials.")

    with tab2:
        st.subheader("Sign Up")
        u_signup = st.text_input("New Username", key="signup_user")
        p_signup = st.text_input("New Password", type="password", key="signup_pwd")
        if st.button("Create Account"):
            if u_signup and p_signup:
                # CALL ONLY ONCE
                success = create_user(u_signup, p_signup)
                if success:
                    st.success("Account created! You can now log in.")
            else:
                st.warning("Please fill in both fields.")
    
    st.stop()

# after login 
st.sidebar.title("Dashboard")
st.sidebar.write(f"👤 **{st.session_state.username}**")

if st.sidebar.button("Logout"):
    st.session_state.username = None # Reset to None
    st.session_state.messages = []
    st.rerun()

st.title("Socratic PersonaTutor")

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Chat Input
if prompt := st.chat_input("Enter your question here..."):
    st.chat_message("user").markdown(prompt)
    
    with st.spinner("PersonaTutor is thinking..."):
        try:
            resultQU = qu_agent.analyze_student_input(prompt, history=st.session_state.messages)
            
            old_profile = st.session_state.current_profile.copy()
            st.session_state.current_profile = sm_agent.update_student_model(
                current_profile_json=old_profile, 
                latest_analysis_json=resultQU
            )
            
            strategy_result = sf_agent.formulate_strategy(resultQU, st.session_state.current_profile)
            
            final_response = qg_agent.generate_grounded_question(
                strategy_result, 
                resultQU.get('core_issue', 'General Concept')
            )

        except Exception as e:
            # display api error when encounter one
            error_msg = f"API error: {str(e)}"
            st.error(error_msg)
            
            # Fallback text so the app doesn't break
            final_response = f"I encountered a connection error. Please try sending your message again. \nError details: {str(e)}" 

    with st.chat_message("assistant"):
        st.markdown(final_response)
    
    # to do save to database
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    
    st.rerun()
