# Generator Strategies

## Overview

Six distinct generation strategies, each testing different reasoning types:

| Generator | Reasoning Type | Difficulty | Solution Type |
|-----------|---------------|------------|---------------|
| Concatenation | Pattern matching | Easy | Direct |
| Backward | Sequential | Medium-Expert | Direct |
| Palindrome | Pattern recognition | Medium-Hard | Direct |
| Sorting | Algorithmic | Medium-Hard | BFS |
| Multiphase | Multi-phase planning | Hard | BFS |
| Expansion | Non-monotonic | Expert | BFS |

---

## 1. Concatenation Generator

### Principle

Create strings as **concatenation of independently removable segments**.

### Algorithm

```python
def generate_concatenation_puzzle(problem_id, num_parts=3):
    # 1. Create random parts
    parts = [random_string(3, 6) for _ in range(num_parts)]
    
    # 2. Concatenate
    initial = "".join(parts)  # e.g., "ABCDEFGHI"
    
    # 3. Create deletion transitions
    transitions = [Transition(src=part, tgt="") for part in parts]
    
    # 4. Shuffle transitions
    random.shuffle(transitions)
    
    # 5. Solution: remove in reverse order (or any valid order)
    solution = list(range(num_parts))
    
    return Problem(problem_id, initial, transitions), solution
```

### Example

```
Parts: ["ABC", "DEF", "GHI"]
Initial: "ABCDEFGHI"
Transitions: [ABC→"", DEF→"", GHI→""] (shuffled)
Solution: Any order works (parts are independent)
```

### Analysis

| Property | Value |
|----------|-------|
| Success Rate | 100% |
| Solution Known | Yes (by construction) |
| Difficulty | Easy |
| Reasoning Type | Simple pattern matching |
| Branching Factor | num_parts |

### Why It's Easy

- Parts don't overlap → order doesn't matter
- No distractors → all transitions are useful
- Clear pattern → just find and remove each part

---

## 2. Backward Construction Generator

### Principle

Build puzzles **backwards from the goal state** — guarantees solvability.

### Algorithm

```python
def generate_backward_puzzle(problem_id, num_steps=4):
    current = ""  # Start from goal
    transitions = []
    solution_path = []
    
    for step in range(num_steps):
        # Generate segment to add
        segment = random_string(2, 4)
        
        # Add to left or right
        if random.choice([True, False]):
            current = segment + current
        else:
            current = current + segment
        
        # Create removal transition
        transitions.append(Transition(src=segment, tgt=""))
        solution_path.append(len(transitions) - 1)
    
    # Add distractors (inapplicable transitions)
    for _ in range(random.randint(1, 2)):
        distractor = random_string(3)
        if distractor not in current:
            transitions.append(Transition(src=distractor, tgt=""))
    
    # Shuffle transitions
    perm = random.sample(range(len(transitions)), len(transitions))
    shuffled = [transitions[perm[i]] for i in range(len(transitions))]
    
    # Update solution indices
    inv_perm = [0] * len(transitions)
    for i, p in enumerate(perm):
        inv_perm[p] = i
    solution = [inv_perm[s] for s in reversed(solution_path)]
    
    return Problem(problem_id, current, shuffled), solution
```

### Key Insight: Backward Construction Guarantee

**Theorem**: If $s$ is constructed by iteratively prepending/appending segments $\{\alpha_1, ..., \alpha_k\}$ to $\varepsilon$, then applying transitions $\{(\alpha_i, \varepsilon)\}$ in reverse construction order yields $\varepsilon$.

**Proof**: By induction. Each step removes the most recently added segment, reversing the construction.

### Example

```
Construction Trace:
  Step 1: "" → "AB"      (add "AB")
  Step 2: "AB" → "CDAB"  (add "CD" to left)
  Step 3: "CDAB" → "CDABEF" (add "EF" to right)

Initial: "CDABEF"
Transitions: [CD→"", AB→"", EF→"", XYZ→"" (distractor)]
Solution: [2, 1, 0] (reverse of construction)

Verification:
  "CDABEF" → "CDAB" → "CD" → "" ✓
```

### Analysis

| Property | Value |
|----------|-------|
| Success Rate | 74-97% (varies by num_steps) |
| Solution Known | Yes (by construction) |
| Difficulty | Medium (3 steps) to Expert (7 steps) |
| Reasoning Type | Sequential, order-dependent |
| Distractors | 1-2 (makes it harder) |

