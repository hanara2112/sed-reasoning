# Dataset Generation Improvement Strategy

## Current Situation Analysis

### Problem: Only 85 Puzzles Generated (Expected 100)

**Root Causes Identified:**

1. **Max Attempts Limit Reached**
   - Current: `max_attempts = target_pool_size * 5 = 250 * 5 = 1250`
   - If success rate is low, you hit the limit before reaching 250 puzzles
   - With 85 puzzles, success rate ≈ 85/1250 = **6.8%** (very low!)

2. **BFS Solver Failures**
   - Generators like `sort_3`, `sort_4`, `multiphase`, `expansion` return `None` for solutions
   - They rely on BFS solver with 15s timeout
   - Complex puzzles may timeout or be unsolvable
   - **Impact**: ~40% of generator types fail to produce solutions

3. **Duplicate Detection Too Strict**
   - Checks exact `initial_string` match
   - Even slightly different puzzles with same string are rejected
   - **Issue**: Many valid puzzles rejected as duplicates

4. **Unbalanced Generator Selection**
   - All 12 generators have equal probability (1/12 = 8.3%)
   - But some generators (sorting, multiphase) have much lower success rates
   - **Result**: Too many attempts wasted on hard-to-solve generators

5. **No Difficulty Distribution Control During Generation**
   - Selection happens AFTER pool generation
   - If pool doesn't have enough of each difficulty, selection fails
   - **Current**: Selection takes all available, resulting in 85 instead of 100

6. **No Progress Tracking**
   - Can't see WHY puzzles are being rejected
   - No statistics on failure reasons
   - Hard to debug and improve

---

## Is 85 Puzzles Enough for Benchmarking?

### Short Answer: **Barely, but not ideal**

### Analysis:

**For Prompting Techniques (LLM Evaluation):**

✅ **Minimum Viable:**
- 50-100 puzzles for initial testing
- 85 is acceptable for proof-of-concept

⚠️ **Recommended:**
- **100-200 puzzles** for meaningful statistics
- Allows for proper train/validation/test splits:
  - Train: 60-70% (60-140 puzzles)
  - Validation: 15-20% (15-40 puzzles)
  - Test: 15-20% (15-40 puzzles)

✅ **Ideal:**
- **200-500 puzzles** for robust benchmarking
- Enables:
  - Multiple evaluation runs
  - Statistical significance testing
  - Difficulty-stratified analysis
  - Cross-validation

**Current 85 puzzles:**
- Can do basic evaluation
- Limited statistical power
- Hard to do proper train/test splits
- May not cover all difficulty levels adequately

---

## Improvement Strategy

### Phase 1: Fix Core Generation Issues (High Priority)

#### 1.1 Increase Success Rate

**Problem**: Only 6.8% success rate is too low

**Solutions**:
- **Increase max_attempts**: `target_pool_size * 10` or `* 20` instead of `* 5`
- **Weighted generator selection**: Give higher probability to generators with higher success rates
- **Improve BFS solver**: 
  - Increase timeout for complex puzzles (30s instead of 15s)
  - Add iterative deepening or A* for better performance
  - Cache solved puzzles to avoid re-solving similar ones

#### 1.2 Fix Generator Issues

**Problem**: Some generators always fail

**Solutions**:
- **Improve sorting puzzles**: Make them simpler or provide direct solutions
- **Fix multiphase puzzles**: Ensure they're actually solvable
- **Fix expansion puzzles**: Test and validate generation logic
- **Add fallback**: If BFS fails, try simpler variant of same puzzle type

#### 1.3 Better Duplicate Detection

**Problem**: Too strict duplicate checking

**Solutions**:
- **Normalize strings**: Remove whitespace, case-insensitive comparison
- **Semantic duplicates**: Check if puzzles are functionally equivalent (same transitions, same solution)
- **Allow similar puzzles**: Only reject if puzzle is identical in structure AND solution

#### 1.4 Difficulty-Aware Generation

**Problem**: No control over difficulty distribution during generation

**Solutions**:
- **Track difficulty buckets**: Maintain counts per difficulty level
- **Adaptive generation**: If "hard" bucket is full, reduce probability of hard generators
- **Guarantee minimums**: Ensure at least N puzzles per difficulty before stopping

---

### Phase 2: Enhance Dataset Quality (Medium Priority)

#### 2.1 Better Curation

**Current**: Simple selection by difficulty

**Improvements**:
- **Diversity metrics**: Ensure variety in:
  - String lengths
  - Solution lengths
  - Generator types
  - Transition patterns
- **Quality scoring**: Rank puzzles by:
  - Solution uniqueness
  - Transition complexity
  - Educational value
- **Balanced sampling**: Stratified sampling across multiple dimensions

#### 2.2 Progress Tracking & Debugging

**Add**:
- Real-time statistics on:
  - Success/failure rates per generator
  - Reasons for rejection (timeout, duplicate, invalid, etc.)
  - Current difficulty distribution
  - Estimated time to completion
- Logging system to track what's happening

#### 2.3 Validation & Quality Checks

**Add**:
- Verify all puzzles are solvable
- Check solution uniqueness (multiple solutions?)
- Validate difficulty scores are reasonable
- Ensure no degenerate cases (trivial puzzles)

