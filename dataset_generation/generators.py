"""
Puzzle generation strategies for SED puzzles.
All generators use backward construction to guarantee solvability.
"""

import random
import string
from typing import List, Tuple, Optional
import sys
from pathlib import Path

# Add sed-solver to path
base_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(base_dir / "sed-solver" / "src"))
from schema import Problem, Transition


def generate_concatenation_puzzle(problem_id: str, num_parts: int = 3) -> Tuple[Problem, List[int]]:
    """Generate puzzle where parts are concatenated and each can be removed."""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    parts = []
    
    for _ in range(num_parts):
        length = random.randint(3, 6)
        part = ''.join(random.choice(alphabet) for _ in range(length))
        parts.append(part)
    
    initial_string = ''.join(parts)
    transitions = [Transition(src=part, tgt="") for part in parts]
    
    # Shuffle transitions
    indices = list(range(len(transitions)))
    random.shuffle(indices)
    shuffled = [transitions[i] for i in indices]
    
    # Compute solution (reverse of construction order)
    reverse_map = {indices[i]: i for i in range(len(indices))}
    solution = [reverse_map[i] for i in range(len(parts))]
    
    problem = Problem(problem_id=problem_id, initial_string=initial_string, transitions=shuffled)
    return problem, solution


def generate_palindrome_puzzle(problem_id: str, half_length: int = 3) -> Tuple[Problem, List[int]]:
    """Generate palindrome checker puzzles using a marker."""
    alphabet = "01"
    left_half = ''.join(random.choice(alphabet) for _ in range(half_length))
    initial_string = left_half + "?" + left_half[::-1]
    
    transitions = [
        Transition(src="?", tgt="!"),      # Convert marker
        Transition(src="0!0", tgt="!"),    # Match 0s
        Transition(src="1!1", tgt="!"),    # Match 1s
        Transition(src="!", tgt=""),       # Remove when done
    ]
    
    problem = Problem(problem_id=problem_id, initial_string=initial_string, transitions=transitions)
    # Solution: convert marker, match pairs, remove marker
    solution = [0]  # Convert ?
    for i in range(half_length):
        if left_half[i] == '0':
            solution.append(1)  # Match 0!0
        else:
            solution.append(2)  # Match 1!1
    solution.append(3)  # Remove !
    
    return problem, solution


def generate_sorting_puzzle(problem_id: str, num_items: int = 3) -> Tuple[Problem, Optional[List[int]]]:
    """Generate bubble-sort style puzzles with guaranteed solution."""
    # Use simpler approach: create a string that can be sorted by swapping
    # We'll use a pattern that's easier to solve
    items = ['.'] * num_items + ['#'] * num_items
    random.shuffle(items)
    initial_string = ''.join(items)
    
    transitions = [
        Transition(src=".#", tgt="#."),  # Swap adjacent
        Transition(src="#" * num_items + "." * num_items, tgt=""),  # Remove when sorted
    ]
    
    # Try to compute solution directly (simple bubble sort)
    # Count how many swaps needed
    solution = []
    current = list(initial_string)
    target = ['.'] * num_items + ['#'] * num_items
    
    # Simple greedy approach: swap .# pairs
    # This is a simplified solution - may not be optimal but should work
    # For now, return None and let BFS solve it (it's usually fast for small puzzles)
    
    problem = Problem(problem_id=problem_id, initial_string=initial_string, transitions=transitions)
    return problem, None


