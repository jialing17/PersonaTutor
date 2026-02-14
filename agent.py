import json
import sqlite3
import os
from datetime import datetime, time
from typing import List
from webbrowser import get
from openai import OpenAI  
from utils import safe_json_parse
from config import API_KEY, BASE_URL, MODEL_NAME
from prompts.QU_PROMPT import QU_SYSTEM_PROMPT, QU_FEW_SHOT_EXAMPLES
from prompts.SF_PROMPT import SF_SYSTEM_PROMPT, SF_FEW_SHOT_EXAMPLES
from prompts.SM_PROMPT import SM_SYSTEM_PROMPT, SM_FEW_SHOT_EXAMPLES
from prompts.QG_PROMPT import QG_SYSTEM_PROMPT
from langchain_community.vectorstores import Chroma
from openai import OpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import warnings
import logging

# to ignore warning message & huggingface messages for RAG part
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3" # Silences TensorFlow if present
import transformers
transformers.utils.logging.set_verbosity_error()

from huggingface_hub import logging as hf_logging
hf_logging.set_verbosity_error()


class QuestionUnderstandingAgent:
    def __init__(self):
        # Ensure these are imported or defined in config.py
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.model = MODEL_NAME # Consistent naming
        self.system_prompt = QU_SYSTEM_PROMPT

    def analyze_student_input(self, student_text: str, history: List[dict]):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(QU_FEW_SHOT_EXAMPLES)

        # messages.append({
        #     "role": "system", 
        #     "content": "--- BEGIN CURRENT SESSION CONTEXT ---"
        # })

        # get last 3 user-agent history 
        # helps the Agent understand "What did I just ask the student?" and "What did they just say back?"
        
        # print(history)
        recent_context = history[-6:] if len(history) >= 4 else history

        # print(recent_context)

        # # to check if the last few-shot and history roles are the same to prevent role confusion when producing result
        # if recent_context and QU_FEW_SHOT_EXAMPLES:
        #     last_few_shot_role = QU_FEW_SHOT_EXAMPLES[-1]["role"]
        #     first_history_role = recent_context[0]["role"]
            
        #     if last_few_shot_role == first_history_role:
        #         # Skip the first history message to maintain alternation
        #         recent_context = recent_context[1:]

        # messages.extend(recent_context)
        
        user_prompt = f"""
        --- RECENT CONTEXT ---
        {json.dumps(recent_context)}
        --- END CONTEXT ---

        --- NEW STUDENT INPUT ---
        Evaluate the following STUDENT INPUT. 
        Refer to the RECENT CONTEXT above if the input is vague.
        STUDENT INPUT: '''{student_text}'''

        Return a JSON with:
        1. "difficulty_category": 'Concept', 'Procedure', or 'Next-step'
        2. "core_issue": A short summary of the specific hurdle. Preferably under 15 words.
        3. "emotion": 'confused', 'frustrated', or 'neutral'

        Do not include justification in the JSON output.
        """

        messages.append({"role": "user", "content": user_prompt})

        response = self.client.chat.completions.create(
            model=self.model, # Use the correct variable name
            messages=messages,
            response_format={"type": "json_object"}
        )

        return safe_json_parse(response.choices[0].message.content)


