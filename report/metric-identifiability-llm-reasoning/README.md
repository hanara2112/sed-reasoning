# Metric Misalignment and Semantic Identifiability in LLM Reasoning

*Why surface-level metrics fail to capture true reasoning competence*

---

## Overview

These notes analyze why modern LLMs often **appear to reason correctly** while **failing to solve structured tasks**.

We show that common evaluation metrics reward **surface properties**—validity, progress, verbosity—rather than **semantic correctness**, leading to **identifiability failure** of latent reasoning competence.

---

## Core Thesis

> **LLMs are not failing the benchmark; the benchmark is revealing where reasoning is not identifiable from surface behavior.**

When evaluation metrics conflate syntactic validity with semantic correctness, they systematically reward outputs that *look right* over outputs that *are right*.

---

## Grounding

The analysis is grounded in:

- **SED-style controlled reasoning benchmarks** — state-transition tasks with verifiable ground truth
- **Formal semantics** — distinguishing local validity from global correctness
- **Statistical identifiability theory** — when latent competence cannot be recovered from observations
- **Goodhart's Law** — why optimizing metrics corrupts their meaning

---

## Document Structure

| Section                                                | Topic                                      |
| ------------------------------------------------------ | ------------------------------------------ |
| [01. Introduction](docs/01-introduction.md)               | Motivation and core scientific question    |
| [02. Syntax vs Semantics](docs/02-syntax-vs-semantics.md) | The fundamental distinction metrics miss   |
| [03. SED Formalization](docs/03-sed-formalization.md)     | Mathematical framework for reasoning tasks |
| [04. Metric Misalignment](docs/04-metric-misalignment.md) | Three pathologies in evaluation design     |
| [05. Identifiability](docs/05-identifiability.md)         | When competence cannot be observed         |
| [06. Discussion](docs/06-discussion.md)                   | Implications and future directions         |

---

## Key Results

### Diagnostic Table

| Observed Behavior           | Technical Term                |
| --------------------------- | ----------------------------- |
| Rewards longer outputs      | Length / Verbosity Bias       |
| Rewards valid-looking steps | Surface-Form Bias             |
| Rewards local progress      | Myopic Proxy Failure          |
| **All combined**      | **Non-Identifiability** |

### Central Equation

The final state after executing a model's action sequence:

$$
s_n = T(a_n \circ a_{n-1} \circ \dots \circ a_1)(s_0)
$$

**Syntactic validity** ($a_i \in \mathcal{A}(s_{i-1})$) does **not** guarantee **semantic correctness** ($s_n \in G$).

---

## Why This Matters

1. **High validity ≠ reasoning** — Models can produce 100% valid steps and 0% correct solutions
2. **Progress metrics mislead** — Local improvement often anti-correlates with task success
3. **Evaluation must be semantic** — Correctness is a property of the *sequence as computation*, not individual steps

---

## Citation

If referencing these notes:

```bibtex
@misc{metric-identifiability-2025,
  title={Metric Misalignment and Semantic Identifiability in LLM Reasoning},
  author={[Author]},
  year={2025},
  note={Technical notes on LLM evaluation failure modes}
}
```

---

## References

- Goodhart, C. (1975). *Problems of Monetary Management*
- Russell, S., & Norvig, P. *Artificial Intelligence: A Modern Approach*
- Marcus Aurelius. *Meditations*
- Contemporary work on reasoning benchmarks and proxy objectives

---

<div align="center">
<i>Written as a technical note for coursework and research discussion.</i>
</div>
