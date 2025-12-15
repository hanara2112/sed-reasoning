"""
Difficulty metrics and analysis for SED puzzles.
"""

from dataclasses import dataclass
from typing import List, Set
from schema import Problem
from solver import solve_bfs


@dataclass
class DifficultyMetrics:
    """Metrics for analyzing puzzle difficulty."""
    solution_length: int = 0
    branching_factor: float = 0.0
    initial_string_length: int = 0
    num_transitions: int = 0
    num_distractors: int = 0
    max_intermediate_length: int = 0
    has_expansion: bool = False
    
    def compute_difficulty_score(self) -> float:
        """Compute overall difficulty score (0-100)."""
        score = 0
        score += min(30, self.solution_length * 3)      # Solution length (0-30)
        score += min(25, self.branching_factor * 5)     # Branching (0-25)
        score += min(20, self.initial_string_length * 0.5)  # String length (0-20)
        score += min(15, self.num_distractors * 3)      # Distractors (0-15)
        if self.has_expansion:
            score += 10                                   # Expansion bonus
        return min(100, score)
    
    def difficulty_level(self) -> str:
        """Get difficulty level based on score."""
        score = self.compute_difficulty_score()
        if score < 25:
            return "easy"
        elif score < 50:
            return "medium"
        elif score < 75:
            return "hard"
        else:
            return "expert"
    
    def compute_quality_score(self) -> float:
        """Compute quality score for puzzle curation (0-100).
        
        Higher score = better puzzle quality.
        Considers:
        - Non-trivial solution (not too short, not too long)
        - Good use of transitions (not all transitions used)
        - Reasonable complexity
        - Educational value
        """
        score = 50.0  # Base score
        
        # Solution length bonus (sweet spot: 2-7 steps)
        if 2 <= self.solution_length <= 7:
            score += 20
        elif self.solution_length == 1:
            score -= 10  # Too trivial
        elif self.solution_length > 10:
            score -= 5  # Too long
        
        # Distractor usage (having some distractors is good)
        if 1 <= self.num_distractors <= 3:
            score += 15
        elif self.num_distractors == 0:
            score -= 5  # No distractors = too easy
        
        # Transition diversity (using most but not all transitions)
        transition_usage = (self.num_transitions - self.num_distractors) / max(1, self.num_transitions)
        if 0.4 <= transition_usage <= 0.8:
            score += 10
        
        # Complexity balance
        if 1.5 <= self.branching_factor <= 3.0:
            score += 10
        
        # Expansion bonus (interesting puzzles)
        if self.has_expansion:
            score += 5
        
        return max(0, min(100, score))


def analyze_difficulty(problem: Problem, solution: List[int]) -> DifficultyMetrics:
    """Analyze the difficulty of a puzzle given its solution."""
    metrics = DifficultyMetrics()
    metrics.solution_length = len(solution)
    metrics.initial_string_length = len(problem.initial_string)
    metrics.num_transitions = len(problem.transitions)
    metrics.num_distractors = len(problem.transitions) - len(set(solution))
    
    current = problem.initial_string
    max_length = len(current)
    total_choices = 0
    
    for step in solution:
        applicable = sum(1 for t in problem.transitions if t.src in current)
        total_choices += applicable
        trans = problem.transitions[step]
        current = current.replace(trans.src, trans.tgt, 1)
        max_length = max(max_length, len(current))
    
    metrics.branching_factor = total_choices / len(solution) if solution else 0
    metrics.max_intermediate_length = max_length
    metrics.has_expansion = max_length > metrics.initial_string_length
    return metrics


def check_solution_uniqueness(problem: Problem, known_solution: List[int], 
                              max_attempts: int = 5) -> bool:
    """Check if puzzle has multiple solutions.
    
    Returns True if likely unique, False if multiple solutions found.
    """
    # Try to find alternative solutions by solving with different approach
    # This is a heuristic - we try a few times with different search orders
    solutions_found = {tuple(known_solution)}
    
    # Try solving with limited attempts
    for _ in range(max_attempts):
        alt_solution = solve_bfs(problem, time_limit=5.0)
        if alt_solution and tuple(alt_solution) != tuple(known_solution):
            return False  # Found different solution
    
    return True  # Likely unique


def is_trivial_puzzle(problem: Problem, solution: List[int]) -> bool:
    """Check if puzzle is too trivial."""
    # Trivial if:
    # 1. Solution is only 1 step
    # 2. No distractors and solution uses all transitions
    # 3. String is very short (< 4 chars) and solution is 1 step
    if len(solution) == 1 and len(problem.initial_string) < 4:
        return True
    if len(solution) == 1 and len(problem.transitions) == 1:
        return True
    return False