### Why It's Powerful

- **Guaranteed solvability** — construction ensures solution exists
- **Scalable difficulty** — more steps = harder
- **Realistic distractors** — forces discrimination
- **Order-dependent** — tests sequential reasoning

---

## 3. Palindrome Generator

### Principle

Verify palindrome structure using **marker-based matching**.

### Algorithm

```python
def generate_palindrome_puzzle(problem_id, half_length=3):
    # 1. Create binary palindrome
    left_half = "".join(random.choice("01") for _ in range(half_length))
    
    # 2. Add marker and reverse
    initial = left_half + "?" + left_half[::-1]  # e.g., "101?101"
    
    # 3. Create matching transitions
    transitions = [
        Transition(src="?", tgt="!"),    # Activate marker
        Transition(src="0!0", tgt="!"),  # Match 0-pair
        Transition(src="1!1", tgt="!"),  # Match 1-pair
        Transition(src="!", tgt=""),     # Remove marker
    ]
    
    # 4. Solution: activate, match all pairs, remove
    solution = [0]  # Activate
    for char in left_half:
        solution.append(1 if char == '0' else 2)  # Match
    solution.append(3)  # Remove
    
    return Problem(problem_id, initial, transitions), solution
```

### Example

```
Initial: "101?101"
Transitions:
  0: ? → !
  1: 0!0 → !
  2: 1!1 → !
  3: ! → ""

Solution: [0, 2, 1, 2, 3]

Trace:
  "101?101" → "101!101" → "10!01" → "1!1" → "!" → "" ✓
```

### Analysis

| Property | Value |
|----------|-------|
| Success Rate | 3-6% (often fails validation) |
| Solution Known | Yes (by construction) |
| Difficulty | Medium-Hard |
| Reasoning Type | Pattern recognition, symmetry |

### Mathematical Structure

This simulates a **pushdown automaton** — the marker acts as a stack pointer, matching pairs from outside in. This is a classic technique for recognizing context-free languages.

---

## 4. Sorting Generator

### Principle

Simulate **bubble sort** on a two-symbol string.

### Algorithm

```python
def generate_sorting_puzzle(problem_id, num_items=3):
    # 1. Create string with n dots and n hashes
    items = ['.'] * num_items + ['#'] * num_items
    random.shuffle(items)
    initial = "".join(items)  # e.g., ".##.#."
    
    # 2. Create transitions
    transitions = [
        Transition(src=".#", tgt="#."),  # Swap adjacent
        Transition(src="#" * num_items + "." * num_items, tgt=""),  # Remove sorted
    ]
    
    # 3. No direct solution — needs BFS
    return Problem(problem_id, initial, transitions), None
```

### Example

```
Initial: ".##.#."
Target:  "###..." (sorted: all # left, all . right)

Transitions:
  0: .# → #.  (swap)
  1: ###... → "" (remove sorted)

Solution (found by BFS): [0, 0, 0, 0, 1]

Trace:
  ".##.#." → "#.#.#." → "##..#." → "##.#.." → "###..." → "" ✓
```

### Analysis

| Property | Value |
|----------|-------|
| Success Rate | 12-27% (BFS may timeout) |
| Solution Known | No (BFS required) |
| Difficulty | Medium-Hard |
| Reasoning Type | Algorithmic (bubble sort) |

### State Space Analysis

$$|V| = \binom{2n}{n} = \frac{(2n)!}{n! \cdot n!}$$

For $n=4$: $|V| = 70$ states (manageable by BFS).

### Optimal Solution Length

Equals the number of inversions in the initial string plus one:

$$|\sigma|_{\text{opt}} = \text{inv}(s_0) + 1$$

---

## 5. Multiphase Generator

### Principle

Require **sequential phases** before reaching goal.

### Algorithm

```python
def generate_multiphase_puzzle(problem_id):
    # 1. Create string with even number of A's and marker
    num_a = random.choice([2, 4, 6])
    initial = "A" * num_a + "#"  # e.g., "AAAA#"
    
    # 2. Create phase transitions
    transitions = [
        Transition(src="A", tgt="B"),   # Phase 1: Convert
        Transition(src="BB", tgt=""),   # Phase 2: Remove pairs
        Transition(src="#", tgt=""),    # Phase 3: Terminal
        Transition(src="AB", tgt="BA"), # Distractor
        Transition(src="AA", tgt=""),   # TRAP!
    ]
    
    # 3. No direct solution — needs BFS (or careful construction)
    return Problem(problem_id, initial, transitions), None
```

