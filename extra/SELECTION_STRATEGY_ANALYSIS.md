# Selection Strategy Analysis: Quality vs Diversity

## The Question

**Is it good to force minimum puzzles from each generator type, even if some have low success rates?**

## Trade-offs

### ❌ **Arguments AGAINST Forcing Diversity**

1. **Quality Over Diversity**
   - Low success rate generators (2.5% - 23.5%) might produce lower quality puzzles
   - Forcing inclusion might add puzzles that are:
     - Too hard (unsolvable by LLMs)
     - Buggy or poorly constructed
     - Not representative of the generator's intended difficulty

2. **Skewed Results**
   - Including many puzzles from a broken/buggy generator could skew evaluation
   - If `multiphase` has 2.5% success rate, those 2-3 puzzles might be outliers
   - Not statistically significant for evaluation

3. **Wasted Slots**
   - Using 3-5 slots on a generator that only produced 2 good puzzles
   - Could use those slots for better puzzles from successful generators
   - Reduces overall dataset quality

### ✅ **Arguments FOR Forcing Diversity**

1. **Comprehensive Evaluation**
   - For LLM evaluation, you want to test ALL reasoning types
   - Even if `sort_3` has 11.6% success, those puzzles test algorithmic reasoning
   - Missing a generator type = missing a reasoning type in evaluation

2. **Prevents Dominance**
   - Without diversity, `backward_3/7` would dominate (97% and 75% success)
   - Dataset would be biased toward sequential reasoning
   - Wouldn't test algorithmic, multi-phase, or pattern recognition

3. **Low Success ≠ Low Quality**
   - Low success rate might mean:
     - Generator is harder to solve (good for evaluation!)
     - Generator produces more complex puzzles (valuable!)
     - Not necessarily that puzzles are bad

## The Real Issue

Looking at your statistics:
```
multiphase:  2.5% success (2/81)   → Only 2 puzzles in pool!
palin_3:     3.6% success (4/112)  → Only 4 puzzles in pool!
sort_3:     11.6% success (20/172) → Only 20 puzzles in pool!
sort_4:     23.5% success (69/294) → 69 puzzles in pool
```

**Problem**: Some generators produce so few puzzles that forcing 3-5 from each might:
- Use ALL available puzzles from that generator (no selection)
- Include puzzles that might not be the best quality
- Not have enough for statistical significance

## Better Approach: Balanced Selection

### Option 1: **Quality-First with Diversity Floor** (Recommended)

```python
# 1. Select best quality puzzles first (top 70-80%)
# 2. Ensure minimum diversity (at least 1-2 from each generator)
# 3. Fill remaining with best available
```

**Pros:**
- Prioritizes quality
- Ensures all reasoning types are represented
- Flexible: allows some generators to have fewer if they truly can't produce enough

**Cons:**
- Some generators might only get 1-2 puzzles (not statistically significant)

### Option 2: **Diversity-First with Quality Threshold**

```python
# 1. Ensure minimum from each generator (if they meet quality threshold)
# 2. Only include generators that produced at least N good puzzles
# 3. Fill remaining with best quality
```

**Pros:**
- Ensures diversity
- Filters out truly broken generators
- Better quality control

**Cons:**
- Might exclude some generators entirely if they can't meet threshold

### Option 3: **Weighted Selection** (Best for LLM Evaluation)

```python
# 1. Calculate weights based on:
#    - Generator success rate (higher = more weight)
#    - Generator importance for evaluation (all equal)
#    - Quality scores
# 2. Select proportionally based on weights
```

**Pros:**
- Balances quality and diversity
- More puzzles from successful generators
- Still ensures all types are represented
- Mathematically sound

**Cons:**
- More complex to implement

## Recommendation for LLM Evaluation

**Use Option 1: Quality-First with Diversity Floor**

**Reasoning:**
1. **For LLM evaluation, you need ALL reasoning types**
   - Even 1-2 puzzles from each type is valuable
   - Tests if LLMs can handle that reasoning type at all
   - Better than missing a reasoning type entirely

2. **Quality matters, but diversity matters more for evaluation**
   - A few lower-quality puzzles from each type is better than missing types
   - You can analyze per-generator performance separately
   - Outliers can be identified and excluded in analysis

3. **Low success rate might indicate valuable difficulty**
   - If `multiphase` is hard to generate, it might be hard to solve (good test!)
   - If `sort_3` has low success, those puzzles might be genuinely challenging

## Implementation Suggestion

```python
# Minimum per generator: 1-2 (not 3-5)
# This ensures representation without forcing too many low-quality puzzles
min_per_generator = max(1, target_count // (len(all_generators) * 3))

# Quality threshold: Only include if generator produced at least N puzzles
min_pool_size = 5  # Generator must have at least 5 puzzles in pool

# Then fill remaining with best quality
```

This way:
- Every generator gets at least 1-2 puzzles (representation)
- Only generators with enough puzzles in pool are included (quality control)
- Remaining slots go to best quality puzzles (overall quality)

## For Your Specific Case

Given your statistics:
- ✅ **Include**: `concat_2`, `backward_3/5/7`, `sort_3/4` (all have enough in pool)
- ⚠️ **Conditional**: `multiphase` (only 2 puzzles - use both if good quality)
- ⚠️ **Conditional**: `palin_3` (only 4 puzzles - use 2-3 if good quality)

**Recommendation**: 
- Set minimum to 1-2 per generator (not 3-5)
- Allow generators with very few puzzles to contribute what they have
- Fill remaining with best quality from successful generators

This balances quality and diversity appropriately for LLM evaluation.

