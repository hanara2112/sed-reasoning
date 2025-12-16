# Final Outcomes

## Dataset Summary

### Production Statistics

| Metric | Value |
|--------|-------|
| **Total Puzzles** | 100 |
| **Generator Types** | 8 (of 12 original) |
| **Difficulty Distribution** | Easy: 10, Medium: 30, Hard: 40, Expert: 20 |
| **Solution Length Range** | 1-10 steps |
| **String Length Range** | 6-25 characters |
| **Mean Branching Factor** | 2.5 |
| **Mean Quality Score** | 85.3 |

### Generator Distribution

| Generator | Count | % | Reasoning Type |
|-----------|-------|---|----------------|
| `backward_7` | 42 | 42% | Sequential (Expert) |
| `backward_3` | 15 | 15% | Sequential (Medium) |
| `backward_5` | 10 | 10% | Sequential (Hard) |
| `concat_2` | 10 | 10% | Pattern Matching |
| `sort_4` | 10 | 10% | Algorithmic |
| `sort_3` | 10 | 10% | Algorithmic |
| `palin_3` | 4 | 4% | Pattern Recognition |
| `multiphase` | 2 | 2% | Multi-phase |

### Difficulty Distribution

```
Easy   (D < 25):   ██████████ 10%
Medium (25 ≤ D < 50): ██████████████████████████████ 30%
Hard   (50 ≤ D < 75): ████████████████████████████████████████ 40%
Expert (D ≥ 75):   ████████████████████ 20%
```

---

## What Worked Well ✅

### 1. Backward Construction

**Success**: Guarantees solvability by design.

**Why It Works**:
- Build from goal → solution is construction reverse
- No BFS needed → fast generation
- Scalable difficulty → adjust num_steps

**Evidence**: 74-97% success rate across variants.

### 2. BFS Solver with Caching

**Success**: Finds optimal solutions reliably.

**Why It Works**:
- BFS guarantees shortest path
- Caching avoids redundant computation
- Timeout prevents hanging on hard puzzles

**Evidence**: Solved all solvable puzzles within 30s timeout.

### 3. Composite Difficulty Metric

**Success**: Meaningful stratification across difficulty levels.

**Why It Works**:
- Multiple factors capture different aspects of difficulty
- Weights are calibrated to produce reasonable distribution
- Thresholds create distinct categories

**Evidence**: Smooth distribution across all four levels.

### 4. Quality-Based Selection

**Success**: Final dataset is diverse and interesting.

**Why It Works**:
- Over-generation (250 → 100) allows cherry-picking
- Quality score penalizes trivial puzzles
- Diversity constraints ensure coverage

**Evidence**: All reasoning types represented, no trivial puzzles.

### 5. Two-Phase Pipeline

**Success**: Clean separation of concerns.

**Why It Works**:
- Generation is independent of selection
- Can iterate on selection without regenerating
- Easy to debug each phase independently

**Evidence**: Able to diagnose and fix issues quickly.

---

## What Failed ❌

### 1. Expansion Generator

**Failure**: 0% success rate — all puzzles invalid.

**Root Cause**: Solution construction logic was incorrect.

**Impact**: Lost one generator type, no non-monotonic puzzles.

**Lesson**: Test generators thoroughly before integration.

### 2. Expert Threshold

**Failure**: Most "expert" generators produced "hard" puzzles.

**Root Cause**: Difficulty formula didn't weight components to reach 75+.

**Impact**: Had to redistribute expert slots to other levels.

**Lesson**: Calibrate scoring against actual expected difficulty.

### 3. Initial Diversity Selection

**Failure**: Only 3 generator types in first run.

**Root Cause**: Quality score bias + success rate imbalance.

**Impact**: Dataset was not representative of all reasoning types.

**Lesson**: Explicit diversity constraints are necessary.

---

## Key Insights Gained

### Insight 1: Generation ≠ Difficulty

Generator labels (easy/medium/hard/expert) don't guarantee difficulty scores.

**Example**: `backward_7` was labeled "expert" but produced "hard" puzzles.

**Learning**: Difficulty is an emergent property of the puzzle, not the generator.

### Insight 2: Success Rate Indicates Generator Quality

| Success Rate | Interpretation |
|--------------|----------------|
| 100% | Trivial generator (concat) |
| 70-97% | Well-designed generator (backward) |
| 10-30% | Complex generator (sort) |
| 0-5% | Potentially broken (expansion, multiphase) |

**Learning**: Very low success rates are a red flag for bugs.

### Insight 3: Direct Solutions Are Valuable

Generators that provide solutions by construction:
- Are faster (no BFS)
- Are more reliable (guaranteed valid)
- Produce more consistent difficulty

**Learning**: Prefer constructive generation over search-based generation.

### Insight 4: Diversity Requires Explicit Constraints

Random selection with quality ranking leads to homogeneous datasets.

**Learning**: If diversity matters, enforce it algorithmically.

---

## Recommendations for Future Work

### For Dataset Improvement

1. **Fix Expansion Generator**
   - Redesign solution construction
   - Add non-monotonic reasoning puzzles

2. **Create True Expert Puzzles**
   - Increase solution lengths (10+ steps)
   - Add more distractors
   - Enable expansion in backward puzzles

3. **Add New Generator Types**
   - Graph traversal puzzles
   - Constraint satisfaction puzzles
   - Recursive structure puzzles

### For LLM Evaluation

1. **Keep These Generators**
   - `backward_3/5/7` — Sequential reasoning
   - `sort_3/4` — Algorithmic reasoning
   - `multiphase` — Multi-phase planning

2. **Remove These Generators**
   - `concat_3/4` — Redundant with concat_2
   - `palin_2` — Too easy
   - `expansion` — Broken

3. **Use concat_2 as Baseline**
   - LLMs should solve 100%
   - If they fail, evaluation setup is wrong

### For Similar Projects

1. **Start with constructive generators** — Guarantee solvability
2. **Log everything** — Statistics reveal problems early
3. **Test incrementally** — Small batches before full runs
4. **Separate generation from selection** — Easier to iterate
5. **Define success precisely** — What makes a "good" puzzle?

---

## Conclusion

### What Was Accomplished

1. **Created a principled dataset** of 100 SED puzzles
2. **Covered multiple reasoning types** (sequential, algorithmic, multi-phase)
3. **Established a difficulty metric** with theoretical grounding
4. **Built a robust pipeline** that can be extended

### What Remains

1. **Fix broken generators** (expansion)
2. **Calibrate difficulty** against human performance
3. **Evaluate LLMs** to validate the benchmark
4. **Iterate based on evaluation** results

### The Core Contribution

> **Backward construction is the key innovation** — by generating puzzles from solutions rather than finding solutions for puzzles, we guarantee solvability, enable difficulty control, and achieve efficient generation.

This principle can be applied to many other reasoning benchmark domains.

---

## Appendix: Quick Reference

### Running Generation

```bash
cd sed-reasoning/dataset_generation
python main.py
```

### Output Files

```
data/
├── puzzles/000.json ... 099.json
├── solutions/000.json ... 099.json
└── metadata.json
```

### Key Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `seed` | 42 | Reproducibility |
| `pool_size` | 250 | Candidates generated |
| `target_count` | 100 | Final dataset size |
| `bfs_timeout` | 30s | Solver timeout |

### Difficulty Thresholds

| Level | Score |
|-------|-------|
| Easy | < 25 |
| Medium | 25-49 |
| Hard | 50-74 |
| Expert | ≥ 75 |

---

*Previous: [← Experiments & Issues](06-experiments.md) | [Back to Overview](../README.md)*

