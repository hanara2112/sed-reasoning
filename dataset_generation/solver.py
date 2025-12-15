"""
BFS solver and solution verification for SED puzzles.
"""

import time
from collections import deque
from typing import List, Optional, Tuple, Dict
from schema import Problem

# Cache for solved puzzles (simple string-based cache)
_solution_cache: Dict[str, Optional[List[int]]] = {}


def verify_solution(problem: Problem, solution: List[int]) -> Tuple[bool, str]:
    """Verify if a solution is valid. Returns (is_valid, final_string)."""
    current = problem.initial_string
    for step in solution:
        if step >= len(problem.transitions):
            return False, current
        trans = problem.transitions[step]
        if trans.src not in current:
            return False, current
        current = current.replace(trans.src, trans.tgt, 1)
    return current == "", current


def _get_cache_key(problem: Problem) -> str:
    """Generate cache key for a problem."""
    # Normalize by sorting transitions (same transitions = same puzzle structure)
    trans_strs = sorted([f"{t.src}->{t.tgt}" for t in problem.transitions])
    return f"{problem.initial_string}|{'|'.join(trans_strs)}"


def solve_bfs(problem: Problem, time_limit: float = 30.0, use_cache: bool = True) -> Optional[List[int]]:
    """BFS solver for finding a solution with caching support.
    
    Args:
        problem: The puzzle to solve
        time_limit: Maximum time in seconds (default 30.0)
        use_cache: Whether to use solution cache (default True)
    
    Returns:
        Solution as list of transition indices, or None if unsolvable/timeout
    """
    # Check cache first
    if use_cache:
        cache_key = _get_cache_key(problem)
        if cache_key in _solution_cache:
            return _solution_cache[cache_key]
    
    initial = problem.initial_string
    transitions = problem.transitions
    
    queue = deque([(initial, [])])
    visited = {initial}
    start_time = time.time()
    
    while queue:
        if time.time() - start_time > time_limit:
            result = None
            break
        
        current, path = queue.popleft()
        
        if current == "":
            result = path
            break
        
        # Try transitions in order
        for i, trans in enumerate(transitions):
            if trans.src in current:
                new_string = current.replace(trans.src, trans.tgt, 1)
                if new_string not in visited:
                    visited.add(new_string)
                    queue.append((new_string, path + [i]))
    else:
        result = None  # No solution found
    
    # Cache result
    if use_cache:
        cache_key = _get_cache_key(problem)
        _solution_cache[cache_key] = result
    
    return result


def clear_cache():
    """Clear the solution cache."""
    global _solution_cache
    _solution_cache.clear()

