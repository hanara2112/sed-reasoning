# LLM-Focused Generator Selection - Summary

## What Changed

**Removed Generators:**
- ❌ `concat_3`, `concat_4` - Redundant with concat_2
- ❌ `palin_2` - Too easy, redundant with palin_3
- ❌ `expansion` - Broken (0% success rate)

**Kept Generators (8 total):**
- ✅ `concat_2` - Easy, simple pattern matching (baseline/sanity check)
- ✅ `backward_3` - Medium, sequential reasoning
- ✅ `backward_5` - Hard, sequential reasoning
- ✅ `backward_7` - Expert, complex sequential reasoning
- ✅ `sort_3` - Medium, algorithmic reasoning
- ✅ `sort_4` - Hard, algorithmic reasoning
- ✅ `multiphase` - Hard, multi-phase reasoning
- ✅ `palin_3` - Hard, pattern recognition (optional)

## Why This Set is Better for LLM Evaluation

### 1. **Tests Actual Reasoning**
- Sequential reasoning (backward puzzles)
- Algorithmic reasoning (sorting puzzles)
- Multi-phase planning (multiphase puzzles)
- Pattern recognition (palindrome puzzles)

### 2. **CoT-Friendly**
All generators require multi-step reasoning that benefits from Chain-of-Thought:
- **Backward**: "First I need to remove segment X, then Y, then Z..."
- **Sorting**: "I need to swap these pairs to sort the string..."
- **Multiphase**: "Phase 1: Convert A to B. Phase 2: Remove pairs. Phase 3: Remove marker..."

### 3. **Varying Difficulty**
- Easy: `concat_2` (10%) - Baseline/sanity check
- Medium: `backward_3`, `sort_3` (30%)
- Hard: `backward_5`, `sort_4`, `multiphase`, `palin_3` (40%)
- Expert: `backward_7` (20%)

### 4. **Man vs Machine Potential**

**Easy for Humans, Hard for LLMs:**
- **Sorting**: Humans understand bubble sort intuitively, LLMs might overthink
- **Multiphase**: Humans can plan phases, LLMs might get stuck in one phase
- **Palindrome**: Humans see symmetry, LLMs might miss the pattern

**Hard for Humans, Easier for LLMs:**
- **Backward (long)**: LLMs can systematically try all paths, humans might get lost
- **Complex sequences**: LLMs don't get tired, humans make mistakes

## Expected Evaluation Results

### Zero-Shot Performance
- **Low on all types** (~20-30%): LLMs struggle without examples
- **Worst on multiphase**: Requires planning, hard without guidance
- **Best on backward_3**: Shortest sequences, easier to guess

### Few-Shot Performance
- **Improvement on sorting**: Examples help with algorithm understanding
- **Modest improvement on backward**: Pattern matching helps
- **Limited improvement on multiphase**: Still requires planning

### Chain-of-Thought Performance
- **Best on multiphase**: Explicit phase planning helps significantly
- **Good on sorting**: Can explain algorithm step-by-step
- **Moderate on backward**: Helps but can lead to overthinking

## Next Steps

1. **Regenerate dataset** with focused generators
2. **Run LLM evaluations**:
   - Zero-shot prompting
   - Few-shot prompting (3-5 examples)
   - Chain-of-Thought prompting
3. **Compare results** across:
   - Generator types
   - Difficulty levels
   - Prompting strategies
4. **Man vs Machine analysis**:
   - Find puzzles humans solve easily but LLMs struggle with
   - Find puzzles LLMs solve but humans find hard
5. **Document findings**:
   - Which reasoning types are hardest for LLMs?
   - Does CoT help more on certain puzzle types?
   - What patterns emerge in failures?

## Benefits of This Approach

1. **Focused evaluation**: Tests reasoning, not just pattern matching
2. **Baseline included**: Easy puzzles provide sanity check (LLMs should solve easily)
3. **Clearer analysis**: Easier to understand what LLMs struggle with
4. **Better CoT evaluation**: Most puzzles benefit from explicit reasoning
5. **Man vs Machine insights**: Diverse reasoning types reveal differences
6. **Smaller dataset**: 100 puzzles, all meaningful for evaluation

## Why Keep concat_2?

**Baseline/Sanity Check:**
- LLMs should solve these easily (100% success rate expected)
- If LLMs fail on easy puzzles, something is wrong with evaluation setup
- Provides contrast: shows difference between easy pattern matching vs hard reasoning

**Evaluation Value:**
- Can compare: "LLMs solve 100% of easy puzzles but only 30% of hard puzzles"
- Shows that difficulty matters
- Validates that harder puzzles actually test reasoning

