# All Generator Types Explained

## Overview

There are **12 generator types** organized by difficulty level:

### Easy Generators (25% target)
1. **`concat_2`** - Concatenation with 2 parts
2. **`concat_3`** - Concatenation with 3 parts  
3. **`palin_2`** - Palindrome checker (half-length 2)

### Medium Generators (35% target)
4. **`concat_4`** - Concatenation with 4 parts
5. **`backward_3`** - Backward construction (3 steps)
6. **`sort_3`** - Sorting puzzle (3 items)
7. **`palin_3`** - Palindrome checker (half-length 3)

### Hard Generators (30% target)
8. **`backward_5`** - Backward construction (5 steps)
9. **`sort_4`** - Sorting puzzle (4 items)
10. **`multiphase`** - Multi-phase puzzle

### Expert Generators (10% target)
11. **`backward_7`** - Backward construction (7 steps)
12. **`expansion`** - Expansion puzzle (currently broken)

---

## Detailed Generator Explanations

### 1. Concatenation Puzzles (`concat_2`, `concat_3`, `concat_4`)

**How it works:**
- Creates N random string parts (e.g., "ABC", "DEF", "GHI")
- Concatenates them: `"ABCDEFGHI"`
- Each part can be removed independently
- Solution: Remove parts in reverse order

**Example:**
```
Initial: "ABCDEFGHI"
Parts: ["ABC", "DEF", "GHI"]
Transitions: Remove "ABC", Remove "DEF", Remove "GHI"
Solution: [2, 1, 0]  (remove in reverse order)
```

**Characteristics:**
- ✅ 100% success rate
- ✅ Direct solutions (no BFS needed)
- ✅ Simple and reliable
- Difficulty: Easy to Medium

---

### 2. Backward Construction (`backward_3`, `backward_5`, `backward_7`)

**How it works:**
- Builds puzzle **backwards** from empty string
- Starts with `""`, adds segments one by one
- Creates transitions to remove each segment
- Adds distractors (transitions that don't match)
- Solution: Remove segments in reverse of construction order

**Example (backward_3):**
```
Step 1: "" → "AB"
Step 2: "AB" → "CDAB"  (add to left)
Step 3: "CDAB" → "CDABEF"  (add to right)
Final: "CDABEF"

Transitions: Remove "CD", Remove "AB", Remove "EF", Remove "XYZ" (distractor)
Solution: [2, 1, 0]  (reverse order)
```

**Characteristics:**
- ✅ High success rate (74-97%)
- ✅ Direct solutions
- ✅ Guaranteed solvability (built backwards)
- ✅ Can have distractors
- Difficulty: Medium to Expert (depends on steps)

---

### 3. Palindrome Puzzles (`palin_2`, `palin_3`)

**How it works:**
- Creates a palindrome string with a marker
- Uses marker to check if string is palindrome
- Matches pairs from outside in
- Solution: Convert marker, match pairs, remove marker

**Example (palin_2):**
```
Initial: "10?01"  (palindrome with marker)
Transitions:
  "?" → "!"  (convert marker)
  "0!0" → "!"  (match 0s)
  "1!1" → "!"  (match 1s)
  "!" → ""  (remove marker)

Solution: [0, 1, 2, 3]  (convert, match 0, match 1, remove)
```

**Characteristics:**
- ⚠️ Low success rate (3-6%)
- ✅ Direct solutions
- ⚠️ May fail validation
- Difficulty: Easy to Medium

---

### 4. Sorting Puzzles (`sort_3`, `sort_4`)

**How it works:**
- Creates string with dots (.) and hashes (#)
- Need to sort: all dots left, all hashes right
- Uses bubble-sort style swapping
- Solution: Swap adjacent pairs until sorted, then remove

**Example (sort_3):**
```
Initial: ".##.#."  (shuffled)
Target:  "...###"  (sorted)
Transitions:
  ".#" → "#."  (swap)
  "###..." → ""  (remove when sorted)

Solution: [0, 0, 0, 1]  (swap 3 times, then remove)
```

**Characteristics:**
- ⚠️ Low success rate (13-27%)
- ❌ Requires BFS solving (slow)
- ⚠️ May timeout
- Difficulty: Medium to Hard

---

### 5. Multi-phase Puzzle (`multiphase`)

**How it works:**
- Requires multiple distinct phases
- Phase 1: Convert all A's to B's
- Phase 2: Remove BB pairs
- Phase 3: Remove marker
- Has distractors and traps

**Example:**
```
Initial: "AAAA#"
Transitions:
  "A" → "B"  (convert)
  "BB" → ""  (remove pairs)
  "#" → ""  (remove marker)
  "AB" → "BA"  (distractor)
  "AA" → ""  (trap - leads to odd number)

Solution: [0, 0, 0, 0, 1, 1, 2]  (convert 4 A's, remove 2 BB pairs, remove #)
```

**Characteristics:**
- ⚠️ Very low success rate (2.4%)
- ✅ Direct solutions (recently fixed)
- ⚠️ May fail validation
- Difficulty: Hard

---

### 6. Expansion Puzzle (`expansion`)

**How it works:**
- String must **expand** before contracting
- Start with 2-char seed (e.g., "AB")
- Expand first char: `A` → `AXX`
- Continue expanding until 4 X's
- Remove XXXX, then remove second char

**Example:**
```
Initial: "AB"
Transitions:
  "A" → "AXX"  (expand)
  "XXXX" → ""  (remove 4 X's)
  "B" → ""  (remove second char)
  "XX" → ""  (distractor)

Solution: [0, 0, 1, 2]  (expand twice, remove XXXX, remove B)
```

**Characteristics:**
- ❌ **0% success rate** (BROKEN)
- ❌ All attempts fail validation
- ❌ Solution construction is buggy
- Difficulty: Expert (but doesn't work)

---

## Why Only 3 Types Are Selected?

**Problem:** Your dataset only has:
- `backward_3`: 38 puzzles
- `backward_7`: 35 puzzles
- `concat_2`: 27 puzzles

**Root Causes:**

1. **Quality Score Bias:**
   - Selection sorts by quality score
   - `backward_3/7` and `concat_2` have high quality scores
   - Other generators score lower

2. **Success Rate Bias:**
   - `concat_2`: 100% success → many puzzles in pool
   - `backward_3/7`: 74-97% success → many puzzles in pool
   - `palin_2/3`: 3-6% success → few puzzles in pool
   - `sort_3/4`: 13-27% success → some puzzles in pool
   - `multiphase`: 2.4% success → very few puzzles
   - `expansion`: 0% success → no puzzles

3. **Diversity Logic Too Strict:**
   - `_ensure_diversity()` filters by (string_length_bucket, solution_length, generator)
   - This might eliminate many puzzles
   - Only keeps first occurrence of each combo

4. **Selection Order:**
   - First selects by difficulty (25 easy, 35 medium, 30 hard)
   - Then applies diversity filters
   - If filters are too strict, only common types remain

---

## Fix: Ensure Generator Diversity

The selection should **guarantee minimum puzzles per generator type** to ensure diversity.

