# Introduction

## The Paradox of Modern LLM Evaluation

Recent LLM evaluations frequently report paradoxical behavior:

- **High syntactic validity** but **low correctness**
- **Increasing progress scores** while final answers become wrong
- **Verbose, confident**, yet semantically incorrect reasoning traces

These patterns recur across benchmarks: mathematical reasoning, code generation, planning tasks, and structured problem-solving.

---

## Reframing the Problem

Rather than attributing these outcomes to anthropomorphic notions such as "laziness" or "hallucination," we frame them as **systematic artifacts of metric design**.

The models are not malfunctioning. The evaluation is failing to measure what matters.

---

## The Core Scientific Question

> **Does an evaluation metric actually identify latent reasoning competence, or merely reward surface compliance?**

We argue that many existing metrics are **non-identifying**—meaning multiple distinct latent reasoning states map to indistinguishable observed scores.

A model that:
- Understands the task deeply
- Guesses plausibly
- Memorizes surface patterns

...may all receive identical evaluation scores if the metric rewards form over function.

---

## Stoic Framing: The Evaluator's Mindset

*Marcus Aurelius, Meditations:*

> "Begin the morning by saying to thyself, I shall meet with the busy-body, the ungrateful, arrogant, deceitful, envious, unsocial."

Translated into evaluation design:

| Stoic Principle | Evaluation Analog |
|-----------------|-------------------|
| Expect flawed behavior | Expect hallucinations, confident errors, partial progress |
| Do not moralize it | Treat failures as diagnostic signals, not moral defects |
| Do not let it harm you | Ensure the *metric* is not corrupted by bad outputs |

This motivates **robust evaluation schemes** that remain invariant to:
- Deception
- Verbosity
- Syntactic polish
- Surface compliance

---

## What We Will Show

1. **Syntax ≠ Semantics** — Valid steps do not compose into correct solutions
2. **Progress ≠ Success** — Local improvement often leads away from the goal
3. **Observables ≠ Competence** — Metrics fail to identify latent reasoning
4. **Goodhart's Law applies** — When metrics become targets, they lose meaning

---

## Document Scope

These notes are *not* a finished research paper. They are:

- A structured analysis of evaluation failure modes
- Grounded in formal definitions and mathematical intuition
- Applicable to any benchmark with state-transition semantics

The goal is conceptual clarity, not comprehensive empirical validation.

---

*Next: [Syntax vs Semantics →](02-syntax-vs-semantics.md)*

