# Data Structures

## Overview

The dataset consists of three components:
1. **Puzzles** — problem definitions
2. **Solutions** — ground-truth answers
3. **Metadata** — difficulty and generation information

---

## Puzzle Schema

### JSON Format

```json
{
  "problem_id": "000",
  "initial_string": "CEAEEBEDDABCACBE",
  "transitions": [
    {"src": "CEAE", "tgt": ""},
    {"src": "EDD", "tgt": ""},
    {"src": "ABCA", "tgt": ""},
    {"src": "AEC", "tgt": ""},
    {"src": "EDC", "tgt": ""},
    {"src": "EB", "tgt": ""},
    {"src": "CBE", "tgt": ""}
  ]
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `problem_id` | `string` | 3-digit zero-padded identifier |
| `initial_string` | `string` | Starting state $s_0$ |
| `transitions` | `array` | Ordered list of rewrite rules |
| `transitions[i].src` | `string` | Source pattern $\alpha_i$ |
| `transitions[i].tgt` | `string` | Target replacement $\beta_i$ |

### Invariants

- `problem_id` is unique across the dataset
- `initial_string` is non-empty
- `transitions` has at least one element
- `src` is non-empty for all transitions
- `tgt` can be empty (deletion) or non-empty (replacement)

---

## Solution Schema

### JSON Format

```json
{
  "problem_id": "000",
  "solution": [0, 5, 1, 2, 6]
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `problem_id` | `string` | Matching puzzle identifier |
| `solution` | `array[int]` | Ordered list of transition indices |

### Interpretation

The solution `[0, 5, 1, 2, 6]` means:
1. Apply transition at index 0
2. Apply transition at index 5
3. Apply transition at index 1
4. Apply transition at index 2
5. Apply transition at index 6

### Verification

A solution is **valid** if and only if:

$$s_0 \xrightarrow{t_{\sigma_1}} s_1 \xrightarrow{t_{\sigma_2}} \cdots \xrightarrow{t_{\sigma_k}} \varepsilon$$

Each step must:
1. Reference a valid index ($ 0 \leq \sigma_i < |\mathcal{T}|$)
2. Be applicable ($\alpha_{\sigma_i} \sqsubseteq s_{i-1}$)
3. Result in empty string at the end ($s_k = \varepsilon$)

---

## Metadata Schema

### JSON Format (Array Element)

```json
{
  "problem_id": "000",
  "generator": "backward_5",
  "difficulty_score": 52.3,
  "difficulty_level": "hard",
  "solution_length": 5,
  "string_length": 16,
  "branching_factor": 2.8,
  "num_distractors": 2,
  "has_expansion": false,
  "quality_score": 85.0
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `problem_id` | `string` | Matching puzzle identifier |
| `generator` | `string` | Generation strategy used |
| `difficulty_score` | `float` | Composite difficulty [0-100] |
| `difficulty_level` | `string` | Category: easy/medium/hard/expert |
| `solution_length` | `int` | Number of steps $|\sigma|$ |
| `string_length` | `int` | Initial string length $|s_0|$ |
| `branching_factor` | `float` | Average applicable transitions |
| `num_distractors` | `int` | Unused transitions in solution |
| `has_expansion` | `bool` | Whether intermediate strings grow |
| `quality_score` | `float` | Curation quality metric [0-100] |

---

## Directory Structure

```
data/
├── puzzles/
│   ├── 000.json          # Puzzle definition
│   ├── 001.json
│   ├── 002.json
│   └── ... (100 files)
├── solutions/
│   ├── 000.json          # Ground-truth solution
│   ├── 001.json
│   ├── 002.json
│   └── ... (100 files)
└── metadata.json         # Array of all puzzle metadata
```

### File Naming Convention

- **Pattern**: `{problem_id}.json`
- **Format**: 3-digit zero-padded integer
- **Range**: 000 to 099 for 100 puzzles
- **Correspondence**: Puzzle and solution files share the same name

---

## Data Classes (Python)

### Problem Class

```python
@dataclass
class Transition:
    src: str  # Pattern to match
    tgt: str  # Replacement string

@dataclass
class Problem:
    problem_id: str
    initial_string: str
    transitions: List[Transition]
```

### Solution Class

```python
@dataclass
class Solution:
    problem_id: str
    solution: List[int]  # Indices into transitions
```

### DifficultyMetrics Class

```python
@dataclass
class DifficultyMetrics:
    solution_length: int = 0
    branching_factor: float = 0.0
    initial_string_length: int = 0
    num_transitions: int = 0
    num_distractors: int = 0
    max_intermediate_length: int = 0
    has_expansion: bool = False
```

---

## Design Decisions

### Why Separate Files?

1. **Modularity** — Can load puzzles without solutions (for LLM evaluation)
2. **Versioning** — Can update solutions without changing puzzles
3. **Scalability** — Can process puzzles individually
4. **Debugging** — Easy to inspect specific puzzles

### Why JSON?

1. **Human-readable** — Easy to inspect and debug
2. **Language-agnostic** — Works with Python, JavaScript, etc.
3. **Schema-flexible** — Can add fields without breaking
4. **Standard** — Well-supported everywhere

### Why Zero-Padded IDs?

1. **Sorting** — Files sort correctly (000, 001, ..., 099)
2. **Consistency** — Fixed-width IDs
3. **Scalability** — Can extend to 1000+ puzzles

---

## Example: Full Puzzle Walkthrough

### Puzzle 000 (backward_5)

**Puzzle JSON:**
```json
{
  "problem_id": "000",
  "initial_string": "CEAEEBEDDABCACBE",
  "transitions": [
    {"src": "CEAE", "tgt": ""},
    {"src": "EDD", "tgt": ""},
    {"src": "ABCA", "tgt": ""},
    {"src": "AEC", "tgt": ""},
    {"src": "EDC", "tgt": ""},
    {"src": "EB", "tgt": ""},
    {"src": "CBE", "tgt": ""}
  ]
}
```

**Solution JSON:**
```json
{
  "problem_id": "000",
  "solution": [0, 5, 1, 2, 6]
}
```

**Execution Trace:**
```
"CEAEEBEDDABCACBE" --[0: CEAE→""]-- → "EBEDDABCACBE"
"EBEDDABCACBE"     --[5: EB→""]--   → "EDDABCACBE"
"EDDABCACBE"       --[1: EDD→""]--  → "ABCACBE"
"ABCACBE"          --[2: ABCA→""]-- → "CBE"
"CBE"              --[6: CBE→""]--  → "" ✓
```

**Metadata:**
```json
{
  "problem_id": "000",
  "generator": "backward_5",
  "difficulty_score": 52.3,
  "difficulty_level": "hard",
  "solution_length": 5,
  "string_length": 16,
  "branching_factor": 2.8,
  "num_distractors": 2,
  "has_expansion": false,
  "quality_score": 85.0
}
```

**Note:** Transitions 3 (`AEC`) and 4 (`EDC`) are distractors—never used in the solution.

---

*Previous: [← Introduction](01-introduction.md) | Next: [Generation Pipeline →](03-generation-pipeline.md)*

