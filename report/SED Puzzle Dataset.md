# SED Puzzle Dataset: Generation Methodology

## Abstract

This document describes the **generation methodology** and **design principles** for the SED puzzle benchmark. For statistical analysis and visualizations, see `notebooks/data_analysis.ipynb`.

---

## 1. Problem Formalization

An SED puzzle is defined as a 3-tuple $\mathcal{P} = (s_0, \mathcal{T}, \varepsilon)$ where:

- $s_0 \in \Sigma^*$ is the initial string
- $\mathcal{T} = \{t_1, ..., t_n\}$ is a set of rewrite rules $\alpha_i \to \beta_i$
- $\varepsilon$ is the goal state (empty string)

A **solution** is a sequence of rule indices $\sigma = [i_1, ..., i_k]$ such that:

$$s_0 \xrightarrow{t_{i_1}} s_1 \xrightarrow{t_{i_2}} \cdots \xrightarrow{t_{i_k}} \varepsilon$$

---

## 2. Generation Methodology

### 2.1 Core Principle: Backward Construction

> **Key Insight**: Generate puzzles from solutions, not solutions from puzzles.

By constructing strings iteratively from $\varepsilon$ (adding segments), the reverse sequence is guaranteed to be a valid solution.

**Theorem**: If $s$ is constructed by prepending/appending segments $\{\alpha_1, ..., \alpha_k\}$ to $\varepsilon$, then applying $\{(\alpha_i, \varepsilon)\}$ in reverse order yields $\varepsilon$.

**Proof**: By induction. Each removal step undoes the corresponding construction step.

### 2.2 Two-Phase Pipeline

```
Phase 1: Pool Generation (250+ candidates)
    → Generator selection (weighted by difficulty)
    → BFS solving (for non-constructive generators)
    → Validation & duplicate detection
    → Difficulty analysis

Phase 2: Representative Selection (100 final)
    → Stratified sampling by difficulty
    → Generator diversity balancing
    → Quality-based ranking
```

### 2.3 Generator Types

| Generator | Reasoning Type | Approach | Success Rate |
|-----------|---------------|----------|--------------|
| `backward_3/5/7` | Sequential | Constructive | 74–97% |
| `concat_2` | Pattern matching | Constructive | 100% |
| `sort_3/4` | Algorithmic | BFS-solved | 12–27% |
| `palin_3` | Symmetry recognition | Constructive | 3–6% |
| `multiphase` | Multi-phase planning | BFS-solved | 2.5% |

---

## 3. Difficulty Quantification

### 3.1 Composite Difficulty Score

$$D = \underbrace{\min(30, |\sigma| \cdot 3)}_{\text{solution length}} + \underbrace{\min(25, \bar{b} \cdot 5)}_{\text{branching}} + \underbrace{\min(20, |s_0| \cdot 0.5)}_{\text{string length}} + \underbrace{\min(15, d \cdot 3)}_{\text{distractors}} + \underbrace{10 \cdot \mathbb{1}[\text{exp}]}_{\text{expansion}}$$

### 3.2 Thresholds

| Level | Score Range | Interpretation |
|-------|-------------|----------------|
| Easy | $D < 25$ | Short solutions, low branching |
| Medium | $25 \leq D < 50$ | Moderate planning required |
| Hard | $50 \leq D < 75$ | Long chains, distractors present |

---

## 4. Data Schema

### 4.1 Puzzle Format

```json
{
  "problem_id": "042",
  "initial_string": "BDCAECAABEABCEBADBCAD",
  "transitions": [
    {"src": "BCAD", "tgt": ""},
    {"src": "CE", "tgt": ""}
  ]
}
```

### 4.2 Solution Format

```json
{
  "problem_id": "042",
  "solution": [0, 8, 1, 5, 4, 3, 2]
}
```

### 4.3 Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `problem_id` | string | 3-digit identifier |
| `generator` | string | Generation strategy |
| `difficulty_score` | float | Composite score [0–100] |
| `difficulty_level` | string | easy / medium / hard |
| `solution_length` | int | Number of steps |
| `branching_factor` | float | Avg. applicable rules per step |
| `num_distractors` | int | Unused rules in solution |

---

## 5. Quality Assurance

### 5.1 Validation Pipeline

1. **Solvability**: BFS solver verifies all puzzles reach $\varepsilon$
2. **Optimality**: Solutions are shortest paths (BFS guarantee)
3. **Uniqueness**: Duplicate detection by initial string
4. **Verification**: Step-by-step execution confirms solution validity

### 5.2 Selection Criteria

- Stratified sampling ensures difficulty coverage
- Generator balancing prevents single-type dominance
- Quality scoring penalizes trivial puzzles (1-step solutions)
- Distractor presence required for majority of puzzles

---

## 6. Implications for LLM Evaluation

### 6.1 Reasoning Modes Tested

| Reasoning Type | Generators | LLM Challenge |
|----------------|------------|---------------|
| **Sequential** | backward_* | Order-dependent rule application |
| **Algorithmic** | sort_* | Iterative refinement (bubble sort) |
| **Multi-phase** | multiphase | Phase transitions, trap avoidance |
| **Pattern** | concat, palin | Direct substring matching |

### 6.2 Hypothesized Difficulty

| Easy for LLMs | Hard for LLMs |
|---------------|---------------|
| `concat_2` (direct match) | `sort_*` (iteration recognition) |
| Short `backward_3` | Long `backward_7` (7+ steps) |
| — | `multiphase` (phase awareness) |

---

## 7. Limitations

- No expert-level puzzles (score ≥ 75) in final dataset
- `expansion` generator broken (0% success rate)
- High correlation between string length and branching factor (r = 0.92)

---

## References

- **Code**: `dataset_generation/`
- **Data**: `data/`
- **Analysis**: `notebooks/data_analysis.ipynb`
