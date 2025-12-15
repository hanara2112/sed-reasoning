# Recommended Generators for LLM Evaluation

## Goal: Test Reasoning Capabilities

For evaluating LLMs on reasoning tasks (Zero-shot, Few-shot, CoT), we need generators that:
1. **Test different reasoning types** (sequential, multi-step, pattern recognition)
2. **Vary in difficulty** (easy to hard)
3. **Benefit from CoT** (multi-step reasoning that LLMs can explain)
4. **Are interesting** (not too trivial, reveal LLM weaknesses)

---

## Analysis of Each Generator Type

### ❌ **Concatenation (`concat_2/3/4`)** - NOT RECOMMENDED

**Why:**
- Too simple: Just pattern matching
- LLMs will solve easily (100% success rate)
- No interesting reasoning required
- All variants (`concat_2/3/4`) are essentially the same

**Reasoning Type:** Pattern matching only
**LLM Difficulty:** Too easy
**CoT Benefit:** Minimal (trivial steps)

**Verdict:** ❌ Remove all concatenation generators

---

### ✅ **Backward Construction (`backward_3/5/7`)** - HIGHLY RECOMMENDED

**Why:**
- Tests **sequential reasoning**: Must apply steps in correct order
- **Varying difficulty**: 3 steps (medium) → 7 steps (hard/expert)
- **Good for CoT**: LLMs can explain step-by-step reasoning
- **Distractors**: Tests if LLMs can ignore irrelevant transitions
- **Realistic**: Similar to real-world sequential tasks

**Reasoning Type:** Sequential, multi-step
**LLM Difficulty:** Medium to Hard
**CoT Benefit:** High (can explain each step)

**Verdict:** ✅ **Keep `backward_3`, `backward_5`, `backward_7`**
- Different difficulty levels
- Good for testing CoT effectiveness
- Can reveal LLM weaknesses in sequential reasoning

---

### ⚠️ **Palindrome (`palin_2/3`)** - CONDITIONALLY RECOMMENDED

**Why:**
- Tests **pattern recognition**: Recognizing palindrome structure
- **Symmetry reasoning**: Understanding mirror patterns
- **Low success rate** (3-6%) suggests complexity
- But: May be too hard or buggy

**Reasoning Type:** Pattern recognition, symmetry
**LLM Difficulty:** Hard (low success rate)
**CoT Benefit:** Medium (can explain pattern matching)

**Verdict:** ⚠️ **Keep ONE** (`palin_3` - harder variant)
- Tests pattern recognition
- Can reveal if LLMs understand symmetry
- But only if it's actually solvable

---

### ✅ **Sorting (`sort_3/4`)** - HIGHLY RECOMMENDED

**Why:**
- Tests **algorithmic reasoning**: Bubble sort logic
- **Multi-step**: Requires multiple swaps
- **Good for CoT**: LLMs can explain sorting algorithm
- **Classic CS problem**: Familiar to LLMs, tests understanding
- **Varying difficulty**: 3 items (medium) vs 4 items (hard)

**Reasoning Type:** Algorithmic, multi-step
**LLM Difficulty:** Medium to Hard
**CoT Benefit:** Very High (can explain algorithm)

**Verdict:** ✅ **Keep `sort_3` and `sort_4`**
- Different difficulty levels
- Excellent for CoT (LLMs can explain bubble sort)
- Tests algorithmic understanding

---

### ✅ **Multiphase (`multiphase`)** - HIGHLY RECOMMENDED

**Why:**
- Tests **complex multi-phase reasoning**: Multiple distinct phases
- **Planning**: Must understand phase order
- **Excellent for CoT**: LLMs can explain each phase
- **Distractors and traps**: Tests careful reasoning
- **Real-world relevance**: Many problems have phases

**Reasoning Type:** Multi-phase, planning
**LLM Difficulty:** Hard
**CoT Benefit:** Very High (can explain phases)

**Verdict:** ✅ **Keep `multiphase`**
- Best for testing complex reasoning
- Excellent for CoT evaluation
- Can reveal LLM weaknesses in planning

