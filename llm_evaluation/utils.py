"""
Utility functions for loading puzzles and managing evaluation.
"""

import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'sed-solver' / 'src'))
from schema import Problem


def load_puzzle(puzzle_path: Path) -> Problem:
    """Load a single puzzle from JSON file."""
    return Problem(**json.loads(puzzle_path.read_text()))


def load_puzzles(puzzles_dir: Path) -> List[Problem]:
    """Load all puzzles from a directory."""
    puzzles = []
    for puzzle_file in sorted(puzzles_dir.glob("*.json")):
        try:
            puzzles.append(load_puzzle(puzzle_file))
        except Exception as e:
            print(f"Error loading {puzzle_file}: {e}")
    return puzzles


def load_metadata(metadata_path: Path) -> Dict[str, Dict[str, Any]]:
    """Load metadata JSON file."""
    data = json.loads(metadata_path.read_text())
    return {item['problem_id']: item for item in data}


def select_test_set(
    puzzles: List[Problem],
    metadata: Dict[str, Dict[str, Any]],
    n_easy: int = 8, n_medium: int = 12, n_hard: int = 12, n_expert: int = 8,
    seed: int = 42
) -> List[Problem]:
    """Select a stratified test set by difficulty."""
    random.seed(seed)
    
    by_difficulty = {'easy': [], 'medium': [], 'hard': [], 'expert': []}
    for puzzle in puzzles:
        if puzzle.problem_id in metadata:
            diff = metadata[puzzle.problem_id].get('difficulty_level', 'medium')
            if diff in by_difficulty:
                by_difficulty[diff].append(puzzle)
    
    test_set = []
    targets = {'easy': n_easy, 'medium': n_medium, 'hard': n_hard, 'expert': n_expert}
    
    for difficulty, target in targets.items():
        available = by_difficulty[difficulty]
        sampled = random.sample(available, min(target, len(available)))
        test_set.extend(sampled)
        print(f"Selected {len(sampled)}/{target} {difficulty} puzzles")
    
    return test_set


def select_few_shot_examples(
    puzzles: List[Problem],
    metadata: Dict[str, Dict[str, Any]],
    test_set_ids: set,
    n_examples: int = 5,
    seed: int = 42
) -> List[Dict[str, Any]]:
    """Select diverse examples for few-shot prompting.
    
    IMPORTANT: Includes examples with multi-step swapping, not just deletions.
    This teaches the model that rules can be applied multiple times.
    """
    random.seed(seed)
    solutions_dir = Path(__file__).parent.parent / 'data' / 'solutions'
    
    # Categorize available puzzles by type
    available = [p for p in puzzles if p.problem_id not in test_set_ids and p.problem_id in metadata]
    
    # Prioritize diverse generator types (especially sorting which requires swaps!)
    by_generator = {}
    for puzzle in available:
        gen = metadata[puzzle.problem_id].get('generator', 'unknown')
        if gen not in by_generator:
            by_generator[gen] = []
        by_generator[gen].append(puzzle)
    
    examples = []
    
    # 1. MUST include sorting examples (teaches multi-step swapping)
    sort_puzzles = by_generator.get('sort_3', []) + by_generator.get('sort_4', [])
    for puzzle in sort_puzzles:
        if len(examples) >= 2:  # Include 2 sorting examples
            break
        solution_path = solutions_dir / f"{puzzle.problem_id}.json"
        if solution_path.exists():
            solution_data = json.loads(solution_path.read_text())
            sol = solution_data.get('solution', [])
            # Prefer examples with multiple swaps (solution length > 2)
            if len(sol) >= 3:
                examples.append(_create_example_with_steps(puzzle, solution_data))
                break
    
    # Add one more sorting example with different length
    for puzzle in sort_puzzles:
        if len(examples) >= 2:
            break
        solution_path = solutions_dir / f"{puzzle.problem_id}.json"
        if solution_path.exists():
            solution_data = json.loads(solution_path.read_text())
            sol = solution_data.get('solution', [])
            if len(sol) >= 2 and puzzle.problem_id not in [e.get('problem_id', '') for e in examples]:
                examples.append(_create_example_with_steps(puzzle, solution_data))
    
    # 2. Include examples from other generator types for diversity
    priority_generators = ['concat_2', 'backward_3', 'backward_5', 'multiphase', 'palin_3']
    
    for gen in priority_generators:
        if len(examples) >= n_examples:
            break
        gen_puzzles = by_generator.get(gen, [])
        random.shuffle(gen_puzzles)
        
        for puzzle in gen_puzzles:
            if len(examples) >= n_examples:
                break
            solution_path = solutions_dir / f"{puzzle.problem_id}.json"
            if solution_path.exists():
                solution_data = json.loads(solution_path.read_text())
                examples.append(_create_example_with_steps(puzzle, solution_data))
                break
    
    # 3. Fill remaining slots with any diverse examples
    remaining = [p for p in available if p.problem_id not in [e.get('problem_id', '') for e in examples]]
    random.shuffle(remaining)
    
    for puzzle in remaining:
        if len(examples) >= n_examples:
            break
        solution_path = solutions_dir / f"{puzzle.problem_id}.json"
        if solution_path.exists():
            solution_data = json.loads(solution_path.read_text())
            examples.append(_create_example_with_steps(puzzle, solution_data))
    
    print(f"Selected {len(examples)} few-shot examples:")
    for ex in examples:
        print(f"  - {ex.get('problem_id', '?')}: {ex.get('generator', '?')}, solution={ex.get('solution', [])}")
    
    return examples


def _create_example_with_steps(puzzle: 'Problem', solution_data: Dict) -> Dict[str, Any]:
    """Create a few-shot example with step-by-step trace."""
    solution = solution_data.get('solution', [])
    transitions = [{'src': t.src, 'tgt': t.tgt} for t in puzzle.transitions]
    
    # Generate step-by-step trace
    steps = []
    current = puzzle.initial_string
    for rule_idx in solution:
        if rule_idx < len(transitions):
            src = transitions[rule_idx]['src']
            tgt = transitions[rule_idx]['tgt']
            if src in current:
                new_string = current.replace(src, tgt, 1)
                steps.append(f'"{current}" --rule {rule_idx}--> "{new_string}"')
                current = new_string
    
    return {
        'problem_id': puzzle.problem_id,
        'generator': solution_data.get('generator', 'unknown'),
        'initial_string': puzzle.initial_string,
        'transitions': transitions,
        'solution': solution,
        'steps': steps,  # Include step-by-step trace!
    }


def save_test_set(test_set: List[Problem], output_path: Path):
    """Save test set IDs to file."""
    output_path.write_text(json.dumps([p.problem_id for p in test_set], indent=2))
    print(f"Saved test set ({len(test_set)} puzzles) to {output_path}")
