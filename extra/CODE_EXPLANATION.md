# SED Dataset Generation - Code Explanation

## Overview

This directory contains a complete system for generating a curated dataset of SED (String Edit Distance) puzzles. The system generates puzzles using multiple strategies, validates them, analyzes their difficulty, and selects a representative subset.

---

## Architecture & Flow

```
main.py (orchestrator)
    ↓
generators.py (puzzle creation)
    ↓
solver.py (validation)
    ↓
metrics.py (difficulty analysis)
    ↓
main.py (curation & export)
```

---

## File-by-File Breakdown

### 1. `main.py` - Main Orchestrator

**Purpose**: Coordinates the entire dataset generation pipeline.

**Key Class**: `DatasetGenerator`

#### Methods:

##### `__init__(seed: int = 42)`
- **Input**: Random seed for reproducibility
- **Output**: Initialized generator with empty lists for puzzles, solutions, and metadata
- **Purpose**: Sets up the generator with a fixed random seed

##### `generate_pool(target_pool_size: int = 250)`
- **Input**: Target number of puzzles to generate (default 250)
- **Output**: Populates `self.puzzles`, `self.solutions`, and `self.metadata`
- **Logic**:
  1. Defines 12 different generator strategies with their difficulty levels:
     - **Easy (25%)**: `concat_2`, `concat_3`, `palin_2`
     - **Medium (35%)**: `concat_4`, `backward_3`, `sort_3`, `palin_3`
     - **Hard (30%)**: `backward_5`, `sort_4`, `multiphase`
     - **Expert (10%)**: `backward_7`, `expansion`
  2. Randomly selects a generator and creates a puzzle
  3. If no solution provided, solves using BFS (15s timeout)
  4. Verifies solution is valid
  5. Checks for duplicates (by initial_string)
  6. Analyzes difficulty metrics
  7. Stores puzzle, solution, and metadata
  8. Continues until pool size reached or max attempts exceeded

##### `select_representative(target_count: int = 100)`
- **Input**: Target number of puzzles to select (default 100)
- **Output**: Filters and renumbers puzzles to final dataset
- **Logic**:
  1. Buckets puzzles by difficulty level
  2. Selects target distribution:
     - Easy: 25
     - Medium: 35
     - Hard: 30
     - Expert: 10
  3. Within each bucket, sorts by "interestingness" (solution_length, branching_factor)
  4. Ensures strategy diversity using `_balance_strategies()`
  5. Renumbers problem IDs sequentially (000, 001, 002, ...)

##### `_balance_strategies(indices: List[int], target_count: int)`
- **Input**: List of selected indices, target count
- **Output**: Balanced list ensuring generator type diversity
- **Logic**: Prefers less common generator types when trimming

##### `save_dataset(output_dir: Path)`
- **Input**: Output directory path
- **Output**: Creates JSON files in `output_dir/`
- **Structure**:
  ```
  output_dir/
    ├── puzzles/
    │   ├── 000.json
    │   ├── 001.json
    │   └── ...
    ├── solutions/
    │   ├── 000.json
    │   ├── 001.json
    │   └── ...
    └── metadata.json
  ```

##### `print_statistics()`
- **Output**: Prints summary statistics to console
- Shows: total count, difficulty distribution, strategy distribution, length ranges

#### Main Function Flow:
```python
1. Create DatasetGenerator(seed=42)
2. generate_pool(250)      # Generate large pool
3. select_representative(100)  # Curate to 100
4. print_statistics()      # Show stats
5. save_dataset(data_dir)  # Export to files
```

---

### 2. `generators.py` - Puzzle Generation Strategies

**Purpose**: Implements 6 different puzzle generation strategies.

All generators return: `Tuple[Problem, Optional[List[int]]]`
- `Problem`: The puzzle (initial_string + transitions)
- `List[int]`: Solution (transition indices), or `None` if needs BFS solving

#### Generator Functions:

##### `generate_concatenation_puzzle(problem_id: str, num_parts: int = 3)`
- **Input**: Problem ID, number of parts to concatenate
- **Output**: Puzzle where string is made of parts that can be removed
- **Logic**:
  1. Creates `num_parts` random strings (3-6 chars each)
  2. Concatenates them into `initial_string`
  3. Creates transitions to remove each part
  4. Shuffles transitions
  5. Solution is reverse of construction order (removes parts in reverse)

**Example**:
- Parts: `["ABC", "DEF", "GHI"]`
- Initial: `"ABCDEFGHI"`
- Transitions: Remove "ABC", "DEF", "GHI" (shuffled)
- Solution: Remove in reverse order

##### `generate_palindrome_puzzle(problem_id: str, half_length: int = 3)`
- **Input**: Problem ID, half-length of palindrome
- **Output**: Palindrome checker puzzle
- **Logic**:
  1. Creates left half of palindrome (binary: 0s and 1s)
  2. Adds marker "?" in middle
  3. Creates right half as reverse of left
  4. Transitions:
     - Convert "?" to "!"
     - Match "0!0" → "!"
     - Match "1!1" → "!"
     - Remove "!" when done
  5. Solution: Convert marker, match pairs, remove marker

