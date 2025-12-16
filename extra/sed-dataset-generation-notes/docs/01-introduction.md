# Introduction

## Motivation

Evaluating reasoning in Large Language Models requires **controlled benchmarks** with:

1. **Ground truth solutions** — verifiable correctness
2. **Tunable difficulty** — from trivial to expert
3. **Diverse reasoning types** — not just one skill
4. **No data contamination** — novel puzzles

String Edit Distance (SED) puzzles satisfy all criteria.

---

## What is an SED Puzzle?

### Informal Description

- Start with an **initial string** (e.g., `"ABCDEF"`)
- Apply **allowed transitions** (substring replacements)
- Goal: Reach the **empty string** `""`

### Example

**Initial:** `"ABCDEF"`

**Transitions:**
- Rule 0: `"ABC"` → `""`
- Rule 1: `"DEF"` → `""`

**Solution:** `[0, 1]`

```
"ABCDEF" → [Rule 0] → "DEF" → [Rule 1] → "" ✓
```

---

## Formal Definition

### Mathematical Formulation

An SED puzzle instance $\mathcal{P}$ is a 3-tuple:

$$\mathcal{P} = (s_0, \mathcal{T}, s_f)$$

Where:
- $s_0 \in \Sigma^*$ — initial string over alphabet $\Sigma$
- $\mathcal{T} = \{t_1, t_2, ..., t_n\}$ — finite set of transitions
- $s_f = \varepsilon$ — goal state (empty string)

Each transition $t_i = (\alpha_i, \beta_i)$ represents the rewrite rule $\alpha_i \rightarrow \beta_i$.

### Transition Semantics

A transition $t_i$ is **applicable** to string $s$ if $\alpha_i$ is a substring:

$$\text{applicable}(t_i, s) \iff \alpha_i \sqsubseteq s$$

Application replaces the **first occurrence**:

$$\text{apply}(t_i, s) = u \cdot \beta_i \cdot v \quad \text{where } s = u \cdot \alpha_i \cdot v \text{ and } \alpha_i \not\sqsubseteq u$$

### Solution Definition

A solution is a sequence $\sigma = [i_1, i_2, ..., i_k]$ such that:

$$s_0 \xrightarrow{t_{i_1}} s_1 \xrightarrow{t_{i_2}} s_2 \xrightarrow{} \cdots \xrightarrow{t_{i_k}} \varepsilon$$

---

## Why SED Puzzles for LLM Evaluation?

### Advantages

| Property | Benefit for Evaluation |
|----------|----------------------|
| **Deterministic** | No ambiguity in correctness |
| **Verifiable** | Solutions can be mechanically checked |
| **Scalable** | Difficulty is parameterized |
| **Diverse** | Multiple reasoning types via generators |
| **Novel** | Generated puzzles avoid memorization |

### Comparison to Existing Benchmarks

| Benchmark | Ground Truth | Controllable Difficulty | Reasoning Types |
|-----------|--------------|------------------------|-----------------|
| GSM8K | ✓ | ✗ | Math only |
| HumanEval | ✓ | ✗ | Code only |
| ARC | ✓ | ✗ | Pattern only |
| **SED Puzzles** | ✓ | ✓ | Multiple |

---

## State Space Characterization

The SED puzzle induces a **directed graph** $G = (V, E)$:

- $V = \Sigma^*$ — all possible strings (states)
- $E = \{(s, s') : \exists t_i, s' = \text{apply}(t_i, s)\}$ — transitions

### Reachability

**Theorem**: The reachability problem "Is $\varepsilon$ reachable from $s_0$?" is **decidable** for length-monotonic transitions.

**Proof Sketch**: If $|\beta_i| \leq |\alpha_i|$ for all $t_i$, string length is non-increasing. The search space is bounded by $O(|s_0| \cdot |\Sigma|^{|s_0|})$.

### Complexity

Finding an optimal solution (shortest path to $\varepsilon$) is in **PSPACE** for general SED problems. Our restricted setting (mostly deletions) is polynomial.

---

## Research Questions

This work addresses:

1. **Generation**: How do we create puzzles that are guaranteed solvable?
2. **Difficulty**: How do we quantify and control puzzle complexity?
3. **Diversity**: How do we ensure coverage of different reasoning types?
4. **Quality**: How do we select puzzles suitable for LLM evaluation?

---

## Scope of This Document

These notes document:

- The **design decisions** behind each component
- The **experiments** conducted and their outcomes
- The **failures** encountered and how they were resolved
- The **insights** gained about dataset engineering

This is not a research paper but a **technical diary** of the development process.

---

*Next: [Data Structures →](02-data-structures.md)*

