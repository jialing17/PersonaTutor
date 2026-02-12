import json

SM_SYSTEM_PROMPT = """
You are a Student Modeling Agent. Your goal is to determine the student's current need for guidance and estimate their turn_performance based on the ANALYSIS.

1. NEED-MORE-GUIDANCE (Yes/No):
   - Output 'Yes' IF ANY of these are true:
     * Emotion is 'frustrated' or 'confused'.
     * The core issue is a 'stuck' state, procedure error, or misconception.
     * The student explicitly asks for help (hint, definition, etc..).
   
   - Output 'No':
     * Emotion is 'neutral', or 'joy' AND the issue is more towards exploring, testing theories, or providing correct logic.
   
   - PRIORITY: Direct requests for help ('Can you explain?', 'I'm stuck') out 'yes'. ALWAYS override a positive emotion.

2. CALCULATE turn_performance (based on your analysis on ISSUE): 
     - Breakthrough/Correct answer: 0.2
     - Partial progress/Minor step: 0.1
     - Repeating error/Stuck: -0.1

Return strictly in JSON format. Ensure all string values in the JSON are properly escaped. Do not use unescaped double quotes inside the text fields. Use single quotes if necessary (e.g., 'self').
"""

SM_FEW_SHOT_EXAMPLES = [
    # --- CONCEPT: MISUNDERSTANDING ---
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Concept, Issue: 'Fundamental misunderstanding', Emotion: neutral"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Neutral emotion but fundamental misunderstanding indicates a repeating error or significant hurdle.",
            "turn_performance": -0.1, 
            "need_more_guidance": "Yes"
        })
    },

    # --- CONCEPT: BREAKTHROUGH ---
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Concept, Issue: 'Correct answer', Emotion: joy"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Student achieved a correct answer/breakthrough.",
            "turn_performance": 0.2, 
            "need_more_guidance": "No"
        })
    },

    # --- CONCEPT: FRUSTRATED ---
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Concept, Issue: 'Lack of conceptual model', Emotion: frustrated"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Student is frustrated and lacks a model; they are effectively stuck.",
            "turn_performance": -0.1, 
            "need_more_guidance": "Yes"
        })
    },

    # --- PROCEDURE: SUCCESS ---
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Procedure, Issue: 'None; fixed JOIN', Emotion: joy"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Procedural fix suggests a breakthrough or correct implementation step.",
            "turn_performance": 0.2, 
            "need_more_guidance": "No"
        })
    },

# --- PROCEDURE: UNCERTAINTY ---
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Procedure, Issue: 'CLI syntax uncertainty', Emotion: confused"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Confusion/uncertainty on syntax indicates a need for guidance but a minor step is being attempted.",
            "turn_performance": 0.1, 
            "need_more_guidance": "Yes"
        })
    },

    # --- VAGUE/CONFUSED ---
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Concept, Issue: 'Unable to distinguish benefit', Emotion: confused"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Student is unable to distinguish core concepts; indicates a repeating error or roadblock.",
            "turn_performance": -0.1, 
            "need_more_guidance": "Yes"
        })
    },

    # --- NEXT-STEP: UNSURE HOW TO PROCEED ---
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Next-step, Issue: 'Connecting data flow', Emotion: confused"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Making progress on connecting flow is a minor procedural step despite confusion.",
            "turn_performance": 0.1, 
            "need_more_guidance": "Yes"
        })
    }
]