class StudentModelingAgent:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.model = MODEL_NAME
        self.system_prompt = SM_SYSTEM_PROMPT

    def update_student_model(self, current_profile_json, latest_analysis_json):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(SM_FEW_SHOT_EXAMPLES)

        # 1. Setup initial values
        old_mastery = float(current_profile_json.get('mastery_level', 0.0))
        category = latest_analysis_json.get('difficulty_category', 'Concept')
        emotion = latest_analysis_json.get('emotion', 'neutral')    

        if old_mastery == 0.0:
            # print("initializing mastery based on category...")
            baselines = {"Concept": 0.15, "Procedure": 0.30, "Next-step": 0.60}
            old_mastery = baselines.get(category, 0.15)

        # print(f"\n[StudentModelingAgent] Old Mastery: {old_mastery}, guidance: {current_profile_json.get('need_more_guidance', 'Yes')}, emotion: {emotion}")

        analysis_str = f"Category: {category}, Issue: {latest_analysis_json['core_issue']}, Emotion: {emotion}"
        
        user_prompt = f"""
        ANALYSIS: {analysis_str}

        Please output a JSON object with:
        1. "need_more_guidance": 'Yes' or 'No'.
        2. "turn_performance": A float between -0.2 and 0.2.
        """
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.0,
                timeout=60.0
            )
            content = response.choices[0].message.content.strip()
            
            # clean Markdown wrap 
            if content.startswith("```"):
                content = content.strip("`").replace("json", "", 1).strip()

            # standard return if does not output anything
            if not content:
                return {"need_more_guidance": "Yes", "mastery_level": old_mastery}

            data = json.loads(content)

            turn_perf = float(data.get('turn_performance', 0.5))
            
            emotion_mastery = 0.0             
            if emotion == 'joy':
                emotion_mastery += 0.1
            elif emotion == 'neutral':
                emotion_mastery += 0.05 
            elif emotion == 'confused':
                emotion_mastery -= 0.1  
            elif emotion == 'frustrated':
                emotion_mastery -= 0.2

            current_mastery = old_mastery + turn_perf + emotion_mastery
            clipped_mastery = max(0.0, min(1.0, current_mastery)) # ensure it is always between 0 and 1
            new_mastery = (old_mastery * 0.7) + (clipped_mastery * 0.3)
            final_mastery = max(0.0, min(1.0, new_mastery))

            return {
                "need_more_guidance": data.get("need_more_guidance", "No"),
                "mastery_level": round(final_mastery, 2)
            }

        except Exception as e:
            print(f"API Error in SM Agent: {e}")
            return {"need_more_guidance": "Yes", "mastery_level": old_mastery}
        
class StrategyFormulationAgent:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.model = MODEL_NAME
        self.system_prompt = SF_SYSTEM_PROMPT

    def formulate_strategy(self, analysis_result, student_state):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(SF_FEW_SHOT_EXAMPLES)
        
        analysis_summary = f"mastery_level: {student_state['mastery_level']}, Guidance: {student_state['need_more_guidance']}, difficulty_category: {analysis_result['difficulty_category']},"

        # Simplified context passing
        user_prompt = f"""
        ANALYSIS: {analysis_summary}

        Based on the Strategy Mapping Rules:
        1. Select the 'strategy_type' (Clarification, Reasoning Probe, Step-Probing, Next-step Guidance).
        2. Select the 'instructional_style' (Scaffolded vs Reflective).
        
        Return JSON including: 'strategy_type', 'instructional_style'
        """
        messages.append({"role": "user", "content": user_prompt})

        for attempt in range(3): # Try 3 times
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    timeout=30.0
                )
                return json.loads(response.choices[0].message.content)
            
            except Exception as e:
                if "500" in str(e) and attempt < 2:
                    print(f"  [Server Error] Agent 3 busy. Retrying in {5 * (attempt + 1)}s...")
                    time.sleep(5 * (attempt + 1))
                else:
                    print(f"API error: {e}")
                    # standard return on failure
                    return {"strategy_type": "Clarification", "instructional_style": "Scaffolded"}



