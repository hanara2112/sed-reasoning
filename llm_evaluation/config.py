"""
Configuration for LLM evaluation.
All models are FREE!
"""

# Available models
MODELS = {
    # Groq API (FREE - 30 req/min, 14,400 req/day)
    "compound-beta": {
        "name": "compound-beta",
        "api_key_env": "GROQ_API_KEY",
        "description": "Groq Compound Beta (FREE) - Best for reasoning",
    },
    "llama-3.3-70b": {
        "name": "llama-3.3-70b",
        "api_key_env": "GROQ_API_KEY",
        "description": "Meta Llama 3.3 70B (FREE) - Fast & accurate",
    },
    "llama-4-scout": {
        "name": "llama-4-scout",
        "api_key_env": "GROQ_API_KEY",
        "description": "Meta Llama 4 Scout 17B (FREE) - Newest",
    },
    "llama-3.1-8b": {
        "name": "llama-3.1-8b",
        "api_key_env": "GROQ_API_KEY",
        "description": "Meta Llama 3.1 8B (FREE) - Fastest",
    },
    # Google Gemini (FREE tier - 15 req/min, uses gemini-2.0-flash)
    "gemini-1.5-flash": {
        "name": "gemini-1.5-flash",
        "api_key_env": "GEMINI_API_KEY",
        "description": "Google Gemini 2.0 Flash (FREE) - Uses latest version",
    },
}

# Default models
DEFAULT_MODELS = ["compound-beta", "llama-3.3-70b"]

# Prompting techniques
PROMPT_TYPES = [
    "zero_shot",      # Basic: no examples, just instructions
    "few_shot",       # Provide solved examples
    "cot",            # Chain-of-Thought: step-by-step reasoning
    "self_verify",    # Self-Verification: propose, simulate, verify, revise
    "role_classify",  # Rule Role Classification: classify rules first, then solve
]

# Test set configuration
TEST_SET_CONFIG = {
    "n_easy": 8,
    "n_medium": 12,
    "n_hard": 12,
    "n_expert": 8,
    "seed": 42,
}

# Few-shot configuration
FEW_SHOT_CONFIG = {
    "n_examples": 5,
    "seed": 42,
}
