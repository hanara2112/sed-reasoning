# Human vs Machine: Cognitive Asymmetries in Reasoning

## Abstract

We analyze systematic differences between human and LLM performance on SED puzzles. Sorting puzzles reveal a striking asymmetry: trivially easy for humans (~100%) but catastrophically hard for LLMs (8-24%). This gap exposes a fundamental difference in reasoning architecture—humans recognize algorithms, LLMs execute isolated rules.

For detailed case studies and visualizations, see `notebooks/human_vs_machine.ipynb`.

---

## 1. Research Question

> Do humans and LLMs exhibit systematically different difficulty profiles on reasoning tasks?

We identify three categories:
1. **Easy Human, Hard LLM** — Exposes LLM-specific weaknesses
2. **Easy for Both** — Shared capabilities
3. **Hard for Both** — Fundamental reasoning limits

---

## 2. Empirical Results

### 2.1 Success Rate by Generator

| Generator | LLM Success | Human (Est.) | Category |
|-----------|-------------|--------------|----------|
| `concat_2` | 86.7% | ~100% | Easy for Both |
| `backward_3` | 58.3% | ~90% | Medium |
| `backward_5` | 28.3% | ~80% | Medium |
| `sort_4` | 24.0% | ~100% | **Easy Human, Hard LLM** |
| `sort_3` | 8.3% | ~100% | **Easy Human, Hard LLM** |
| `backward_7` | 6.1% | 60-80% | Hard for Both |

### 2.2 The Sorting Puzzle Anomaly

Sorting puzzles show the largest human-LLM gap:

$$\Delta_{\text{sort}} = P_{\text{human}} - P_{\text{LLM}} \approx 100\% - 16\% = 84\%$$

This is not explained by difficulty metrics—sorting puzzles are labeled "easy" by the composite score.

---

## 3. Case Analysis

### 3.1 Sorting Puzzles (Easy Human, Hard LLM)

**Problem 059** — 0% LLM Success

```
Initial: "#.##.#.."
Rules:   
  0: ".#" → "#."  (swap adjacent)
  1: "####...." → ""  (delete sorted)
Solution: [0, 0, 0, 0, 1]
```

**Human reasoning (5 seconds):**
1. Recognize pattern: "This is bubble sort"
2. Apply rule 0 repeatedly until sorted
3. Apply rule 1 to delete

**LLM failure modes:**
1. Attempts rule 1 directly (doesn't match)
2. Applies rule 0 once, then stops
3. Produces random rule sequences

**Root cause:** LLMs lack the concept of "repeat until condition."

### 3.2 Concatenation Puzzles (Easy for Both)

**Problem 074** — 87% LLM Success

```
Initial: "EEZCHDRY"
Rules:   
  0: "EEZ" → ""
  1: "CHDRY" → ""
Solution: [0, 1]
```

**Why both succeed:**
- Solution is "visible" in input (direct substring match)
- 2-step solution fits in working memory
- No iteration or planning required

### 3.3 Long-Chain Puzzles (Hard for Both)

**Problem 022** — 0% LLM Success

```
Initial: "BDCAECAABEABCEBADBCAD" (21 chars)
Rules: 9 rules (7 useful, 2 distractors)
Solution: [0, 8, 1, 5, 4, 3, 2] (7 steps)
```

**Why both struggle:**
- 7+ step solutions exceed easy planning
- Distractors create false paths
- Backtracking required

**Key difference:** Humans can solve with patience (5+ minutes). LLMs have one shot.

---

## 4. Cognitive Framework

### 4.1 Capability Comparison

| Capability | Humans | LLMs |
|------------|--------|------|
| **Pattern Recognition** | Recognize algorithms (bubble sort) | Recognize substrings |
| **Iteration** | Understand "repeat until done" | No meta-pattern |
| **Planning** | Backtrack, trial-and-error | Single-shot generation |
| **Abstraction** | Abstract away syntax | Bound to token sequences |

### 4.2 The Iteration Gap

Sorting puzzles require recognizing:

$$\text{repeat } (a \to b) \text{ until } \neg\exists(a)$$

Humans parse this as a single cognitive unit ("bubble sort"). LLMs see individual rule applications without the meta-structure.

### 4.3 Formal Model

Let $\mathcal{A}$ denote algorithm recognition and $\mathcal{R}$ rule application.

**Human reasoning:**
$$\text{Solve} = \mathcal{A} \circ \mathcal{R}^*$$

Humans first recognize the algorithm, then apply rules accordingly.

**LLM reasoning:**
$$\text{Solve} = \mathcal{R}^n$$

LLMs apply rules without algorithm recognition. When $n$ is unknown (iteration required), they fail.

---

## 5. Difficulty Matrix

### 5.1 Two-Dimensional Difficulty

| | Low LLM Difficulty | High LLM Difficulty |
|---|---|---|
| **Low Human Difficulty** | `concat_2` (pattern match) | `sort_3/4` (iteration) |
| **High Human Difficulty** | — | `backward_7` (planning) |

The upper-right quadrant (Easy Human, Hard LLM) is most diagnostic of LLM limitations.

### 5.2 Structural vs. Model Difficulty

Define:
- **Structural difficulty** $D_S$: Based on puzzle features (length, branching)
- **Model difficulty** $D_M$: Empirical LLM failure rate

For sorting puzzles: $D_S \approx 30$ (easy) but $D_M \approx 85$ (hard).

$$\text{Difficulty Gap} = D_M - D_S = 55$$

This gap quantifies the "algorithm blindness" of LLMs.

---

## 6. Implications

### 6.1 For Evaluation

- **Don't trust aggregate accuracy** — Different puzzle types probe different capabilities
- **Use generator-stratified metrics** — Report performance by reasoning type
- **Include "easy human, hard LLM" cases** — Most diagnostic of LLM limitations

### 6.2 For Model Development

- **Iteration is a key gap** — Models need "repeat until" capability
- **Algorithm recognition matters** — Not just rule application
- **Pattern matching is insufficient** — Works for concat, fails for sort

### 6.3 For Benchmark Design

- **Include algorithmic puzzles** — Sorting, iterative refinement
- **Avoid concat-only benchmarks** — Overestimates reasoning capability
- **Human calibration is essential** — Reveals true difficulty asymmetries

---

## 7. Conclusions

1. **Sorting puzzles expose algorithmic blindness** — 84% gap between human and LLM
2. **Concatenation puzzles test pattern matching** — Both succeed (shared capability)
3. **Long-chain puzzles test planning** — Both struggle (fundamental limit)
4. **The core gap is meta-cognition** — Recognizing patterns of patterns

> **Key insight:** LLMs are not failing at reasoning in general—they are failing at a specific type of reasoning: recognizing and executing iterative algorithms.

---

## References

- **Notebook**: `notebooks/human_vs_machine.ipynb`
- **Figures**: `results/success_by_generator.png`, `results/structural_vs_model_difficulty.png`

