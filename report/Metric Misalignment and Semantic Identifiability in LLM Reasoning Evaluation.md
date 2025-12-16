# Metric Misalignment and Semantic Identifiability in LLM Reasoning Evaluation

## Abstract

Large Language Models (LLMs) increasingly exhibit surface-level competence on structured reasoning benchmarks while failing to demonstrate true semantic understanding. This document formalizes and analyzes this phenomenon through the lens of **metric misalignment** and **identifiability failure**, grounded in observations from **SED-style controlled reasoning benchmarks**. Drawing conceptual inspiration from Stoic philosophy (Marcus Aurelius) and formal tools from planning, statistics, and evaluation theory, we show that common evaluation metrics—validity, progress, verbosity, and efficiency—often fail to identify latent reasoning competence. We provide precise definitions, mathematical intuition, and diagnostic signatures, and argue that many observed "LLM failures" are in fact failures of evaluation design.

---

## 1. Introduction

Recent LLM evaluations frequently report paradoxical behavior:

- High syntactic validity but low correctness
- Increasing progress scores while final answers become wrong
- Verbose, confident, yet semantically incorrect reasoning traces

Rather than attributing these outcomes to anthropomorphic notions such as laziness or hallucination, we frame them as **systematic artifacts of metric design**. This work asks a core scientific question:

> **Does an evaluation metric actually identify latent reasoning competence, or merely reward surface compliance?**

We argue that many existing metrics are **non-identifying**, meaning multiple distinct latent reasoning states map to indistinguishable observed scores.

---

## 2. Stoic Framing as Evaluator Mindset (Conceptual Motivation)

Marcus Aurelius advises expecting flawed behavior, not moralizing it, and not allowing it to corrupt one’s own judgment. Translated into evaluation design:

- Expect hallucinations, confident errors, and partial progress
- Treat failures as diagnostic signals, not moral defects
- Ensure the *metric* is not harmed by bad outputs

This motivates robust evaluation schemes that remain invariant to deception, verbosity, and syntactic polish.

---

## 3. Problem Setting: SED-Style Reasoning Tasks

### 3.1 Task Description (Informal)

- Start with an initial string
- Apply allowed substring-removal operations
- Reach a goal state (typically the empty string)
- Order of operations matters

### 3.2 State–Action Formalization

Let:

- $s_0$ : initial state (string)
- $\mathcal{A}(s)$ : set of allowed actions in state $s$
- $a_i$ : action at step $i$ (substring removal)
- $T$ : true transition function
- $G$ : set of goal states
- $Y = (a_1, a_2, \dots, a_n)$ : model-generated action sequence

A step is **syntactically valid** if:

$$
a_i \in \mathcal{A}(s_{i-1})
$$

The final state after executing the sequence is:

$$
s_n = T(a_n \circ a_{n-1} \circ \dots \circ a_1)(s_0)
$$

---

## 4. Syntax vs Semantics (Core Distinction)

### 4.1 Syntactic Validity

Syntactic validity checks whether each step is *locally allowed*.

> “Can I remove this substring right now?”

This corresponds to grammatical correctness, type safety, or rule compliance.

### 4.2 Semantic Correctness

Semantic correctness evaluates the *global meaning* of the sequence:

> “If I actually execute all these steps in this order, do I solve the task?”

Formally:

$$
\text{Semantic correctness} \iff s_n \in G
$$

Crucially, **local validity does not compose into global correctness**.

---

## 5. Canonical Failure Mode: Valid Steps, Wrong Outcome

It is possible to:

- Execute only syntactically valid actions
- Make apparent local progress
- Yet reach an unsolvable state

This demonstrates that semantic correctness is a *property of the sequence as a computation*, not of individual steps.

---

## 6. Metric Pathologies in LLM Evaluation

We identify three recurring biases.

### 6.1 Length / Verbosity Bias

**Definition:**

> The metric assigns higher scores to longer outputs independent of correctness.

Formal signature:

$$
\frac{\partial \mathbb{E}[\text{Score}]}{\partial |Y|} > 0 \quad (\text{holding correctness fixed})
$$

Common in ROUGE-like and likelihood-based metrics.

---

### 6.2 Syntactic Validity (Surface-Form) Bias

**Definition:**

> The metric rewards well-formed structure without enforcing semantic soundness.

Analogous to:

- Compiling programs that compute the wrong function
- Grammatically perfect but logically invalid proofs

---

### 6.3 Myopic Progress / Proxy Objective Failure

**Definition:**

> The metric rewards short-horizon improvements that are uncorrelated or negatively correlated with final success.

Empirical signature:

$$
\text{corr}(\text{Progress}, \text{Correctness}) < 0
$$

This indicates heuristic misalignment: progress is not a valid distance-to-goal measure.

---

## 7. Unified Theoretical Framing

### 7.1 Metric Misalignment

Collectively, these biases constitute **metric misalignment**: the metric optimizes for proxies rather than task success.

### 7.2 Identifiability Failure

In statistical terms:

> Multiple latent reasoning states induce identical observable metric values.

Thus, latent reasoning competence is **non-identifiable** from the metric alone.

### 7.3 Goodhart’s Law (Strong Form)

> When a measure becomes a target, it ceases to be a good measure.

SED-style benchmarks exhibit multiple Goodhart modes simultaneously.

---

## 8. Diagnostic Table (Paper-Ready)

| Informal Observation            | Technical Term                         |
|--------------------------------|----------------------------------------|
| Rewards verbosity              | Length / Verbosity Bias                |
| Rewards valid-looking steps    | Syntactic Validity / Surface-Form Bias |
| Rewards local progress         | Myopic Reward / Proxy Failure          |
| All combined                   | Metric Misalignment / Non-Identifiability |

---

## 9. Implications for LLM Evaluation

- High validity does **not** imply reasoning
- Progress heuristics must be proven admissible
- Semantic correctness must be evaluated at the sequence level
- Metrics should be adversarially stress-tested against surface compliance

Most importantly:

> **LLMs are not failing the benchmark; the benchmark is revealing where reasoning is not identifiable from surface behavior.**

---

## 10. Conclusion

This document formalizes a key failure mode in modern LLM evaluation: the inability of common metrics to identify semantic reasoning competence. By separating syntax from semantics, local from global correctness, and observables from latent computation, we show that many alarming LLM behaviors are predictable consequences of metric design. Future evaluation must shift from rewarding plausibility to enforcing semantic soundness under true task dynamics.

---

## References (Suggested)

- Goodhart, C. (1975). *Problems of Monetary Management*
- Russell, S., & Norvig, P. *Artificial Intelligence: A Modern Approach*
- Marcus Aurelius. *Meditations*
- Recent work on reasoning benchmarks and proxy objectives in LLMs

