"""
Solution extraction from LLM responses.

Handles various response formats and extracts solution arrays.
"""

import json
import re
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def extract_solution(response: str, problem_id: str = None) -> Optional[List[int]]:
    """
    Extract solution array from LLM response.
    
    Handles various formats:
    - JSON: {"problem_id": "...", "solution": [0, 1, 2]}
    - JSON: {"solution": [0, 1, 2]}
    - JSON: [0, 1, 2]
    - Text: solution: [0, 1, 2]
    - Text: [0, 1, 2]
    
    Returns:
        List of integers (solution), or None if extraction fails
    """
    if not response:
        return None
    
    # Try 1: Extract JSON object
    json_match = re.search(r'\{[^}]*"solution"\s*:\s*\[([^\]]+)\][^}]*\}', response)
    if json_match:
        try:
            full_json = json_match.group(0)
            data = json.loads(full_json)
            if 'solution' in data and isinstance(data['solution'], list):
                return [int(x) for x in data['solution']]
        except (json.JSONDecodeError, ValueError) as e:
            logger.debug(f"Failed to parse JSON match: {e}")
    
    # Try 2: Extract array directly
    array_match = re.search(r'\[[\s\d,]+]', response)
    if array_match:
        try:
            arr_str = array_match.group(0)
            arr = json.loads(arr_str)
            if isinstance(arr, list) and all(isinstance(x, int) for x in arr):
                return arr
        except (json.JSONDecodeError, ValueError) as e:
            logger.debug(f"Failed to parse array: {e}")
    
    # Try 3: Find "solution:" followed by array
    solution_match = re.search(r'solution\s*:\s*\[([^\]]+)\]', response, re.IGNORECASE)
    if solution_match:
        try:
            arr_str = '[' + solution_match.group(1) + ']'
            arr = json.loads(arr_str)
            if isinstance(arr, list):
                return [int(x) for x in arr]
        except (json.JSONDecodeError, ValueError) as e:
            logger.debug(f"Failed to parse solution match: {e}")
    
    # Try 4: Extract comma-separated numbers
    numbers_match = re.findall(r'\b\d+\b', response)
    if numbers_match:
        try:
            solution = [int(n) for n in numbers_match]
            if len(solution) > 0:
                return solution
        except ValueError:
            pass
    
    # Try 5: Full JSON parse (if response is pure JSON)
    try:
        data = json.loads(response.strip())
        if isinstance(data, dict) and 'solution' in data:
            return [int(x) for x in data['solution']]
        elif isinstance(data, list):
            return [int(x) for x in data]
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    
    logger.warning(f"Could not extract solution from response: {response[:200]}...")
    return None


def validate_solution_format(solution: Optional[List[int]]) -> bool:
    """Validate that solution is a list of non-negative integers."""
    if solution is None:
        return False
    if not isinstance(solution, list):
        return False
    if len(solution) == 0:
        return False
    if not all(isinstance(x, int) and x >= 0 for x in solution):
        return False
    return True