def generate_backward_puzzle(problem_id: str, num_steps: int = 4) -> Tuple[Problem, List[int]]:
    """Build puzzle backwards from empty string - guarantees solvability."""
    alphabet = "ABCDE"
    transitions = []
    solution_steps = []
    current = ""
    
    for step in range(num_steps):
        add_len = random.randint(2, 4)
        addition = ''.join(random.choice(alphabet) for _ in range(add_len))
        
        # Add segment to current string
        if current == "":
            new_string = addition
        else:
            pos = random.choice(['left', 'right'])
            if pos == 'left':
                new_string = addition + current
            else:
                new_string = current + addition
        
        # Create transition to remove this segment
        trans = Transition(src=addition, tgt="")
        transitions.append(trans)
        solution_steps.append(len(transitions) - 1)
        current = new_string
    
    # Add distractor transitions
    num_distractors = random.randint(1, 2)
    for _ in range(num_distractors):
        dist = ''.join(random.choice(alphabet) for _ in range(3))
        if dist not in current:  # Make sure it's a distractor
            transitions.append(Transition(src=dist, tgt=""))
    
    # Shuffle transitions and fix solution indices
    n = len(transitions)
    perm = list(range(n))
    random.shuffle(perm)
    shuffled = [transitions[perm[i]] for i in range(n)]
    
    # Map old indices to new indices
    inv_perm = [0] * n
    for i, p in enumerate(perm):
        inv_perm[p] = i
    
    # Solution is reverse of construction order
    solution = [inv_perm[s] for s in reversed(solution_steps)]
    
    problem = Problem(problem_id=problem_id, initial_string=current, transitions=shuffled)
    return problem, solution


def generate_multiphase_puzzle(problem_id: str) -> Tuple[Problem, Optional[List[int]]]:
    """Puzzles requiring multiple distinct phases to solve."""
    num_as = random.randint(2, 3) * 2  # Even number (reduced from 2-4 to 2-3 for easier solving)
    initial_string = "A" * num_as + "#"
    
    # Create transitions with known indices for solution construction
    transitions = [
        Transition(src="A", tgt="B"),    # Phase 1: Convert A to B
        Transition(src="BB", tgt=""),    # Phase 2: Remove BB pairs
        Transition(src="#", tgt=""),     # Phase 3: Remove marker
        Transition(src="AB", tgt="BA"),  # Distractor
        Transition(src="AA", tgt=""),    # Trap (leads to odd number)
    ]
    
    # Shuffle but track original indices for solution
    indices = list(range(len(transitions)))
    random.shuffle(indices)
    shuffled = [transitions[i] for i in indices]
    
    # Find indices after shuffling
    a_idx = indices.index(0)  # A -> B
    bb_idx = indices.index(1)  # BB -> ""
    hash_idx = indices.index(2)  # # -> ""
    
    # Build solution: convert all A to B, remove BB pairs, remove #
    solution = []
    for _ in range(num_as):
        solution.append(a_idx)
    for _ in range(num_as // 2):
        solution.append(bb_idx)
    solution.append(hash_idx)
    
    problem = Problem(problem_id=problem_id, initial_string=initial_string, transitions=shuffled)
    return problem, solution


def generate_expansion_puzzle(problem_id: str) -> Tuple[Problem, Optional[List[int]]]:
    """Puzzles where string must first expand before contracting."""
    seeds = ["AB", "XY", "PQ"]
    seed = random.choice(seeds)
    
    # Create transitions with known structure
    transitions = [
        Transition(src=seed[0], tgt=seed[0] + "XX"),  # Expand
        Transition(src="XXXX", tgt=""),                # Remove when 4 X's
        Transition(src=seed[1], tgt=""),               # Final removal
        Transition(src="XX", tgt=""),                  # Distractor
    ]
    
    # Shuffle but track indices for solution
    indices = list(range(len(transitions)))
    random.shuffle(indices)
    shuffled = [transitions[i] for i in indices]
    
    # Find indices after shuffling
    expand_idx = indices.index(0)  # seed[0] -> seed[0] + "XX"
    xxxx_idx = indices.index(1)    # XXXX -> ""
    remove_idx = indices.index(2)  # seed[1] -> ""
    
    # Build solution: expand twice to get 4 X's, remove XXXX, remove second char
    solution = [expand_idx, expand_idx, xxxx_idx, remove_idx]
    
    problem = Problem(problem_id=problem_id, initial_string=seed, transitions=shuffled)
    return problem, solution

