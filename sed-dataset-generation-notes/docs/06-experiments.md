# Experiments & Issues

## Overview

This section documents the **debugging journey** — what went wrong, how it was diagnosed, and how it was fixed.

---

## Issue 1: Only 90 Puzzles Selected (Expected 100)

### Observation

```
Final dataset: 90 puzzles (expected 100)
Difficulty distribution:
  Easy: 25 ✓
  Medium: 35 ✓
  Hard: 30 ✓
  Expert: 0 ✗
```

### Diagnosis

**Root Cause**: Selection logic skipped expert level when bucket was empty.

```python
# Problematic code
for level, count in target_distribution.items():
    candidates = difficulty_buckets[level]
    if len(candidates) == 0:  # ← Expert has 0!
        continue  # Just skips, doesn't redistribute
```

**Math**: 25 + 35 + 30 + 0 = **90 puzzles**

### Why Expert Was Empty

1. **`backward_7`** (labeled 'expert') → All puzzles scored < 75 → Classified as "hard"
2. **`expansion`** (labeled 'expert') → 0% success rate → No puzzles at all

### Fix Applied

Redistribute expert slots when missing:

```python
if len(difficulty_buckets['expert']) == 0:
    expert_slots = 10
    target_distribution['hard'] += 5   # 50%
    target_distribution['medium'] += 3  # 30%
    target_distribution['easy'] += 2    # 20%
```

**Result**: Now generates 100 puzzles ✓

---

## Issue 2: Only 3 Generator Types Selected

### Observation

```
Generator distribution:
  backward_3: 38 puzzles
  backward_7: 35 puzzles
  concat_2: 27 puzzles
  (all others: 0)
```

### Expected

All 8+ generator types should be represented.

### Diagnosis

**Multiple Root Causes**:

1. **Quality Score Bias**
   - Selection sorted by quality score first
   - `backward_*` and `concat_2` have high quality scores
   - Other generators scored lower → filtered out

2. **Success Rate Imbalance**
   ```
   High success → many puzzles:
     concat_2:    100% (427/427)
     backward_3:   97% (361/371)
     backward_7:   74% (1512/2044)
   
   Low success → few puzzles:
     palin_2:      3.3% (2/60)
     palin_3:      5.6% (4/71)
     multiphase:   2.5% (2/83)
     sort_3:      12.7% (20/157)
   ```

3. **Strict Diversity Filter**
   - `_ensure_diversity()` filtered by (string_length_bucket, solution_length, generator)
   - Only kept first occurrence of each combination
   - Eliminated valid puzzles from less common generators

4. **No Minimum Guarantee**
   - Selection didn't ensure minimum puzzles per generator
   - High-quality generators dominated

### Fix Applied

Updated `_balance_strategies()`:

```python
def _balance_strategies(indices, target_count):
    # First pass: ensure minimum per generator
    min_per_generator = target_count // (num_generators * 2)  # ~5 each
    
    selected = []
    for generator in all_generators:
        gen_puzzles = [i for i in indices if metadata[i].generator == generator]
        selected.extend(gen_puzzles[:min_per_generator])
    
    # Second pass: fill remaining with best quality
    remaining = [i for i in indices if i not in selected]
    remaining.sort(key=lambda i: -metadata[i].quality_score)
    selected.extend(remaining[:target_count - len(selected)])
    
    return selected
```

**Result**: All working generator types now represented ✓

---

## Issue 3: Expansion Generator (0% Success)

### Observation

```
expansion: 0/231 (0.0%) - FAILED
All attempts failed validation
```

### Diagnosis

**Bug in Solution Construction**:

The intended behavior:
```
"AB" → [A→AXX] → "AXXB" → [A→AXX] → "AXXXXB" → [XXXX→""] → "AB" → ...
```

**Problem**: After removing `XXXX`, we get `"AB"` — back to start!

The expansion rule `A → AXX` adds X's but leaves A. The solution logic incorrectly assumed A would be consumed.

### Correct Logic (What It Should Be)

```
Initial: "AB"
Goal: String must expand (add X's), then contract (remove X's), then remove B

Correct transitions:
  0: "A" → "XX"   (replace A with XX, not "AXX")
  1: "XXXX" → ""  (remove 4 X's)
  2: "B" → ""     (remove B)

Solution: [0, 0, 1, 2]
Trace: "AB" → "XXB" → "XXXXB" → "B" → "" ✓
```

### Status

**Not fixed** — Generator remains broken. Excluded from final dataset.

### Learning

- Always **verify generated solutions** against expected behavior
- Write **unit tests** for each generator
- **Trace through examples** manually before trusting automation

---

## Issue 4: Fast Execution (Expected Slower)

### Observation

