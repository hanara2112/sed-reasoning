"""
Main script to run LLM evaluation on SED puzzles.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import logging

# Load API keys
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / "api_keys.env"
    load_dotenv(env_file if env_file.exists() else None)
except ImportError:
    pass

# Add solver path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'sed-solver' / 'src'))

from schema import Problem
from .models import get_evaluator
from .evaluator import PuzzleEvaluator
from .utils import load_puzzles, load_metadata, select_test_set, select_few_shot_examples, save_test_set
from .metrics import compute_metrics, create_comparison_report
from .config import MODELS, PROMPT_TYPES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_or_create_test_set(puzzles: List[Problem], metadata: Dict, test_set_path: Path, force: bool = False) -> List[Problem]:
    """Load existing test set or create a new one."""
    if test_set_path.exists() and not force:
        logger.info(f"Loading existing test set from {test_set_path}")
        test_ids = set(json.loads(test_set_path.read_text()))
        return [p for p in puzzles if p.problem_id in test_ids]
    
    logger.info("Creating new test set...")
    test_set = select_test_set(puzzles, metadata)
    save_test_set(test_set, test_set_path)
    return test_set


def run_evaluation(models: List[str], prompt_types: List[str], test_set: List[Problem],
                   few_shot_examples: List[Dict], output_dir: Path, max_puzzles: int = None):
    """Run evaluation for multiple models and prompt types."""
    all_results = {}
    
    if max_puzzles:
        test_set = test_set[:max_puzzles]
        logger.info(f"Limited test set to {len(test_set)} puzzles")
    
    for model_key in models:
        if model_key not in MODELS:
            logger.warning(f"Unknown model: {model_key}")
            continue
        
        config = MODELS[model_key]
        api_key = os.getenv(config["api_key_env"])
        
        if not api_key:
            logger.warning(f"No API key for {model_key} ({config['api_key_env']})")
            continue
        
        logger.info(f"\n{'='*80}\nEvaluating: {config['description']}\n{'='*80}\n")
        
        try:
            evaluator = get_evaluator(config["name"], api_key=api_key)
            puzzle_evaluator = PuzzleEvaluator(evaluator, output_dir=output_dir)
            model_results = {}
            
            for prompt_type in prompt_types:
                logger.info(f"\n--- {prompt_type.upper()} PROMPTING ---\n")
                
                results = puzzle_evaluator.batch_evaluate(
                    test_set,
                    prompt_type=prompt_type,
                    few_shot_examples=few_shot_examples if prompt_type == "few_shot" else None,
                    save_results=True
                )
                
                metrics = compute_metrics(results)
                logger.info(f"\n{prompt_type} Results:")
                logger.info(f"  Accuracy: {metrics['accuracy']:.2%}")
                logger.info(f"  Correct: {metrics['correct']}/{metrics['total']}")
                logger.info(f"  Parsing Rate: {metrics['parsing_rate']:.2%}")
                
                puzzle_evaluator.save_summary(results, f"{model_key}_{prompt_type}_summary.json")
                model_results[prompt_type] = results
            
            all_results[model_key] = model_results
        except Exception as e:
            logger.error(f"Error evaluating {model_key}: {e}", exc_info=True)
    
    return all_results


def main():
    parser = argparse.ArgumentParser(description="Evaluate LLMs on SED puzzles")
    parser.add_argument("--models", nargs="+", default=["llama-3.1-8b"], choices=list(MODELS.keys()))
    parser.add_argument("--prompt-types", nargs="+", default=PROMPT_TYPES, choices=PROMPT_TYPES)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent.parent / "data")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent.parent / "results")
    parser.add_argument("--max-puzzles", type=int, default=None)
    parser.add_argument("--recreate-test-set", action="store_true")
    args = parser.parse_args()
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    logger.info("Loading puzzles and metadata...")
    puzzles = load_puzzles(args.data_dir / "puzzles")
    metadata = load_metadata(args.data_dir / "metadata.json")
    logger.info(f"Loaded {len(puzzles)} puzzles")
    
    # Create/load test set
    test_set = load_or_create_test_set(puzzles, metadata, args.output_dir / "test_set.json", args.recreate_test_set)
    
    # Select few-shot examples
    few_shot_examples = select_few_shot_examples(puzzles, metadata, {p.problem_id for p in test_set})
    logger.info(f"Selected {len(few_shot_examples)} few-shot examples")
    
    # Run evaluation
    all_results = run_evaluation(args.models, args.prompt_types, test_set, few_shot_examples, args.output_dir, args.max_puzzles)
    
    # Create comparison reports
    logger.info(f"\n{'='*80}\nCREATING COMPARISON REPORT\n{'='*80}\n")
    
    for prompt_type in args.prompt_types:
        prompt_results = {m: r[prompt_type] for m, r in all_results.items() if prompt_type in r}
        if prompt_results:
            report = create_comparison_report(prompt_results, metadata)
            (args.output_dir / f"comparison_{prompt_type}.txt").write_text(report)
            logger.info(f"\n{report}")
            logger.info(f"\nSaved report to {args.output_dir / f'comparison_{prompt_type}.txt'}")
    
    logger.info("\nEvaluation complete!")


if __name__ == "__main__":
    main()
