"""
Metrics computation and model comparison.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
import pandas as pd
from .evaluator import EvaluationResult


def compute_metrics(results: List[EvaluationResult]) -> Dict[str, Any]:
    """
    Compute evaluation metrics from results.
    
    Returns:
        Dictionary with metrics
    """
    if not results:
        return {}
    
    total = len(results)
    correct = sum(1 for r in results if r.is_correct)
    accuracy = correct / total if total > 0 else 0
    
    # Error breakdown
    error_counts = defaultdict(int)
    for r in results:
        if r.error_type:
            error_counts[r.error_type] += 1
    
    # Parsing success
    parsed = sum(1 for r in results if r.parsed_solution is not None)
    parsing_rate = parsed / total if total > 0 else 0
    
    # Response time
    response_times = [r.response_time for r in results if r.response_time]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    return {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "parsing_rate": parsing_rate,
        "error_breakdown": dict(error_counts),
        "avg_response_time": avg_response_time,
        "min_response_time": min(response_times) if response_times else 0,
        "max_response_time": max(response_times) if response_times else 0,
    }


def compute_metrics_by_difficulty(
    results: List[EvaluationResult],
    metadata: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """Compute metrics broken down by difficulty level."""
    by_difficulty = defaultdict(list)
    
    for r in results:
        if r.problem_id in metadata:
            difficulty = metadata[r.problem_id].get('difficulty_level', 'unknown')
            by_difficulty[difficulty].append(r)
    
    metrics_by_difficulty = {}
    for difficulty, difficulty_results in by_difficulty.items():
        metrics_by_difficulty[difficulty] = compute_metrics(difficulty_results)
    
    return metrics_by_difficulty


def compute_metrics_by_generator(
    results: List[EvaluationResult],
    metadata: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """Compute metrics broken down by generator type."""
    by_generator = defaultdict(list)
    
    for r in results:
        if r.problem_id in metadata:
            generator = metadata[r.problem_id].get('generator', 'unknown')
            by_generator[generator].append(r)
    
    metrics_by_generator = {}
    for generator, generator_results in by_generator.items():
        metrics_by_generator[generator] = compute_metrics(generator_results)
    
    return metrics_by_generator


def compare_models(
    all_results: Dict[str, List[EvaluationResult]],
    metadata: Optional[Dict[str, Dict[str, Any]]] = None
) -> pd.DataFrame:
    """
    Compare multiple models across different metrics.
    
    Args:
        all_results: Dict mapping model_name -> list of EvaluationResult
        metadata: Optional metadata for per-difficulty/generator analysis
        
    Returns:
        DataFrame with comparison metrics
    """
    comparison_data = []
    
    for model_name, results in all_results.items():
        metrics = compute_metrics(results)
        
        row = {
            "model": model_name,
            "accuracy": metrics["accuracy"],
            "total": metrics["total"],
            "correct": metrics["correct"],
            "parsing_rate": metrics["parsing_rate"],
            "avg_response_time": metrics["avg_response_time"],
        }
        
        # Add error breakdown
        for error_type, count in metrics["error_breakdown"].items():
            row[f"error_{error_type}"] = count
        
        comparison_data.append(row)
    
    df = pd.DataFrame(comparison_data)
    
    # Add per-difficulty metrics if metadata available
    if metadata:
        for model_name, results in all_results.items():
            difficulty_metrics = compute_metrics_by_difficulty(results, metadata)
            for difficulty, metrics in difficulty_metrics.items():
                col_name = f"accuracy_{difficulty}"
                if col_name not in df.columns:
                    df[col_name] = 0.0
                df.loc[df["model"] == model_name, col_name] = metrics["accuracy"]
    
    return df


def create_comparison_report(
    all_results: Dict[str, List[EvaluationResult]],
    metadata: Optional[Dict[str, Dict[str, Any]]] = None
) -> str:
    """Create a text report comparing models."""
    df = compare_models(all_results, metadata)
    
    report = "=" * 80 + "\n"
    report += "MODEL COMPARISON REPORT\n"
    report += "=" * 80 + "\n\n"
    
    # Overall accuracy
    report += "Overall Accuracy:\n"
    report += "-" * 80 + "\n"
    for _, row in df.iterrows():
        report += f"{row['model']:<30} {row['accuracy']:.2%} ({row['correct']}/{row['total']})\n"
    report += "\n"
    
    # Per-difficulty if available
    if metadata:
        difficulty_cols = [c for c in df.columns if c.startswith('accuracy_')]
        if difficulty_cols:
            report += "Accuracy by Difficulty:\n"
            report += "-" * 80 + "\n"
            for _, row in df.iterrows():
                report += f"\n{row['model']}:\n"
                for col in difficulty_cols:
                    difficulty = col.replace('accuracy_', '')
                    acc = row[col]
                    report += f"  {difficulty:<10} {acc:.2%}\n"
            report += "\n"
    
    # Error breakdown
    report += "Error Breakdown:\n"
    report += "-" * 80 + "\n"
    error_cols = [c for c in df.columns if c.startswith('error_')]
    for _, row in df.iterrows():
        report += f"\n{row['model']}:\n"
        for col in error_cols:
            error_type = col.replace('error_', '')
            count = row[col] if pd.notna(row[col]) else 0
            if count > 0:
                report += f"  {error_type:<20} {count}\n"
    report += "\n"
    
    # Response times
    report += "Average Response Time:\n"
    report += "-" * 80 + "\n"
    for _, row in df.iterrows():
        report += f"{row['model']:<30} {row['avg_response_time']:.2f}s\n"
    report += "\n"
    
    report += "=" * 80 + "\n"
    
    return report

