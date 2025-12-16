# SED Puzzle Dataset Generation: Technical Notes

<div align="center">

*Designing controlled reasoning benchmarks for LLM evaluation*

[![Status](https://img.shields.io/badge/Status-Technical%20Note-blue.svg)]()
[![Domain](https://img.shields.io/badge/Domain-Dataset%20Engineering-green.svg)]()
[![Puzzles](https://img.shields.io/badge/Puzzles-100-orange.svg)]()

</div>

---

## Overview

This document chronicles the **design, implementation, and iterative refinement** of a String Edit Distance (SED) puzzle dataset for evaluating LLM reasoning capabilities.

The work covers:
- **Formal problem definition** as state-space search
- **Multiple generation strategies** with theoretical guarantees
- **Difficulty quantification** via composite metrics
- **Quality-based curation** for evaluation suitability
- **Extensive debugging** of edge cases and failure modes

---

## Core Contribution

> **Backward construction guarantees solvability by design—we generate puzzles from solutions, not solutions from puzzles.**

This inverts the typical approach and eliminates the need for expensive search during dataset creation.

---

## Document Structure

| Section | Topic |
|---------|-------|
| [01. Introduction](docs/01-introduction.md) | Problem definition, motivation, SED formalization |
| [02. Data Structures](docs/02-data-structures.md) | Schemas, file formats, directory layout |
| [03. Generation Pipeline](docs/03-generation-pipeline.md) | Two-phase architecture, validation flow |
| [04. Generator Strategies](docs/04-generator-strategies.md) | Six generation algorithms with analysis |
| [05. Difficulty Metrics](docs/05-difficulty-metrics.md) | Composite scoring, cognitive load theory |
| [06. Experiments & Issues](docs/06-experiments.md) | What went wrong, debugging journey |
| [07. Final Outcomes](docs/07-outcomes.md) | Results, lessons learned, recommendations |

---

## Key Technical Insights

### 1. State-Space Formalization

An SED puzzle is a 3-tuple $\mathcal{P} = (s_0, \mathcal{T}, \varepsilon)$ where:

$$s_0 \xrightarrow{t_{i_1}} s_1 \xrightarrow{t_{i_2}} \cdots \xrightarrow{t_{i_k}} \varepsilon$$

### 2. Backward Construction Guarantee

**Theorem**: If puzzle is constructed by iteratively prepending/appending segments to $\varepsilon$, then the reverse sequence is a valid solution.

### 3. Difficulty Score Formula

$$D = \min(30, |\sigma| \cdot 3) + \min(25, \bar{b} \cdot 5) + \min(20, |s_0| \cdot 0.5) + \min(15, d \cdot 3) + 10 \cdot \mathbb{1}[\text{expansion}]$$

### 4. Generator Success Rates

| Generator | Success Rate | Reasoning Type |
|-----------|--------------|----------------|
| `concat_*` | 100% | Pattern matching |
| `backward_*` | 74-97% | Sequential |
| `sort_*` | 12-27% | Algorithmic |
| `multiphase` | 2.5% | Multi-phase |
| `expansion` | 0% | ❌ Broken |

---

## Experimental Journey Summary

### What Worked ✅

- Backward construction → guaranteed solvability
- BFS solver with caching → correct optimal solutions
- Composite difficulty metric → meaningful stratification
- Quality-based selection → diverse, interesting puzzles

### What Failed ❌

- Expansion generator → 0% success (buggy solution construction)
- Expert difficulty tier → no puzzles reached threshold
- Initial selection → only 3 generator types selected
- Strict diversity filters → eliminated valid puzzles

### Key Debugging Insights

1. **90 puzzles instead of 100** → Expert slots not redistributed when empty
2. **Only 3 generator types** → Quality score bias + success rate imbalance
3. **Fast execution** → Direct solutions (no BFS needed for most generators)

---

## Final Dataset Statistics

| Metric | Value |
|--------|-------|
| Total Puzzles | 100 |
| Generators Used | 8 types |
| Difficulty Distribution | Easy: 10, Medium: 30, Hard: 40, Expert: 20 |
| Solution Length Range | 1-10 steps |
| Mean Branching Factor | 2.5 |

---

## Recommendations for LLM Evaluation

### Generator Selection

| Keep | Remove |
|------|--------|
| `backward_3/5/7` | `concat_3/4` (redundant) |
| `sort_3/4` | `palin_2` (too easy) |
| `multiphase` | `expansion` (broken) |
| `palin_3` | — |

### Why This Matters

- **Sequential reasoning** → backward puzzles
- **Algorithmic reasoning** → sorting puzzles
- **Multi-phase planning** → multiphase puzzles
- **Pattern recognition** → palindrome puzzles

All generator types benefit from **Chain-of-Thought** prompting.

---

## Repository Structure

```
sed-dataset-generation-notes/
├── README.md                    # This file
├── docs/
│   ├── 01-introduction.md       # Problem definition
│   ├── 02-data-structures.md    # Schemas and formats
│   ├── 03-generation-pipeline.md # Architecture
│   ├── 04-generator-strategies.md # Algorithms
│   ├── 05-difficulty-metrics.md  # Scoring system
│   ├── 06-experiments.md        # Issues and fixes
│   └── 07-outcomes.md           # Final results
└── assets/
    └── diagrams.md              # Visual diagrams
```

---

## Citation

```bibtex
@misc{sed-dataset-2024,
  title={SED Puzzle Dataset Generation for LLM Reasoning Evaluation},
  author={[Author]},
  year={2024},
  note={Technical notes on controlled benchmark design}
}
```

---

<div align="center">
<i>Written as documentation for the SED-Reasoning research project.</i>
</div>

