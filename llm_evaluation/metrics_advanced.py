"""
Advanced Evaluation Metrics for SED Puzzle LLM Evaluation

This module implements three metrics:
1. Progress-Based Score - How much of the string was reduced
2. Valid Steps Ratio - What % of attempted steps were valid
3. Composite Multi-Metric Score - Weighted combination of multiple factors

Author: Generated for Task 3 - Deriving evaluation metrics
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class MetricResult:
    """Container for all metric scores for a single evaluation."""
    problem_id: str
    model: str
    prompt_type: str
    
    # Binary outcome
    is_correct: bool
    
    # Metric 1: Progress-Based Score
    progress_score: float
    initial_length: int
    final_length: int
    
    # Metric 2: Valid Steps Ratio
    valid_steps_ratio: float
    valid_steps: int
    total_steps: int
    
    # Metric 3: Composite Score
    composite_score: float
    
    # Additional info
    parsed_solution: List[int]
    ground_truth: List[int]
    error_type: Optional[str]
    difficulty: str
    generator: str


def apply_rule(string: str, src: str, tgt: str) -> Tuple[str, bool]:
    """
    Apply a transformation rule to a string.
    Returns (new_string, was_applied).
    """
    if src in string:
        return string.replace(src, tgt, 1), True
    return string, False


def simulate_solution(
    initial_string: str,
    transitions: List[Dict[str, str]],
    solution: List[int]
) -> Tuple[str, int, List[bool]]:
    """
    Simulate applying a solution to a puzzle.
    
    Returns:
        - final_string: The string after applying all valid steps
        - valid_steps: Number of steps that were successfully applied
        - step_validity: List of booleans indicating if each step was valid
    """
    current = initial_string
    step_validity = []
    valid_count = 0
    
    for rule_idx in solution:
        if rule_idx < 0 or rule_idx >= len(transitions):
            step_validity.append(False)
            continue
            
        trans = transitions[rule_idx]
        new_string, was_applied = apply_rule(current, trans['src'], trans['tgt'])
        
        if was_applied:
            current = new_string
            valid_count += 1
            step_validity.append(True)
        else:
            step_validity.append(False)
    
    return current, valid_count, step_validity


def calculate_progress_score(initial_length: int, final_length: int) -> float:
    """
    Calculate progress-based score.
    
    Progress = 1 - (final_length / initial_length)
    
    Score of 1.0 means string was fully reduced to empty.
    Score of 0.0 means no progress was made.
    """
    if initial_length == 0:
        return 1.0  # Already empty
    
    progress = 1.0 - (final_length / initial_length)
    return max(0.0, min(1.0, progress))  # Clamp to [0, 1]


def calculate_valid_steps_ratio(valid_steps: int, total_steps: int) -> float:
    """
    Calculate the ratio of valid steps to total attempted steps.
    
    Valid step = rule index exists AND pattern was found in string.
    """
    if total_steps == 0:
        return 0.0  # No steps attempted
    
    return valid_steps / total_steps


def calculate_composite_score(
    is_correct: bool,
    progress_score: float,
    valid_steps_ratio: float,
    solution_length: int,
    optimal_length: int,
    weights: Dict[str, float] = None
) -> float:
    """
    Calculate composite multi-metric score.
    
    Components:
    - Correctness (binary): Did it reach empty string?
    - Progress: How much of the string was reduced?
    - Validity: What % of steps were valid?
    - Efficiency: How close to optimal solution length? (only for correct solutions)
    
    Default weights:
    - correctness: 0.50 (main goal)
    - progress: 0.25 (partial credit)
    - validity: 0.15 (understanding rules)
    - efficiency: 0.10 (elegance, only for correct)
    """
    if weights is None:
        weights = {
            'correctness': 0.50,
            'progress': 0.25,
            'validity': 0.15,
            'efficiency': 0.10
        }
    
    # Correctness component (binary)
    correctness = 1.0 if is_correct else 0.0
    
    # Efficiency component (only matters if correct)
    if is_correct and solution_length > 0:
        efficiency = min(1.0, optimal_length / solution_length)
    else:
        efficiency = 0.0
    
    # Weighted sum
    composite = (
        weights['correctness'] * correctness +
        weights['progress'] * progress_score +
        weights['validity'] * valid_steps_ratio +
        weights['efficiency'] * efficiency
    )
    
    return composite


def evaluate_single_result(
    result: Dict[str, Any],
    puzzle: Dict[str, Any],
    ground_truth: List[int],
    metadata: Dict[str, Any]
) -> MetricResult:
    """
    Evaluate a single LLM result using all three metrics.
    """
    initial_string = puzzle['initial_string']
    transitions = puzzle['transitions']
    parsed_solution = result.get('parsed_solution', [])
    
    # Handle edge cases
    if parsed_solution is None:
        parsed_solution = []
    
    # Simulate the solution
    final_string, valid_steps, step_validity = simulate_solution(
        initial_string, transitions, parsed_solution
    )
    
    # Calculate metrics
    initial_length = len(initial_string)
    final_length = len(final_string)
    
    progress_score = calculate_progress_score(initial_length, final_length)
    valid_steps_ratio = calculate_valid_steps_ratio(valid_steps, len(parsed_solution))
    
    is_correct = (final_string == "")
    
    composite_score = calculate_composite_score(
        is_correct=is_correct,
        progress_score=progress_score,
        valid_steps_ratio=valid_steps_ratio,
        solution_length=len(parsed_solution),
        optimal_length=len(ground_truth)
    )
    
    return MetricResult(
        problem_id=result.get('problem_id', ''),
        model=result.get('model_name', ''),
        prompt_type=result.get('prompt_type', ''),
        is_correct=is_correct,
        progress_score=progress_score,
        initial_length=initial_length,
        final_length=final_length,
        valid_steps_ratio=valid_steps_ratio,
        valid_steps=valid_steps,
        total_steps=len(parsed_solution),
        composite_score=composite_score,
        parsed_solution=parsed_solution,
        ground_truth=ground_truth,
        error_type=result.get('error_type'),
        difficulty=metadata.get('difficulty_level', 'unknown'),
        generator=metadata.get('generator', 'unknown')
    )


def load_all_data(base_path: Path) -> Tuple[Dict, Dict, Dict]:
    """Load all puzzles, solutions, and metadata."""
    puzzles = {}
    solutions = {}
    
    puzzles_dir = base_path / 'data' / 'puzzles'
    solutions_dir = base_path / 'data' / 'solutions'
    
    for puzzle_file in puzzles_dir.glob('*.json'):
        with open(puzzle_file) as f:
            puzzle = json.load(f)
            puzzles[puzzle['problem_id']] = puzzle
    
    for solution_file in solutions_dir.glob('*.json'):
        with open(solution_file) as f:
            solution = json.load(f)
            solutions[solution['problem_id']] = solution['solution']
    
    with open(base_path / 'data' / 'metadata.json') as f:
        metadata_list = json.load(f)
        metadata = {m['problem_id']: m for m in metadata_list}
    
    return puzzles, solutions, metadata


def evaluate_all_results(base_path: Path) -> List[MetricResult]:
    """
    Evaluate all LLM results using the three metrics.
    """
    puzzles, solutions, metadata = load_all_data(base_path)
    results_dir = base_path / 'results'
    
    all_metrics = []
    
    # Find all summary files
    for summary_file in results_dir.glob('*_summary.json'):
        if 'compound' in summary_file.name:
            continue  # Skip compound-beta
            
        with open(summary_file) as f:
            summary = json.load(f)
        
        for result in summary.get('results', []):
            problem_id = result.get('problem_id')
            
            if problem_id not in puzzles:
                continue
            if problem_id not in solutions:
                continue
            if problem_id not in metadata:
                continue
            
            metric_result = evaluate_single_result(
                result=result,
                puzzle=puzzles[problem_id],
                ground_truth=solutions[problem_id],
                metadata=metadata[problem_id]
            )
            
            all_metrics.append(metric_result)
    
    return all_metrics


def analyze_edge_cases(base_path: Path) -> Dict[str, List[MetricResult]]:
    """
    Identify and categorize edge cases for metric validation.
    """
    all_metrics = evaluate_all_results(base_path)
    
    edge_cases = {
        'correct_optimal': [],      # Correct with optimal length
        'correct_longer': [],       # Correct but longer than optimal
        'almost_there': [],         # Progress > 0.7 but not correct
        'good_progress': [],        # Progress 0.3-0.7
        'minimal_progress': [],     # Progress < 0.3
        'all_valid_wrong': [],      # All steps valid but wrong direction
        'mostly_invalid': [],       # < 50% valid steps
        'parsing_failure': [],      # No solution parsed
        'zero_steps': [],           # Empty solution
    }
    
    for m in all_metrics:
        if m.is_correct:
            if len(m.parsed_solution) <= len(m.ground_truth):
                edge_cases['correct_optimal'].append(m)
            else:
                edge_cases['correct_longer'].append(m)
        else:
            if m.progress_score > 0.7:
                edge_cases['almost_there'].append(m)
            elif m.progress_score >= 0.3:
                edge_cases['good_progress'].append(m)
            else:
                edge_cases['minimal_progress'].append(m)
            
            if m.valid_steps_ratio == 1.0 and m.total_steps > 0:
                edge_cases['all_valid_wrong'].append(m)
            elif m.valid_steps_ratio < 0.5 and m.total_steps > 0:
                edge_cases['mostly_invalid'].append(m)
            
            if m.total_steps == 0:
                edge_cases['zero_steps'].append(m)
    
    return edge_cases


def format_example(m: MetricResult, puzzle: Dict = None) -> str:
    """Format a metric result as a readable example."""
    lines = [
        f"Problem ID: {m.problem_id}",
        f"Model: {m.model}",
        f"Prompt: {m.prompt_type}",
        f"Difficulty: {m.difficulty} | Generator: {m.generator}",
        f"",
        f"Ground Truth Solution: {m.ground_truth}",
        f"LLM Solution: {m.parsed_solution}",
        f"",
        f"Results:",
        f"  Is Correct: {m.is_correct}",
        f"  Initial Length: {m.initial_length} → Final Length: {m.final_length}",
        f"",
        f"METRICS:",
        f"  Progress Score:     {m.progress_score:.3f}",
        f"  Valid Steps Ratio:  {m.valid_steps_ratio:.3f} ({m.valid_steps}/{m.total_steps})",
        f"  Composite Score:    {m.composite_score:.3f}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # Quick test
    base_path = Path(__file__).parent.parent
    all_metrics = evaluate_all_results(base_path)
    
    print(f"Evaluated {len(all_metrics)} results")
    
    # Summary statistics
    progress_scores = [m.progress_score for m in all_metrics]
    valid_ratios = [m.valid_steps_ratio for m in all_metrics]
    composite_scores = [m.composite_score for m in all_metrics]
    
    print(f"\nProgress Score: mean={np.mean(progress_scores):.3f}, std={np.std(progress_scores):.3f}")
    print(f"Valid Ratio: mean={np.mean(valid_ratios):.3f}, std={np.std(valid_ratios):.3f}")
    print(f"Composite Score: mean={np.mean(composite_scores):.3f}, std={np.std(composite_scores):.3f}")