class QuestionGenerationAgent:
    def __init__(self, vectorstore_folders=["db_all", "db_ai"]):
        print("Initializing RAG System (Agent 4)...", end=" ", flush=True)
        try:
            # 1. Path Safety for Streamlit Cloud / Linux
            # Find the directory where this script is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 2. Load the embedding model FIRST
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2"
            )

            # 3. Load all vectorstores into a list
            self.vectorstores = []
            for folder in vectorstore_folders:
                full_path = os.path.join(current_dir, folder)
                
                if os.path.exists(full_path):
                    vs = Chroma(
                        persist_directory=full_path, 
                        embedding_function=self.embedding_model
                    )
                    self.vectorstores.append(vs)
                else:
                    print(f"\n[WARNING] Folder not found: {full_path}")
            
            # 4. Setup Client
            self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
            self.model = MODEL_NAME
            
            print(f"[SUCCESS] Loaded {len(self.vectorstores)} databases.")
        except Exception as e:
            print(f"\n[ERROR] Initialization failed: {e}")

    def _retrieve_combined_context(self, query, k_per_db=2):
        """Internal helper to gather context from all loaded databases."""
        all_context_segments = []
        
        for vs in self.vectorstores:
            try:
                # Retrieve top k segments from each database
                docs = vs.similarity_search(query, k=k_per_db)
                for doc in docs:
                    # Optional: Add metadata source to help the LLM
                    source = doc.metadata.get('source', 'Textbook')
                    all_context_segments.append(f"[{source}]: {doc.page_content}")
            except Exception as e:
                print(f"Search failed for a vectorstore: {e}")
                
        return "\n\n".join(all_context_segments)

    def generate_grounded_question(self, strategy_json, core_issue):
        # 1. RAG: Retrieve segments from ALL databases
        context = self._retrieve_combined_context(core_issue)

        # 2. Safety check: If no context found
        if not context.strip():
            context = "No direct textbook reference found. Use general Socratic principles."

        # 3. Prepare Prompt
        user_content = f"""
        ---
        TARGET TOPIC (CORE ISSUE): {core_issue}
        ---
        PEDAGOGICAL STRATEGY: {strategy_json.get('strategy_type', 'Socratic Questioning')}
        REQUIRED STYLE: {strategy_json.get('instructional_style', 'Supportive')}
        ---
        REFERENCE TEXT FROM TEXTBOOK:
        {context}
        ---
        TASK: Based on the pedagogy and textbook reference above, generate a response 
        that guides the student toward solving the CORE ISSUE without giving away the answer.
        """

        # 4. Generate Response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": QG_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3 
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"API Error: {e}"


# for local testing without Streamlit
if __name__ == "__main__":
    # 1. Initialize Agents
    qu_agent = QuestionUnderstandingAgent()
    sm_agent = StudentModelingAgent()
    sf_agent = StrategyFormulationAgent()
    qg_agent = QuestionGenerationAgent()
    
    # 2. Setup Context
    student_id = "user_123" # need login in app, to add password auth later
    current_history = [] # to do use extract from db 
    
    # Mock existing profile (In a real app, fetch this from SQLite)
    # If no profile exists, use an empty dictionary or a default template
    current_profile = {
        "need_more_guidance": "Yes",
        "mastery_level": 0.00
    }
    
    # student_input = (
    #     "Do you mean NLP is part of AI? I thought they were separate fields. "
    #     "Also, I'm really struggling to understand how transformers work. Can you help clarify?"
    # )

    while True:
        student_input = input("Student: ")
        if student_input.lower() in ["exit"]:
            break
        
        print("Thinking...\n")
        # Step 1: Understanding (Uses Raw History)
        resultQU = qu_agent.analyze_student_input(student_input, history=current_history)
        print(f" QU Result: {resultQU}")
        
        # Step 2: Student Modeling (Updates JSON Profile)
        updated_profile = sm_agent.update_student_model(
            current_profile_json=current_profile, 
            latest_analysis_json=resultQU
        )
        print(f" SM Updated Profile: {updated_profile}")
        
        # Step 3: Strategy Formulation
        strategy_result = sf_agent.formulate_strategy(resultQU, updated_profile)
        print(f" SF Strategy: {strategy_result}")

        # Step 4: Generation (The Socratic Response)
        final_response = qg_agent.generate_grounded_question(
            strategy_json=strategy_result, 
            core_issue=resultQU['core_issue']
        )


        # Update History & States
        # Add the current turn to the history for the NEXT interaction
        current_history.append({"role": "user", "content": student_input})
        current_history.append({"role": "assistant", "content": final_response})
        
        # Update current profile for next turn
        current_profile = updated_profile

        # Output and Persistence
        print(f"\nPersonaTutor: {final_response}\n")
        
        # Save both tracks back to SQLite
        # update_database(student_id, current_history, current_profile)