```
Expected: 5-15 minutes
Actual: 2-5 minutes
```

### Question

Why did generation run so fast?

### Diagnosis

**Direct Solutions** — Most generators provide solutions by construction:

| Generator | Solution Type | Time per Puzzle |
|-----------|--------------|-----------------|
| `concat_*` | Direct | ~0.01s |
| `backward_*` | Direct | ~0.02s |
| `palin_*` | Direct | ~0.01s |
| `sort_*` | BFS | ~2-5s |
| `multiphase` | BFS | ~3-8s |

**High Success Rates**:
- concat: 100% → no retries
- backward: 74-97% → few retries

**Solution Caching**:
- Similar puzzles reuse cached solutions
- Reduces BFS calls

**Over-generation**:
- Generated 3,646 puzzles (way more than target 250)
- Hit success quickly due to efficient generators

### Learning

Fast isn't bad! But it meant:
- Most puzzles came from "easy" generators (direct solutions)
- Hard generators (BFS-dependent) were under-represented
- Need to balance generator selection better

---

## Issue 5: Expert Threshold Not Reached

### Observation

```
backward_7: 1512 puzzles → all classified as "hard" (not expert)
Expert threshold: score ≥ 75
Actual scores: mostly 50-70
```

### Diagnosis

**Difficulty Score Components for backward_7**:

| Component | Typical Value | Points |
|-----------|--------------|--------|
| Solution length (7) | 7 × 3 = 21 | 21 |
| Branching factor (~3) | 3 × 5 = 15 | 15 |
| String length (~18) | 18 × 0.5 = 9 | 9 |
| Distractors (~2) | 2 × 3 = 6 | 6 |
| Expansion (false) | 0 | 0 |
| **Total** | | **51** |

**Result**: Score ~51 → "hard" not "expert"

### To Reach Expert (≥75)

Need one of:
- Solution length ≥ 10 steps (30 points)
- Branching factor ≥ 5 (25 points)
- String length ≥ 40 (20 points)
- More distractors (5 = 15 points)
- Enable expansion (+10 points)

### Fix Options

1. **Increase backward_7 steps to 10** → More points from solution length
2. **Add more distractors** → More points from distractors
3. **Enable expansion in some puzzles** → +10 points

### Status

**Partially addressed** — Redistribution ensures 100 puzzles, but true expert puzzles remain rare.

---

## Summary: What I Learned

### Technical Learnings

| Issue | Learning |
|-------|----------|
| Missing puzzles | Always handle edge cases (empty buckets) |
| Generator bias | Explicit diversity constraints are necessary |
| Broken generator | Test each component in isolation |
| Threshold mismatch | Calibrate scoring against actual difficulty |

### Process Learnings

1. **Logging is essential** — Track statistics at every stage
2. **Verify everything** — Don't trust generators without validation
3. **Test incrementally** — Run small batches first
4. **Read the output** — Statistics reveal problems

### Design Learnings

1. **Separate generation from selection** — Easier to debug
2. **Over-generate then filter** — Better quality control
3. **Make diversity explicit** — Don't rely on random chance
4. **Define "success" precisely** — What does a good puzzle look like?

---

## Experiments Conducted

### Experiment 1: Varying Pool Size

| Pool Size | Final Quality | Generation Time |
|-----------|--------------|-----------------|
| 100 | Low (duplicates) | 2 min |
| 250 | Good | 5 min |
| 500 | Excellent | 12 min |

**Finding**: 250 is a good balance between quality and time.

### Experiment 2: BFS Timeout

| Timeout | Success Rate (sort_4) | Quality |
|---------|----------------------|---------|
| 10s | 15% | Lower |
| 30s | 27% | Good |
| 60s | 32% | Marginal improvement |

**Finding**: 30s timeout is optimal — longer timeouts have diminishing returns.

### Experiment 3: Distractor Count

| Distractors | Branching Factor | Human Difficulty |
|-------------|-----------------|------------------|
| 0 | 2.1 | Easy |
| 1-2 | 3.2 | Medium |
| 3-4 | 4.5 | Hard |

**Finding**: 1-2 distractors create meaningful difficulty without overwhelming.

---

## Open Questions

1. **How to create truly expert puzzles?**
   - Current scoring rarely exceeds 75
   - May need new generator types

2. **Is difficulty score calibrated?**
   - Need human validation
   - Current thresholds are arbitrary

3. **Which generators best predict LLM failure?**
   - Need evaluation data
   - Hypothesis: multiphase and sorting are hardest

4. **How to fix expansion generator?**
   - Requires redesigning solution construction
   - Low priority (have enough generators)

---

*Previous: [← Difficulty Metrics](05-difficulty-metrics.md) | Next: [Final Outcomes →](07-outcomes.md)*

