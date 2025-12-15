"""
LLM Model Wrappers - All FREE models.

Supports:
- Groq (compound-beta, llama-3.3-70b, llama-4-scout, llama-3.1-8b)
- Google Gemini 1.5 Flash (free tier)
"""

import os
import time
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Try importing Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LLMEvaluator(ABC):
    """Base class for LLM evaluators."""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 1000)
        self.rate_limit_delay = kwargs.get('rate_limit_delay', 1.0)
        self._last_request_time = 0
        
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
    
    def solve_puzzle(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Solve a puzzle using the LLM."""
        self._rate_limit()
        try:
            response = self.generate(prompt, **kwargs)
            return {'response': response, 'error': None, 'model': self.model_name}
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {'response': None, 'error': str(e), 'model': self.model_name}


class GroqEvaluator(LLMEvaluator):
    """Groq API evaluator - FREE!"""
    
    MODEL_MAP = {
        "compound-beta": "compound-beta",
        "llama-3.3-70b": "llama-3.3-70b-versatile",
        "llama-4-scout": "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.1-8b": "llama-3.1-8b-instant",
    }
    
    def __init__(self, model_name: str = "llama-3.3-70b", api_key: Optional[str] = None, **kwargs):
        api_key = api_key or os.getenv('GROQ_API_KEY', '')
        if not api_key:
            raise ValueError("GROQ_API_KEY required")
        
        groq_model = self.MODEL_MAP.get(model_name, model_name)
        # Groq: 30 req/min = 1 req per 2s, but use 3s for safety margin
        kwargs.setdefault('rate_limit_delay', 3.0)
        
        super().__init__(groq_model, api_key, **kwargs)
        logger.info(f"Initialized Groq model: {groq_model}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get('max_tokens', self.max_tokens),
            "temperature": kwargs.get('temperature', self.temperature),
        }
        
        # compound-beta needs longer timeout (it does multi-step reasoning)
        timeout = 300 if "compound" in self.model_name else 120
        
        for attempt in range(5):  # More retries for rate limits
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=timeout)
                if response.status_code == 429:
                    # Exponential backoff: 60s, 90s, 120s, 150s, 180s
                    wait_time = 60 + (attempt * 30)
                    logger.warning(f"Rate limited, waiting {wait_time}s (attempt {attempt+1}/5)")
                    time.sleep(wait_time)
                    continue
                if response.status_code != 200:
                    error_msg = response.text[:200] if response.text else "No error message"
                    logger.error(f"Groq error {response.status_code}: {error_msg}")
                    raise Exception(f"Groq error {response.status_code}: {error_msg}")
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.Timeout:
                logger.warning(f"Request timed out after {timeout}s (attempt {attempt+1}/5)")
                if attempt < 4:
                    time.sleep(10)
                continue
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error: {e} (attempt {attempt+1}/5)")
                if attempt < 4:
                    time.sleep(10)
                continue
        raise Exception("Failed after 5 retries")


class GeminiEvaluator(LLMEvaluator):
    """Google Gemini evaluator - FREE tier!"""
    
    # Model name mapping (Gemini 1.5 is deprecated, use 2.0+)
    MODEL_MAP = {
        "gemini-1.5-flash": "gemini-2.0-flash",  # 1.5 deprecated, use 2.0
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-flash": "gemini-2.0-flash",
        "gemini-2.5-flash": "gemini-2.5-flash",
    }
    
    def __init__(self, model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None, **kwargs):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
        
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY required")
        
        # Map to actual model name
        actual_model = self.MODEL_MAP.get(model_name, model_name)
        
        kwargs.setdefault('rate_limit_delay', 4.0)  # 15 req/min
        super().__init__(actual_model, api_key, **kwargs)
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(actual_model)
        logger.info(f"Initialized Gemini model: {actual_model}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        for attempt in range(3):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=kwargs.get('temperature', self.temperature),
                        max_output_tokens=kwargs.get('max_tokens', self.max_tokens),
                    )
                )
                return response.text
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    time.sleep(60)
                    continue
                raise
        raise Exception("Failed after 3 retries")


def get_evaluator(model_name: str, api_key: Optional[str] = None, **kwargs) -> LLMEvaluator:
    """Get the appropriate evaluator for a model."""
    name = model_name.lower()
    
    if "gemini" in name:
        return GeminiEvaluator(model_name, api_key, **kwargs)
    else:
        # Default to Groq for all other models
        return GroqEvaluator(model_name, api_key, **kwargs)