### The Trap Rule Analysis

The rule `AA → ""` is a **trap**:

- **If applied when count is even**: Creates odd number of B's
- **Odd B's cannot be eliminated**: `BB` removes pairs only
- **Result**: Unsolvable state

**Example of trap:**
```
Initial: "AAAA#" (4 A's)

Correct: A→B, A→B, A→B, A→B, BB→"", BB→"", #→""
Trap:    AA→"", AA→"", #→"" → "" ✓ (works because 4 is even, can remove 2 pairs)

But for "AAA#" (3 A's):
Trap:    AA→"" → "A#" → stuck! (can't remove single A)
```

### Analysis

| Property | Value |
|----------|-------|
| Success Rate | 2.5% (very low) |
| Solution Known | No (BFS required) |
| Difficulty | Hard |
| Reasoning Type | Phase planning, constraint awareness |

### Cognitive Model

Tests **constraint satisfaction** — solver must recognize:
1. Phases must be completed in order
2. Trap rules lead to dead ends
3. Non-obvious intermediate states are required

---

## 6. Expansion Generator (BROKEN)

### Principle

String must **expand before contracting** — non-monotonic.

### Algorithm

```python
def generate_expansion_puzzle(problem_id):
    # 1. Start with 2-char seed
    initial = random.choice(["AB", "XY", "PQ"])
    
    # 2. Create transitions
    transitions = [
        Transition(src=initial[0], tgt=initial[0] + "XX"),  # Expand
        Transition(src="XXXX", tgt=""),                      # Remove 4 X's
        Transition(src=initial[1], tgt=""),                  # Remove second char
        Transition(src="XX", tgt=""),                        # Distractor
    ]
    
    return Problem(problem_id, initial, transitions), None
```

### Expected Solution

```
Initial: "AB"
  "AB" → "AXXB" → "AXXXXB" → "AB" → "B" → "" 

Wait — this doesn't work! After AXXXXB → AB, we're back where we started.
```

### Why It's Broken

The solution construction has a **bug**:
- Expansion creates `A + XX` but A is still there
- Removing `XXXX` requires 4 X's, but we only added 2 per expansion
- The logic doesn't correctly track intermediate states

**Result**: 0% success rate (all 231 attempts failed validation).

### Analysis

| Property | Value |
|----------|-------|
| Success Rate | 0% ❌ |
| Solution Known | No |
| Difficulty | Expert (in theory) |
| Status | **BROKEN** |

---

## Generator Comparison

### Success Rates

```
concat_*:    ████████████████████ 100%
backward_3:  ████████████████████  97%
backward_7:  ███████████████       74%
sort_4:      █████                 27%
sort_3:      ███                   12%
palin_*:     █                     3-6%
multiphase:  ▌                     2.5%
expansion:   ▏                     0%
```

### Reasoning Type Coverage

| Type | Generators | LLM Challenge |
|------|-----------|---------------|
| Pattern Matching | concat | Easy baseline |
| Sequential | backward | Order-dependent choices |
| Algorithmic | sort | Iterative refinement |
| Multi-phase | multiphase | Phase awareness |
| Pattern Recognition | palin | Symmetry detection |

---

## Recommendations for LLM Evaluation

### Keep ✅

| Generator | Why |
|-----------|-----|
| `backward_3/5/7` | Tests sequential reasoning at varying difficulty |
| `sort_3/4` | Tests algorithmic understanding |
| `multiphase` | Tests planning and constraint awareness |
| `palin_3` | Tests pattern recognition |

### Remove ❌

| Generator | Why |
|-----------|-----|
| `concat_3/4` | Redundant with concat_2 |
| `palin_2` | Too easy |
| `expansion` | Broken (0% success) |

### Keep for Baseline ⚠️

| Generator | Why |
|-----------|-----|
| `concat_2` | Sanity check — LLMs should solve 100% |

---

*Previous: [← Generation Pipeline](03-generation-pipeline.md) | Next: [Difficulty Metrics →](05-difficulty-metrics.md)*

