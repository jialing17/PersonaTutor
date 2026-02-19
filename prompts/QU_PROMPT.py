import json

QU_SYSTEM_PROMPT = """
You are a Question Understanding Agent for a Socratic tutor. 
Your goal is to synthesize student input and conversation history into a standalone summary to guide stable instructional decisions.

### STRICT CONTEXT RULES:
1. Always evaluate the 'STUDENT INPUT' in light of the 'RECENT CONTEXT'. 
2. If input is vague (e.g., "Why?", "IDK"), you MUST use 'RECENT CONTEXT' to define the topic.
3. The 'core_issue' MUST be a standalone description that bridges history and current input.

### CORE_ISSUE FORMAT:
"[Broad Topic] - [Contextual Status] ([Brief summary of the whole issue])"

You MUST select exactly ONE of the following for the [Contextual Status]:
- Inquiry: New questions or topics.
- Confusion: Explicit "I don't get it" or repeating errors.
- Partial: Correct logic mixed with errors/logics.
- Breakthrough: Success or fully correct comprehensive answers.
- Others: If it doesn't fit above, use "Others" but still provide a clear summary.

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
        "core_issue": "Object-Oriented Programming - Confusion (Student is questioning the internal mechanics of class instance referencing via 'self'.)",
        "emotion": "neutral",
        "justification": "Student is asking about the 'why' (logic/meaning) behind a programming construct."
    })},
    {"role": "user", "content": "Oh I got it, I see why transformers are better than RNNs for long sentences."},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Concept",
        "core_issue": "Natural Language Processing - Breakthrough (Student has correctly identified the advantage of Transformers over RNNs for long-range dependencies.)",
        "emotion": "joy",
        "justification": "Student explicitly mentions understanding a comparison and expresses positive excitement."
    })},
    {"role": "user", "content": "I'm lost. I don't get the whole idea of 'Recursion'. How can a function call itself?!"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Concept",
        "core_issue": "Algorithmic Logic - Confusion (Student lacks a mental model for how a function can reference itself and manage a call stack.)",
        "emotion": "frustrated",
        "justification": "Expresses 'don't get the idea', indicating a high-level conceptual gap."
    })},
    {"role": "user", "content": "Wait, if the cloud is just someone else's computer, why is it considered more 'scalable'?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Concept",
        "core_issue": "Cloud Computing Infrastructure - Inquiry (Student is questioning the scaling benefits of cloud infrastructure compared to traditional hardware.)",
        "emotion": "confused",
        "justification": "Questioning the underlying definition and value proposition of a technology."
    })},
    {"role": "user", "content": "What is the actual difference between supervised and unsupervised learning"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Concept",
        "core_issue": "Machine Learning - Inquiry (Student is seeking a clear distinction between labeled and unlabeled learning approaches.)",
        "emotion": "neutral",
        "justification": "Seeking a definition and clarification of theoretical principles."
    })},

    # --- CATEGORY: PROCEDURE (Code, Execution, "How-to") ---
    {"role": "user", "content": "It worked! My ChromaDB collection finally initialized without that path error! How should I store documents?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "Databases - Breakthrough (Student resolved initialization errors and is now seeking best practices for the document ingestion workflow.)",
        "emotion": "joy",
        "justification": "Student celebrates a procedural success (joy) and immediately asks for the logical next move in the workflow (Next-step)."
    })},
    {"role": "user", "content": "How do I write the loop to iterate through a dictionary in Python?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "Python Coding - Inquiry (Student is seeking the specific syntax for traversing key-value pairs within a dictionary object.)",
        "emotion": "neutral",
        "justification": "Asks 'how to write' a specific piece of code."
    })},
    {"role": "user", "content": "I'm trying to split my PDF into chunks, but the text is coming out as empty strings"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "Data Preprocessing - Inquiry (Student is struggling with the PDF parsing stage of the RAG pipeline, specifically regarding text extraction.)",
        "emotion": "frustrated",
        "justification": "Specific execution step is failing technically."
    })},
    {"role": "user", "content": "I'm confused about the syntax for deploying this function to AWS Lambda."},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "Cloud Deployment - Confusion (Student understands the goal of hosting a function but is stuck on the specific CLI commands or syntax for AWS.)",
        "emotion": "confused",
        "justification": "Stuck on the specific 'how-to' steps of a technical task."
    })},
    {"role": "user", "content": "Yes! The SQL query finally returned the right rows after I fixed the JOIN!"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Procedure",
        "core_issue": "Relational Databases - Breakthrough (Student successfully implemented a complex JOIN operation to retrieve the correct dataset.)",
        "emotion": "joy",
        "justification": "Student reports fixing a specific procedural error with excitement."
    })},

    # --- CATEGORY: NEXT-STEP (Roadmap, Process, "What's next") ---
    {"role": "user", "content": "I've loaded the PDF and split the text. What do I do now?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Retrieval-Augmented Generation - Inquiry (Student has completed data ingestion and is seeking the next phase of the retrieval-augmented generation sequence.)",
        "emotion": "neutral",
        "justification": "Explicitly asks 'what do I do now' after finishing a step."
    })},
    {"role": "user", "content": "I finally got my Docker container to deploy to the cloud! I'm so happy it's live!"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Cloud Deployment - Breakthrough (Student successfully transitioned from local development to a live cloud environment.)",
        "emotion": "joy",
        "justification": "Student celebrates a major deployment milestone and expresses success."
    })},
    {"role": "user", "content": "My agent can analyze the input. Where do I send that analysis so it gets used?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Multi-Agent Systems - Confusion (Student has established local agent logic but is unsure how to handle the data hand-off between components.)",
        "emotion": "confused",
        "justification": "Stuck on the roadmap for connecting separate pieces of logic."
    })},
    {"role": "user", "content": "I'm so frustrated. I finished the data cleaning, but I have no idea what model to try first."},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Machine Learning Workflow - Partial (Student has completed preprocessing but is blocked by the selection of an appropriate model architecture.)",
        "emotion": "frustrated",
        "justification": "Student is blocked on the 'next step' despite finishing the current one."
    })},
    {"role": "user", "content": "I've set up the S3 bucket. What is the standard next move for setting up permissions?"},
    {"role": "assistant", "content": json.dumps({
        "difficulty_category": "Next-step",
        "core_issue": "Cloud Infrastructure - Partial (Student understands resource creation but is seeking the standard sequence for Identity and Access Management.)",
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
            "core_issue": "Retrieval-Augmented Generation - Confusion (Student is unable to distinguish the primary benefit—accuracy vs. speed—of RAG implementation based on the previous prompt.)",
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
            "core_issue": "Memory Management - Confusion (Student is seeking clarification on how memory organization, specifically contiguous vs. scattered layout, affects CPU access predictability.)",
            "emotion": "neutral",
            "justification": "The student is following up on the tutor's leading question about CPU predictability and memory layout."
        })
    }
]