**Example**:
- Initial: `"101?101"`
- Solution: Convert ?, match 1!1, match 0!0, match 1!1, remove !

##### `generate_sorting_puzzle(problem_id: str, num_items: int = 3)`
- **Input**: Problem ID, number of items to sort
- **Output**: Bubble-sort style puzzle
- **Logic**:
  1. Creates string with `num_items` dots (.) and `num_items` hashes (#)
  2. Shuffles them randomly
  3. Transitions:
     - Swap adjacent ".#" → "#."
     - Remove sorted pattern "#...#..." → ""
  4. Solution: Needs BFS (returns None)

**Example**:
- Initial: `".##.#."`
- Goal: Sort dots to left, hashes to right, then remove

##### `generate_backward_puzzle(problem_id: str, num_steps: int = 4)`
- **Input**: Problem ID, number of construction steps
- **Output**: Puzzle built backwards (guarantees solvability)
- **Logic**:
  1. Starts with empty string
  2. For each step:
     - Generates random segment (2-4 chars)
     - Adds to left or right of current string
     - Creates transition to remove that segment
  3. Adds 1-2 distractor transitions (segments not in string)
  4. Shuffles all transitions
  5. Solution is reverse of construction order

**Key Feature**: Backward construction ensures puzzle is always solvable!

**Example**:
- Step 1: Add "AB" → "AB"
- Step 2: Add "CD" to right → "ABCD"
- Step 3: Add "EF" to left → "EFABCD"
- Initial: `"EFABCD"`
- Transitions: Remove "AB", "CD", "EF" (plus distractors)
- Solution: Remove in reverse order

##### `generate_multiphase_puzzle(problem_id: str)`
- **Input**: Problem ID
- **Output**: Puzzle requiring multiple distinct phases
- **Logic**:
  1. Creates string with even number of "A"s and marker "#"
  2. Transitions:
     - Phase 1: Convert "A" → "B"
     - Phase 2: Remove "BB" pairs
     - Phase 3: Remove "#"
     - Distractors: "AB" → "BA", "AA" → "" (trap)
  3. Solution: Needs BFS (returns None)

**Example**:
- Initial: `"AAAA#"`
- Solution: Convert all A→B, remove BB pairs, remove #

##### `generate_expansion_puzzle(problem_id: str)`
- **Input**: Problem ID
- **Output**: Puzzle where string must expand before contracting
- **Logic**:
  1. Starts with 2-char seed (e.g., "AB")
  2. Transitions:
     - Expand first char: "A" → "AXX"
     - Remove when 4 X's: "XXXX" → ""
     - Remove second char: "B" → ""
     - Distractor: "XX" → ""
  3. Solution: Needs BFS (returns None)

**Example**:
- Initial: `"AB"`
- Solution: Expand A→AXX, expand again→AXXXX, remove XXXX, remove B

---

### 3. `solver.py` - BFS Solver & Verification

**Purpose**: Solves puzzles and verifies solutions.

#### Functions:

##### `verify_solution(problem: Problem, solution: List[int]) -> Tuple[bool, str]`
- **Input**: 
  - `problem`: The puzzle
  - `solution`: List of transition indices
- **Output**: `(is_valid: bool, final_string: str)`
- **Logic**:
  1. Starts with `initial_string`
  2. For each step in solution:
     - Checks if transition index is valid
     - Checks if source pattern exists in current string
     - Replaces first occurrence of source with target
  3. Returns `True` if final string is empty, `False` otherwise

##### `solve_bfs(problem: Problem, time_limit: float = 10.0) -> Optional[List[int]]`
- **Input**: 
  - `problem`: The puzzle to solve
  - `time_limit`: Maximum time in seconds (default 10.0)
- **Output**: Solution as list of transition indices, or `None` if unsolvable/timeout
- **Logic**:
  1. BFS (Breadth-First Search) from initial string
  2. Queue stores `(current_string, path_so_far)`
  3. For each state:
     - Try all applicable transitions
     - Create new states by applying transitions
     - Track visited states to avoid cycles
  4. Returns first path that reaches empty string
  5. Times out after `time_limit` seconds

**Time Complexity**: O(b^d) where b = branching factor, d = solution depth

---

### 4. `metrics.py` - Difficulty Analysis

**Purpose**: Analyzes puzzle difficulty and computes metrics.

#### Class: `DifficultyMetrics`

**Fields**:
- `solution_length`: Number of steps in solution
- `branching_factor`: Average number of applicable transitions per step
- `initial_string_length`: Length of starting string
- `num_transitions`: Total number of transitions
- `num_distractors`: Number of transitions not used in solution
- `max_intermediate_length`: Maximum string length during solution
- `has_expansion`: Whether string grows during solution

#### Methods:

##### `compute_difficulty_score() -> float`
- **Output**: Score from 0-100
- **Formula**:
  ```
  score = min(30, solution_length * 3)      # 0-30 points
        + min(25, branching_factor * 5)     # 0-25 points
        + min(20, string_length * 0.5)      # 0-20 points
        + min(15, num_distractors * 3)      # 0-15 points
        + (10 if has_expansion else 0)      # 0-10 points
  ```

##### `difficulty_level() -> str`
- **Output**: "easy", "medium", "hard", or "expert"
- **Thresholds**:
  - Easy: score < 25
  - Medium: 25 ≤ score < 50
  - Hard: 50 ≤ score < 75
  - Expert: score ≥ 75

#### Function: `analyze_difficulty(problem: Problem, solution: List[int]) -> DifficultyMetrics`
- **Input**: Puzzle and its solution
- **Output**: `DifficultyMetrics` object with all fields populated
- **Logic**:
  1. Simulates solution step-by-step
  2. Counts applicable transitions at each step (for branching factor)
  3. Tracks maximum intermediate string length
  4. Counts distractors (transitions not in solution)
  5. Checks if expansion occurred

---

### 5. `cleanup.py` - Utility Script

**Purpose**: Removes generated dataset files.

#### Function: `cleanup_dataset()`
- **Input**: None
- **Output**: Deletes `../data/` directory and `__pycache__` directories
- **Usage**: Run before regenerating dataset to start fresh

---

## Data Structures

### Problem Schema (from `sed-solver/src/schema.py`):
```python
class Problem:
    problem_id: str          # e.g., "000"
    initial_string: str      # Starting string
    transitions: List[Transition]  # List of (src, tgt) pairs

class Transition:
    src: str  # Pattern to match
    tgt: str  # Replacement string
```

### Solution Schema:
```python
class Solution:
    problem_id: str
    solution: List[int]  # Indices into transitions list
```

### Metadata Structure:
```json
{
  "problem_id": "000",
  "generator": "concat_2",
  "difficulty_score": 18.5,
  "difficulty_level": "easy",
  "solution_length": 2,
  "string_length": 10,
  "branching_factor": 1.5,
  "num_distractors": 0,
  "has_expansion": false
}
```

---

## Input/Output Summary

### Inputs:
1. **Command-line execution**: `python main.py`
   - No arguments required
   - Uses default seed=42, pool_size=250, target_count=100

2. **Generator functions**: Problem ID string
   - Each generator takes a `problem_id` parameter
   - Some take additional parameters (e.g., `num_parts`, `num_steps`)

### Outputs:
1. **Directory structure** (`../data/`):
   ```
   data/
   ├── puzzles/
   │   ├── 000.json
   │   ├── 001.json
   │   └── ... (100 files)
   ├── solutions/
   │   ├── 000.json
   │   ├── 001.json
   │   └── ... (100 files)
   └── metadata.json (100 entries)
   ```

2. **Puzzle JSON format**:
   ```json
   {
     "problem_id": "000",
     "initial_string": "ABCDEF",
     "transitions": [
       {"src": "ABC", "tgt": ""},
       {"src": "DEF", "tgt": ""}
     ]
   }
   ```

3. **Solution JSON format**:
   ```json
   {
     "problem_id": "000",
     "solution": [1, 0]
   }
   ```

4. **Console output**:
   - Progress messages during generation
   - Final statistics summary

---

## Key Design Decisions

1. **Backward Construction**: Many generators build puzzles backwards (from empty string) to guarantee solvability
2. **Pool-then-Select**: Generates large pool (250) then curates to 100 for better quality
3. **Difficulty Bucketing**: Ensures balanced distribution across difficulty levels
4. **Strategy Diversity**: Balances different generator types in final dataset
5. **BFS Solver**: Uses breadth-first search with timeout for puzzles that need solving
6. **Comprehensive Metrics**: Tracks multiple difficulty factors (length, branching, distractors, expansion)

---

## Usage Examples

### Generate Dataset:
```bash
cd sed-reasoning/dataset_generation
python main.py
```

### Clean and Regenerate:
```bash
python cleanup.py
python main.py
```

### Expected Runtime:
- Pool generation: ~5-15 minutes (depends on puzzle complexity)
- Selection & export: < 1 second
- Total: ~5-15 minutes

---

## Dependencies

- Python 3.7+
- `pydantic` (for schema validation)
- Standard library: `json`, `pathlib`, `random`, `collections`, `time`

---

## Error Handling

- **Unsolved puzzles**: Skipped (generator tries again)
- **Invalid solutions**: Skipped (verification fails)
- **Duplicates**: Skipped (same initial_string)
- **Timeouts**: BFS solver returns None, puzzle skipped
- **Exceptions**: Caught and skipped (generator tries again)

The system is designed to be robust and will continue generating until pool size is reached or max attempts exceeded.