---

### Phase 3: Scale for Production (Low Priority)

#### 3.1 Parallel Generation

**Current**: Sequential generation (slow)

**Improvement**:
- Multi-threading for puzzle generation
- Parallel BFS solving
- Batch processing

#### 3.2 Incremental Generation

**Current**: Generate all at once

**Improvement**:
- Resume from checkpoint
- Incremental saving
- Add puzzles to existing dataset

#### 3.3 Dataset Versioning

**Add**:
- Version numbers
- Change logs
- Ability to regenerate specific subsets

---

## Recommended Implementation Plan

### Step 1: Quick Wins (1-2 hours)
1. ✅ Increase `max_attempts` to `target_pool_size * 20`
2. ✅ Increase BFS timeout to 30s
3. ✅ Add weighted generator selection
4. ✅ Add progress tracking/logging

### Step 2: Core Fixes (2-4 hours)
1. ✅ Fix duplicate detection (normalize, semantic check)
2. ✅ Implement difficulty-aware generation
3. ✅ Improve generator success rates (fix sorting, multiphase)
4. ✅ Add better error handling

### Step 3: Quality Improvements (4-6 hours)
1. ✅ Enhanced curation with diversity metrics
2. ✅ Quality scoring system
3. ✅ Comprehensive validation
4. ✅ Better statistics and reporting

### Step 4: Scaling (Optional, 4-8 hours)
1. ✅ Parallel generation
2. ✅ Incremental saving
3. ✅ Dataset versioning

---

## Target Metrics

### Success Criteria:

1. **Generation Success Rate**: > 20% (currently 6.8%)
2. **Pool Size**: Consistently generate 250+ puzzles
3. **Final Dataset**: 100-200 puzzles with balanced distribution
4. **Generation Time**: < 30 minutes for 250 puzzles
5. **Quality**: All puzzles verified solvable, diverse, non-trivial

### Difficulty Distribution Target:
- Easy: 25-30%
- Medium: 35-40%
- Hard: 25-30%
- Expert: 5-10%

### Generator Distribution Target:
- Each generator type: 5-15 puzzles
- No single generator > 20% of dataset
- Balanced across all 12 generator types

---

## Code Changes Summary

### Files to Modify:

1. **`main.py`**:
   - Increase max_attempts multiplier
   - Add weighted generator selection
   - Implement difficulty-aware generation
   - Add progress tracking
   - Improve duplicate detection

2. **`solver.py`**:
   - Increase default timeout
   - Add better search strategies
   - Add caching

3. **`generators.py`**:
   - Fix sorting puzzle generation
   - Fix multiphase puzzle generation
   - Fix expansion puzzle generation
   - Add validation to generators

4. **`metrics.py`**:
   - Add quality scoring
   - Add diversity metrics

5. **New file: `tracking.py`**:
   - Progress tracking
   - Statistics collection
   - Logging utilities

---

## Expected Outcomes

### After Phase 1 (Quick Wins):
- Success rate: 6.8% → **15-20%**
- Puzzles generated: 85 → **150-200**
- Generation time: Similar or slightly longer

### After Phase 2 (Core Fixes):
- Success rate: **20-30%**
- Puzzles generated: **250-350**
- Final dataset: **100-150 high-quality puzzles**
- Generation time: **15-25 minutes**

### After Phase 3 (Quality Improvements):
- Success rate: **30-40%**
- Puzzles generated: **300-500**
- Final dataset: **150-200 diverse, high-quality puzzles**
- Better difficulty balance
- More generator diversity

---

## Benchmarking Recommendations

### For Current 85 Puzzles:

**Option 1: Use All 85**
- Single test set
- Good for initial evaluation
- Limited statistical power

**Option 2: Split 85**
- Train: 50 (59%)
- Validation: 17 (20%)
- Test: 18 (21%)
- Better for model development
- Small test set limits evaluation

**Option 3: Generate More**
- Follow improvement strategy
- Target 150-200 puzzles
- Proper 60/20/20 split
- Better for publication-quality results

### Recommended Approach:

1. **Immediate**: Use current 85 for initial testing
2. **Short-term**: Implement Phase 1 improvements, generate 150 puzzles
3. **Long-term**: Implement all phases, generate 200+ puzzles for robust benchmarking

---

## Questions to Consider

1. **What's your primary use case?**
   - Research paper? → Need 150-200+ puzzles
   - Internal testing? → 85-100 is fine
   - Production system? → Need 200-500+

2. **What's your evaluation method?**
   - Single-shot prompting? → Need larger test set
   - Few-shot learning? → Need train/validation splits
   - Fine-tuning? → Need even more data

3. **What's your timeline?**
   - Need results now? → Use 85, improve later
   - Have time? → Implement improvements first

---

## Next Steps

1. **Decide on target dataset size** (100, 150, or 200?)
2. **Prioritize improvements** (which phases to implement?)
3. **Implement Phase 1** (quick wins for immediate improvement)
4. **Test and iterate** (generate, evaluate, improve)
5. **Generate final dataset** (with all improvements)

Would you like me to implement these improvements? I can start with Phase 1 (quick wins) which should immediately improve your success rate and get you closer to 100+ puzzles.