---

### ❌ **Expansion (`expansion`)** - NOT RECOMMENDED

**Why:**
- **Broken**: 0% success rate
- All attempts fail validation
- Not usable until fixed

**Verdict:** ❌ Remove (broken)

---

## Recommended Generator Set

### **Core Set (6 generators):**

1. **`backward_3`** - Medium difficulty, sequential reasoning
2. **`backward_5`** - Hard difficulty, longer sequential reasoning
3. **`backward_7`** - Expert difficulty, complex sequential reasoning
4. **`sort_3`** - Medium difficulty, algorithmic reasoning
5. **`sort_4`** - Hard difficulty, longer algorithmic reasoning
6. **`multiphase`** - Hard difficulty, multi-phase reasoning

### **Optional Addition:**

7. **`palin_3`** - Hard difficulty, pattern recognition (if working)

---

## Reasoning Types Covered

| Generator | Reasoning Type | Difficulty | CoT Benefit |
|-----------|---------------|------------|-------------|
| `backward_3` | Sequential | Medium | High |
| `backward_5` | Sequential | Hard | High |
| `backward_7` | Sequential | Expert | High |
| `sort_3` | Algorithmic | Medium | Very High |
| `sort_4` | Algorithmic | Hard | Very High |
| `multiphase` | Multi-phase | Hard | Very High |
| `palin_3` | Pattern | Hard | Medium |

---

## Why This Set Works for LLM Evaluation

### 1. **Diverse Reasoning Types**
- Sequential (backward)
- Algorithmic (sorting)
- Multi-phase (multiphase)
- Pattern recognition (palindrome)

### 2. **Varying Difficulty**
- Medium: `backward_3`, `sort_3`
- Hard: `backward_5`, `sort_4`, `multiphase`
- Expert: `backward_7`

### 3. **CoT-Friendly**
- All require multi-step reasoning
- LLMs can explain their thought process
- Good for evaluating CoT effectiveness

### 4. **Reveals LLM Weaknesses**
- Sequential reasoning failures
- Algorithmic understanding gaps
- Planning and phase management issues

### 5. **Man vs Machine Potential**
- Sorting: Easy for humans, might be hard for LLMs (algorithmic)
- Multiphase: Easy for humans with planning, hard for LLMs
- Backward: Might be easier for LLMs (pattern matching) than humans

---

## Implementation Recommendation

**Update `main.py` to use only these generators:**

```python
self.generators = [
    # Medium
    ('backward_3', lambda pid: generate_backward_puzzle(pid, 3), 'medium'),
    ('sort_3', lambda pid: generate_sorting_puzzle(pid, 3), 'medium'),
    # Hard
    ('backward_5', lambda pid: generate_backward_puzzle(pid, 5), 'hard'),
    ('sort_4', lambda pid: generate_sorting_puzzle(pid, 4), 'hard'),
    ('multiphase', generate_multiphase_puzzle, 'hard'),
    # Expert
    ('backward_7', lambda pid: generate_backward_puzzle(pid, 7), 'expert'),
    # Optional
    ('palin_3', lambda pid: generate_palindrome_puzzle(pid, 3), 'hard'),
]
```

**Target Distribution:**
- Medium: 30% (backward_3, sort_3)
- Hard: 50% (backward_5, sort_4, multiphase, palin_3)
- Expert: 20% (backward_7)

---

## Expected Benefits

1. **Better LLM Evaluation**: Tests actual reasoning, not just pattern matching
2. **CoT Effectiveness**: Can measure if CoT helps with multi-step reasoning
3. **Man vs Machine**: Can find puzzles where humans/LLMs differ
4. **Focused Dataset**: Smaller, more meaningful dataset
5. **Clearer Analysis**: Easier to understand what reasoning types LLMs struggle with

---

## Next Steps

1. Update generator list in `main.py`
2. Regenerate dataset with focused set
3. Evaluate LLMs on these puzzles
4. Analyze which reasoning types are hardest for LLMs
5. Compare with human performance

