"""
Main evaluation pipeline for LLM puzzle solving.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

from schema import Problem
from .models import LLMEvaluator
from .prompts import (
    create_zero_shot_prompt, 
    create_few_shot_prompt, 
    create_cot_prompt,
    create_self_verify_prompt,
    create_role_classify_prompt,
)
from .parser import extract_solution, validate_solution_format

# Import solver for verification
import sys
from pathlib import Path as PathLib
project_root = PathLib(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'sed-solver' / 'src'))
try:
    from solver import verify_solution
except ImportError:
    # Fallback: simple verification
    def verify_solution(problem, solution):
        current = problem.initial_string
        for step in solution:
            if step >= len(problem.transitions):
                return False, current
            trans = problem.transitions[step]
            if trans.src not in current:
                return False, current
            current = current.replace(trans.src, trans.tgt, 1)
        return current == "", current

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result of evaluating a single puzzle."""
    problem_id: str
    prompt_type: str
    model_name: str
    prompt: str
    response: str
    parsed_solution: Optional[List[int]]
    is_correct: bool
    error_type: Optional[str]
    final_string: Optional[str]
    timestamp: str
    response_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PuzzleEvaluator:
    """Evaluates LLMs on SED puzzles."""
    
    def __init__(self, evaluator: LLMEvaluator, output_dir: Path = None):
        self.evaluator = evaluator
        self.output_dir = Path(output_dir) if output_dir else Path("results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def evaluate_puzzle(
        self,
        problem: Problem,
        prompt_type: str = "zero_shot",
        few_shot_examples: List[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate a single puzzle.
        
        Args:
            problem: The puzzle to solve
            prompt_type: "zero_shot", "few_shot", or "cot"
            few_shot_examples: Examples for few-shot prompting
            
        Returns:
            EvaluationResult
        """
        # Create prompt based on prompting technique
        if prompt_type == "zero_shot":
            prompt = create_zero_shot_prompt(problem)
        elif prompt_type == "few_shot":
            if not few_shot_examples:
                raise ValueError("few_shot_examples required for few-shot prompting")
            prompt = create_few_shot_prompt(problem, few_shot_examples)
        elif prompt_type == "cot":
            prompt = create_cot_prompt(problem)
        elif prompt_type == "self_verify":
            # Self-Verification: model proposes, simulates, verifies, revises
            prompt = create_self_verify_prompt(problem)
        elif prompt_type == "role_classify":
            # Rule Role Classification: classify rules first, then solve
            prompt = create_role_classify_prompt(problem)
        else:
            raise ValueError(f"Unknown prompt_type: {prompt_type}")
        
        # Generate response
        start_time = time.time()
        result_dict = self.evaluator.solve_puzzle(prompt)
        response_time = time.time() - start_time
        
        response = result_dict.get('response', '')
        error = result_dict.get('error')
        
        # Extract solution
        parsed_solution = None
        is_correct = False
        error_type = None
        final_string = None
        
        if error:
            error_type = "api_error"
        elif response:
            parsed_solution = extract_solution(response, problem.problem_id)
            
            if not validate_solution_format(parsed_solution):
                error_type = "parsing_error"
            else:
                # Verify solution
                is_valid, final = verify_solution(problem, parsed_solution)
                is_correct = is_valid
                final_string = final
                if not is_valid:
                    error_type = "invalid_solution"
        
        return EvaluationResult(
            problem_id=problem.problem_id,
            prompt_type=prompt_type,
            model_name=self.evaluator.model_name,
            prompt=prompt,
            response=response or "",
            parsed_solution=parsed_solution,
            is_correct=is_correct,
            error_type=error_type,
            final_string=final_string,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            response_time=response_time
        )
    
    def batch_evaluate(
        self,
        problems: List[Problem],
        prompt_type: str = "zero_shot",
        few_shot_examples: List[Dict[str, Any]] = None,
        save_results: bool = True
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple puzzles.
        
        Args:
            problems: List of puzzles to evaluate
            prompt_type: Prompting technique to use
            few_shot_examples: Examples for few-shot prompting
            save_results: Whether to save results to disk
            
        Returns:
            List of EvaluationResult
        """
        results = []
        
        for i, problem in enumerate(problems):
            logger.info(f"Evaluating puzzle {i+1}/{len(problems)}: {problem.problem_id}")
            result = self.evaluate_puzzle(problem, prompt_type, few_shot_examples)
            results.append(result)
            
            if save_results:
                self._save_result(result)
        
        return results
    
    def _save_result(self, result: EvaluationResult):
        """Save a single result to disk."""
        # Save solution (if correct)
        if result.is_correct and result.parsed_solution:
            solution_dir = self.output_dir / result.prompt_type / "solutions"
            solution_dir.mkdir(parents=True, exist_ok=True)
            
            solution_file = solution_dir / f"{result.problem_id}.json"
            solution_data = {
                "problem_id": result.problem_id,
                "solution": result.parsed_solution
            }
            solution_file.write_text(json.dumps(solution_data, indent=2))
        
        # Save full log
        log_dir = self.output_dir / result.prompt_type / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{result.problem_id}_{result.model_name.replace('/', '_')}.json"
        log_file.write_text(json.dumps(result.to_dict(), indent=2))
    
    def save_summary(self, results: List[EvaluationResult], filename: str = "summary.json"):
        """Save evaluation summary."""
        summary = {
            "model": self.evaluator.model_name,
            "total_puzzles": len(results),
            "correct": sum(1 for r in results if r.is_correct),
            "accuracy": sum(1 for r in results if r.is_correct) / len(results) if results else 0,
            "parsing_errors": sum(1 for r in results if r.error_type == "parsing_error"),
            "invalid_solutions": sum(1 for r in results if r.error_type == "invalid_solution"),
            "api_errors": sum(1 for r in results if r.error_type == "api_error"),
            "avg_response_time": sum(r.response_time for r in results) / len(results) if results else 0,
            "results": [r.to_dict() for r in results]
        }
        
        summary_file = self.output_dir / filename
        summary_file.write_text(json.dumps(summary, indent=2))
        return summary

