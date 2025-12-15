"""
LLM Evaluation Module for SED Puzzles.
"""

from .models import LLMEvaluator, GroqEvaluator, GeminiEvaluator, get_evaluator
from .prompts import (
    create_zero_shot_prompt, 
    create_few_shot_prompt, 
    create_cot_prompt,
    create_self_verify_prompt,
    create_role_classify_prompt,
)
from .parser import extract_solution
from .evaluator import PuzzleEvaluator, EvaluationResult
from .metrics import compute_metrics, compare_models

__all__ = [
    'LLMEvaluator', 'GroqEvaluator', 'GeminiEvaluator', 'get_evaluator',
    'create_zero_shot_prompt', 'create_few_shot_prompt', 'create_cot_prompt',
    'create_self_verify_prompt', 'create_role_classify_prompt',
    'extract_solution', 'PuzzleEvaluator', 'EvaluationResult',
    'compute_metrics', 'compare_models',
]
