# Generation Pipeline

## Architecture Overview

The dataset generation follows a **two-phase architecture**:

```
Phase 1: Pool Generation (250+ candidates)
    ↓
Phase 2: Representative Selection (100 final)
```

This approach ensures **quality over quantity** — generate many, select the best.

---

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DATASET GENERATION PIPELINE                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│   │  Generator  │───▶│   Solver    │───▶│  Validator  │            │
│   │  Selection  │    │    (BFS)    │    │             │            │
│   └─────────────┘    └─────────────┘    └─────────────┘            │
│         │                  │                  │                     │
│         ▼                  ▼                  ▼                     │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│   │   Puzzle    │───▶│  Solution   │───▶│  Duplicate  │            │
│   │ Generation  │    │ Verification│    │   Check     │            │
│   └─────────────┘    └─────────────┘    └─────────────┘            │
│                                               │                     │
│                                               ▼                     │
│                         ┌─────────────────────────────┐            │
│                         │    Difficulty Analysis      │            │
│                         │  • Branching Factor         │            │
│                         │  • Solution Length          │            │
│                         │  • Distractor Count         │            │
│                         └─────────────────────────────┘            │
│                                               │                     │
│                                               ▼                     │
│                         ┌─────────────────────────────┐            │
│                         │   Quality-Based Selection   │            │
│                         │  • Stratified by difficulty │            │
│                         │  • Balanced by generator    │            │
│                         └─────────────────────────────┘            │
│                                               │                     │
│                                               ▼                     │
│                         ┌─────────────────────────────┐            │
│                         │     Final Dataset (100)     │            │
│                         └─────────────────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Pool Generation

### Goal

Generate a **large pool** of candidate puzzles (target: 250+).

### Algorithm

```python
def generate_pool(target_pool_size=250):
    puzzles = []
    max_attempts = target_pool_size * 20  # Allow many retries
    
    while len(puzzles) < target_pool_size and attempts < max_attempts:
        # 1. Select generator randomly (weighted by difficulty targets)
        generator = select_generator()
        
        # 2. Generate puzzle
        puzzle, solution = generator(problem_id)
        
        # 3. If no solution provided, solve with BFS
        if solution is None:
            solution = solve_bfs(puzzle, timeout=30)
            if solution is None:
                continue  # Skip unsolvable
        
        # 4. Verify solution
        is_valid, _ = verify_solution(puzzle, solution)
        if not is_valid:
            continue  # Skip invalid
        
        # 5. Check duplicates
        if is_duplicate(puzzle, puzzles):
            continue  # Skip duplicate
        
        # 6. Analyze difficulty
        metrics = analyze_difficulty(puzzle, solution)
        
        # 7. Store
        puzzles.append((puzzle, solution, metrics))
```

### Generator Selection

Generators are selected with **weighted probability** based on target difficulty distribution:

| Difficulty | Target % | Generators |
|------------|----------|------------|
| Easy | 25% | `concat_2`, `concat_3`, `palin_2` |
| Medium | 35% | `concat_4`, `backward_3`, `sort_3`, `palin_3` |
| Hard | 30% | `backward_5`, `sort_4`, `multiphase` |
| Expert | 10% | `backward_7`, `expansion` |

### Why Over-generate?

1. **Quality filtering** — Some puzzles are rejected (duplicates, invalid)
2. **Selection flexibility** — More candidates = better curation
3. **Statistical coverage** — Ensures all difficulty levels are represented

---

## Phase 2: Representative Selection

### Goal

Select **100 high-quality puzzles** with balanced difficulty and generator diversity.

### Algorithm

```python
def select_representative(target_count=100):
    # 1. Bucket by difficulty level
    buckets = {
        'easy': [],
        'medium': [],
        'hard': [],
        'expert': []
    }
    for puzzle, metrics in pool:
        buckets[metrics.difficulty_level].append(puzzle)
    
    # 2. Target distribution
    targets = {
        'easy': 25,
        'medium': 35,
        'hard': 30,
        'expert': 10
    }
    
    # 3. Handle missing levels (redistribute slots)
    redistribute_empty_buckets(buckets, targets)
    
    # 4. Select from each bucket
    selected = []
    for level, count in targets.items():
        candidates = buckets[level]
        # Sort by quality + diversity
        ranked = rank_by_quality_and_diversity(candidates)
        selected.extend(ranked[:count])
    
    # 5. Balance generator types
    selected = balance_strategies(selected)
    
    # 6. Renumber sequentially
    renumber_ids(selected)
    
    return selected
```

### Selection Criteria

Within each difficulty bucket, puzzles are ranked by:

1. **Quality score** — Higher is better
2. **Generator diversity** — Prefer under-represented types
3. **Solution length** — Not too trivial, not too long
4. **Branching factor** — Meaningful decision points

---

## BFS Solver

### Purpose

Find optimal (shortest) solutions for puzzles that don't provide direct solutions.

### Algorithm

```python
def solve_bfs(problem, time_limit=30.0):
    queue = deque([(initial_string, [])])
    visited = {initial_string}
    
    while queue:
        if timeout():
            return None
        
        current, path = queue.popleft()
        
        if current == "":
            return path  # Optimal solution found
        
        for i, (src, tgt) in enumerate(transitions):
            if src in current:
                new_string = current.replace(src, tgt, 1)
                if new_string not in visited:
                    visited.add(new_string)
                    queue.append((new_string, path + [i]))
    
    return None  # No solution exists
```

### Guarantees

- **Optimality** — BFS finds shortest path (all edges have equal weight)
- **Completeness** — Will find solution if one exists (given infinite time)
- **Determinism** — Same puzzle always gets same solution

### Performance Optimizations

1. **Visited set** — Avoids revisiting states
2. **Solution caching** — Reuse solutions for similar puzzles
3. **Timeout** — 30 seconds max to avoid hanging

---

## Solution Verification

### Purpose

Ensure every solution is **actually correct**.

### Algorithm

```python
def verify_solution(problem, solution):
    current = problem.initial_string
    
    for step in solution:
        # Check valid index
        if step >= len(transitions):
            return False, current
        
        src, tgt = transitions[step]
        
        # Check applicability
        if src not in current:
            return False, current
        
        # Apply transition
        current = current.replace(src, tgt, 1)
    
    return current == "", current
```

### What It Catches

| Error Type | Example |
|------------|---------|
| Invalid index | `solution = [0, 1, 99]` (99 out of bounds) |
| Inapplicable rule | Rule `"XYZ" → ""` but "XYZ" not in string |
| Non-termination | Final string is `"AB"` not `""` |
| Wrong order | Rules applied in wrong sequence |

---

## Duplicate Detection

### Purpose

Ensure no two puzzles are functionally identical.

### Detection Methods

1. **Exact match** — Same initial string (case-insensitive)
2. **Semantic match** — Same string + same transitions (order-independent)

### Implementation

```python
def is_duplicate(new_puzzle, existing_puzzles):
    new_str = new_puzzle.initial_string.lower()
    
    for existing in existing_puzzles:
        if existing.initial_string.lower() == new_str:
            return True
    
    return False
```

### Why Case-Insensitive?

Avoids near-duplicates like `"ABCD"` and `"AbCd"` which are essentially the same puzzle.

---

## Statistics Tracking

### What's Tracked

During generation, we track:

| Metric | Purpose |
|--------|---------|
| Attempts per generator | Identify struggling generators |
| Success rate | Generator reliability |
| Failure reasons | Debugging (timeout, invalid, duplicate) |
| Difficulty distribution | Ensure coverage |

### Example Output

```
Generation Statistics:
  concat_2:    427/427 (100.0%) - avg 0.01s
  backward_3:  361/371 (97.3%) - avg 0.02s
  backward_7:  1512/2044 (74.0%) - avg 0.05s
  sort_3:      20/172 (11.6%) - avg 2.3s
  multiphase:  2/81 (2.5%) - avg 5.1s
  expansion:   0/231 (0.0%) - FAILED
```

---

## Configuration Parameters

### Tunable Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_pool_size` | 250 | Candidates to generate |
| `target_count` | 100 | Final dataset size |
| `max_attempts` | pool × 20 | Maximum generation attempts |
| `bfs_timeout` | 30s | Solver timeout |
| `random_seed` | 42 | Reproducibility |

### Difficulty Thresholds

| Level | Score Range |
|-------|-------------|
| Easy | < 25 |
| Medium | 25-49 |
| Hard | 50-74 |
| Expert | ≥ 75 |

---

## Key Design Decisions

### Why Two Phases?

1. **Decoupling** — Generation and selection are independent
2. **Flexibility** — Can re-run selection without regenerating
3. **Quality** — Over-generate then filter produces better results
4. **Debugging** — Can inspect pool before selection

### Why Weighted Generator Selection?

Without weighting, easy generators dominate (higher success rates). Weighting ensures:
- All difficulty levels are represented
- All reasoning types are included
- No single generator type dominates

### Why 250 → 100?

- **2.5× over-generation** balances quality vs. generation time
- Enough candidates for meaningful selection
- Not so many that generation takes too long

---

*Previous: [← Data Structures](02-data-structures.md) | Next: [Generator Strategies →](04-generator-strategies.md)*

