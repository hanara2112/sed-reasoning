# Generator Diversity Fix

## Problem

**Only 3 generator types were being selected:**
- `backward_3`: 38 puzzles
- `backward_7`: 35 puzzles  
- `concat_2`: 27 puzzles

**Missing generators:**
- `concat_3`, `concat_4`
- `palin_2`, `palin_3`
- `backward_5`
- `sort_3`, `sort_4`
- `multiphase`
- `expansion` (broken anyway)

## Root Causes

### 1. Quality Score Bias
- Selection sorted by quality score first
- `backward_3/7` and `concat_2` have high quality scores
- Other generators scored lower → filtered out

### 2. Success Rate Imbalance
- **High success** → many puzzles in pool:
  - `concat_2`: 100% (427/427)
  - `backward_3`: 97.3% (361/371)
  - `backward_7`: 74.0% (1512/2044)
  
- **Low success** → few puzzles in pool:
  - `palin_2`: 3.3% (2/60)
  - `palin_3`: 5.6% (4/71)
  - `multiphase`: 2.4% (2/83)
  - `sort_3`: 12.7% (20/157)
  - `sort_4`: 27.1% (67/247)

### 3. Diversity Logic Too Strict
- `_ensure_diversity()` filtered by (string_length_bucket, solution_length, generator)
- Only kept first occurrence of each combo
- Eliminated many puzzles from less common generators

### 4. No Minimum Guarantee
- Selection didn't ensure minimum puzzles per generator
- Could select 0 puzzles from some generators
- Only quality score mattered

## Fix Applied

### Updated `_balance_strategies()`:

**Before:**
- Just sorted by strategy diversity
- No minimum guarantee per generator
- Could select 0 from some generators

**After:**
1. **First pass**: Ensure minimum puzzles per generator
   - Calculates `min_per_generator = target_count / (num_generators * 2)`
   - For 100 puzzles with ~10 generators: ~5 puzzles minimum per generator
   - Selects at least this many from each generator type

2. **Second pass**: Fill remaining slots
   - Uses best quality puzzles from remaining pool
   - Still prioritizes diversity

**Result:**
- Every generator type gets at least some puzzles
- Better diversity across all 12 generator types
- Still maintains quality (best puzzles selected)

## Expected Outcome

**Before:**
```
backward_3: 38
backward_7: 35
concat_2: 27
Total: 100 (only 3 types)
```

**After (expected):**
```
concat_2: ~10-15
concat_3: ~5-10
concat_4: ~5-10
backward_3: ~10-15
backward_5: ~5-10
backward_7: ~10-15
palin_2: ~3-5
palin_3: ~3-5
sort_3: ~3-5
sort_4: ~5-8
multiphase: ~3-5
Total: 100 (all 11 working types represented)
```

## Additional Improvements

1. **Added generator distribution printout** after selection
   - Shows how many puzzles from each generator
   - Helps verify diversity

2. **Less strict diversity filtering**
   - Only applies `_ensure_diversity()` if we have more than target_count
   - Prevents over-filtering

## Next Steps

1. **Run generation again** to see improved diversity
2. **Check generator distribution** in output
3. **Adjust minimums** if needed (can tune `min_per_generator` calculation)

## Notes

- `expansion` generator still broken (0% success)
- Will be excluded until fixed
- Other 11 generators should all be represented

