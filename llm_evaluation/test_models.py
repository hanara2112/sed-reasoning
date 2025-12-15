"""
Test model availability across multiple providers.
"""

import os
import requests
from pathlib import Path

# Load API keys
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / "api_keys.env"
    load_dotenv(env_file if env_file.exists() else None)
except ImportError:
    pass

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

def test_groq(model_id: str) -> tuple:
    """Test Groq model."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5}
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            return True, r.json()["choices"][0]["message"]["content"][:20]
        error = r.json().get("error", {}).get("message", "")[:50]
        return False, error
    except Exception as e:
        return False, str(e)[:50]

def test_openai(model_id: str) -> tuple:
    """Test OpenAI-compatible endpoint."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 5}
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            return True, r.json()["choices"][0]["message"]["content"][:20]
        return False, r.json().get("error", {}).get("message", "")[:50]
    except Exception as e:
        return False, str(e)[:50]

def main():
    print("=" * 70)
    print("MODEL AVAILABILITY TEST")
    print("=" * 70)
    
    # Test all current Groq models
    groq_models = [
        # From https://console.groq.com/docs/models (Dec 2024)
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama-3.2-1b-preview",
        "llama-3.2-3b-preview", 
        "llama-3.2-11b-vision-preview",
        "llama-3.2-90b-vision-preview",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "compound-beta",
        "compound-beta-mini",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "playai/playai-tts",
        "whisper-large-v3",
        "whisper-large-v3-turbo",
        "distil-whisper-large-v3-en",
    ]
    
    print("\n📦 GROQ MODELS:")
    print("-" * 70)
    working_groq = []
    for model in groq_models:
        print(f"  {model:<45}", end=" ", flush=True)
        ok, msg = test_groq(model)
        if ok:
            print(f"✅ {msg}")
            working_groq.append(model)
        else:
            print(f"❌ {msg[:40]}")
    
    # Test OpenAI models
    openai_models = [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-3.5-turbo",
    ]
    
    print("\n📦 OPENAI MODELS:")
    print("-" * 70)
    working_openai = []
    for model in openai_models:
        print(f"  {model:<45}", end=" ", flush=True)
        ok, msg = test_openai(model)
        if ok:
            print(f"✅ {msg}")
            working_openai.append(model)
        else:
            print(f"❌ {msg[:40]}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ WORKING MODELS FOR EVALUATION:")
    print("=" * 70)
    
    print("\n🆓 FREE (Groq):")
    for m in working_groq:
        if "whisper" not in m and "tts" not in m and "vision" not in m:
            print(f"   - {m}")
    
    print("\n💰 PAID (OpenAI):")
    for m in working_openai:
        print(f"   - {m}")
    
    print()

if __name__ == "__main__":
    main()
