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
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Procedure, Issue: 'Python Data Structures - Direct Inquiry (Student is seeking the specific syntax for traversing keys in a dictionary.)', Emotion: neutral"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Neutral emotion but Direct Inquiry on a procedural task indicates the student is at a starting point and needs instruction to proceed.",
            "turn_performance": 0.0, 
            "need_more_guidance": "Yes"
        })
    },
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Next-step, Issue: 'Vector Databases - Procedural Breakthrough (Student resolved initialization errors and is now seeking the next workflow step.)', Emotion: joy"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Positive emotion combined with a 'Breakthrough' status confirms a correct execution/answer; student is ready for the next phase.",
            "turn_performance": 0.2, 
            "need_more_guidance": "No"
        })
    },
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Concept, Issue: 'Recursion Logic - Fundamental Confusion (Student lacks a mental model for how a function can reference itself.)', Emotion: frustrated"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Negative emotion and 'Fundamental Confusion' indicates a 'stuck' state or major misconception that prevents progress.",
            "turn_performance": -0.1, 
            "need_more_guidance": "Yes"
        })
    },
    {
        "role": "user", 
        "content": "ANALYSIS: Category: Concept, Issue: 'SQLite Primary Keys - Partial Understanding (Student identified uniqueness but missed the non-null constraint.)', Emotion: neutral"
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "internal_logic": "Neutral emotion with 'Partial Understanding' suggests minor progress but the student hasn't reached full conceptual mastery yet.",
            "turn_performance": 0.1, 
            "need_more_guidance": "Yes"
        })
    }
]