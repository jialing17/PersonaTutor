import json

# Agent 1 Question Understanding Agent Data
QU_SYSTEM_PROMPT = """
You are a Question Understanding Agent for a Socratic tutor. 
Your goal is to categorize student input to guide stable instructional decisions.

STRICT CONTEXT RULE:
Always evaluate the 'STUDENT INPUT' in light of the 'RECENT CONTEXT'. 
1. If the input is specific (e.g., "How do I use a for-loop?"), prioritize the input.
2. If the input is vague (e.g., "I don't get it", "Why?", "Yes", "IDK"), you MUST use the RECENT CONTEXT to determine exactly what 'it' or the current topic is.
3. The 'core_issue' should always be a standalone description of the problem (e.g., "Confusion regarding [Topic]").

1. DIFFICULTY CATEGORY (Choose one):
   - Concept: Lack of understanding of definitions, "why," or underlying principles.
   - Procedure: Stuck on a specific execution step (code, math, or derivation).
   - Next-step: Knows the current state but is unsure how to move forward.

2. EMOTION (Choose one):
   - confused, frustrated, joy or neutral.

Return strictly in JSON format. Ensure all string values in the JSON are properly escaped. Do not use unescaped double quotes inside the text fields. Use single quotes if necessary (e.g., 'self').
"""


QU_FEW_SHOT_EXAMPLES = [
    # --- CATEGORY: CONCEPT (Theory, Definitions, "Why") ---
    {"role": "user", "content": "I don't understand why we need to use 'self' in Python classes"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Concept",
        "core_issue": "Fundamental misunderstanding of class instance referencing.",
        "emotion": "neutral",
        "justification": "Student is asking about the 'why' (logic/meaning) behind a programming construct."
    })},
    {"role": "user", "content": "Oh I got it, I see why transformers are better than RNNs for long sentences."},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Concept",
        "core_issue": "None; expressing conceptual breakthrough.",
        "emotion": "joy",
        "justification": "Student explicitly mentions understanding a comparison and expresses positive excitement."
    })},
    {"role": "user", "content": "I'm lost. I don't get the whole idea of 'Recursion'. How can a function call itself?!"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Concept",
        "core_issue": "Lack of conceptual model for recursive call stacks.",
        "emotion": "frustrated",
        "justification": "Expresses 'don't get the idea', indicating a high-level conceptual gap."
    })},
    {"role": "user", "content": "Wait, if the cloud is just someone else's computer, why is it considered more 'scalable'?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Concept",
        "core_issue": "Confusion regarding the abstraction and elasticity of cloud resources.",
        "emotion": "confused",
        "justification": "Questioning the underlying definition and value proposition of a technology."
    })},
    {"role": "user", "content": "What is the actual difference between supervised and unsupervised learning"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Concept",
        "core_issue": "Distinguishing between fundamental machine learning paradigms.",
        "emotion": "neutral",
        "justification": "Seeking a definition and clarification of theoretical principles."
    })},

    # --- CATEGORY: PROCEDURE (Code, Execution, "How-to") ---
    {"role": "user", "content": "It worked! My ChromaDB collection finally initialized without that path error! How should I store documents?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "Uncertainty regarding document storage patterns and methods in ChromaDB.",
        "emotion": "joy",
        "justification": "Student celebrates a procedural success (joy) and immediately asks for the logical next move in the workflow (Next-step)."
    })},
    {"role": "user", "content": "How do I write the loop to iterate through a dictionary in Python?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "Syntax implementation for dictionary iteration.",
        "emotion": "neutral",
        "justification": "Asks 'how to write' a specific piece of code."
    })},
    {"role": "user", "content": "I'm trying to split my PDF into chunks, but the text is coming out as empty strings"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "Debugging PDF parsing failure.",
        "emotion": "frustrated",
        "justification": "Specific execution step is failing technically."
    })},
    {"role": "user", "content": "I'm confused about the syntax for deploying this function to AWS Lambda."},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "Uncertainty regarding deployment CLI/syntax commands for AWS Lambda.",
        "emotion": "confused",
        "justification": "Stuck on the specific 'how-to' steps of a technical task."
    })},
    {"role": "user", "content": "Yes! The SQL query finally returned the right rows after I fixed the JOIN!"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "None; debugging success.",
        "emotion": "joy",
        "justification": "Student reports fixing a specific procedural error with excitement."
    })},

    # --- CATEGORY: NEXT-STEP (Roadmap, Process, "What's next") ---
    {"role": "user", "content": "I've loaded the PDF and split the text. What do I do now?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Lack of workflow roadmap for RAG pipeline.",
        "emotion": "neutral",
        "justification": "Explicitly asks 'what do I do now' after finishing a step."
    })},
    {"role": "user", "content": "I finally got my Docker container to deploy to the cloud! I'm so happy it's live!"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Transitioning from local to cloud environment.",
        "emotion": "joy",
        "justification": "Student celebrates a major deployment milestone and expresses success."
    })},
    {"role": "user", "content": "My agent can analyze the input. Where do I send that analysis so it gets used?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Connecting data flow between agents.",
        "emotion": "confused",
        "justification": "Stuck on the roadmap for connecting separate pieces of logic."
    })},
    {"role": "user", "content": "I'm so frustrated. I finished the data cleaning, but I have no idea what model to try first."},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Indecision regarding the next phase of the ML pipeline.",
        "emotion": "frustrated",
        "justification": "Student is blocked on the 'next step' despite finishing the current one."
    })},
    {"role": "user", "content": "I've set up the S3 bucket. What is the standard next move for setting up permissions?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Seeking the standard sequence for cloud security configuration.",
        "emotion": "neutral",
        "justification": "Student is looking for guidance on the logical sequence of a cloud task."
    })},
    # --- CATEGORY: VAGUE/CONTEXTUAL (Resolving "I don't know") ---
    {
        "role": "user", 
        "content": """Analyze this student input: '''i dont know''' 
        RECENT CONTEXT: [
            {'role': 'user', 'content': 'Why do we need RAG if the LLM already knows things?'}, 
            {'role': 'assistant', 'content': 'Great question! RAG allows the model to look at fresh data. Do you think it helps more with accuracy or with speed?'}
        ]"""
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "difficulty_category": "Concept",
            "core_issue": "Unable to distinguish the primary benefit (accuracy vs. speed) of RAG implementation.",
            "emotion": "confused",
            "justification": "The student is stuck on a specific comparison probe regarding RAG benefits identified in the context."
        })
    },
    {
        "role": "user", 
        "content": """Analyze this student input: '''I have no idea''' 
        RECENT CONTEXT: [
            {'role': 'user', 'content': 'Is the stack or the heap faster?'}, 
            {'role': 'assistant', 'content': 'Think about how they are organized. The stack is a simple contiguous block, while the heap is scattered. Which one do you think the CPU can access more predictably?'}
        ]"""
    },
    {
        "role": "assistant", 
        "content": json.dumps({
            "difficulty_category": "Concept",
            "core_issue": "Seeking clarification on how memory organization (contiguous vs. scattered) affects access speed.",
            "emotion": "neutral",
            "justification": "The student is following up on the tutor's leading question about CPU predictability and memory layout."
        })
    }
]