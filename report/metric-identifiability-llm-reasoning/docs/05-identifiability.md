# Identifiability

## The Core Statistical Problem

### Latent Variables and Observables

In any evaluation, we have:

| Variable | Description | Directly Observable? |
|----------|-------------|---------------------|
| $\theta$ | Latent reasoning competence | No |
| $Y$ | Model output (action sequence) | Yes |
| $M(Y)$ | Metric score | Yes |

The goal is to **infer $\theta$ from $M(Y)$**.

---

## Identifiability Failure

### Definition

A latent variable $\theta$ is **non-identifiable** from observable $M(Y)$ if:

$$\exists \, \theta_1 \neq \theta_2 : \quad P(M(Y) \mid \theta_1) = P(M(Y) \mid \theta_2)$$

Distinct reasoning states produce **indistinguishable** metric distributions.

### In Plain Language

> Multiple models with **different reasoning abilities** can produce the **same metric scores**.

The metric cannot tell them apart.

---

## Examples of Identifiability Failure

### Example 1: High Validity, Low Correctness

| Model | Latent State | Validity Score | Correctness |
|-------|--------------|----------------|-------------|
| A | Understands task | 95% | 90% |
| B | Applies random valid rules | 95% | 10% |

Both achieve **95% validity**. The metric cannot distinguish A from B.

### Example 2: Long Outputs

| Model | Strategy | Length Score | Correctness |
|-------|----------|--------------|-------------|
| A | Concise correct reasoning | Medium | 90% |
| B | Verbose wrong reasoning | High | 10% |

Model B scores **higher** on length despite being wrong more often.

### Example 3: Progress Without Success

| Model | Progress Score | Correctness |
|-------|---------------|-------------|
| A (careful) | 60% | 80% |
| B (greedy) | 90% | 20% |

Model B looks better on progress but fails more often.

---

## The Identifiability Spectrum

### Identifiable Metrics

A metric is **identifying** if:

$$M(Y_1) = M(Y_2) \implies \text{correct}(Y_1) = \text{correct}(Y_2)$$

Equal scores imply equal correctness.

**Example:** Binary correctness (0 or 1) is trivially identifying.

### Partially Identifiable Metrics

Some correctness information is preserved, but noise exists.

**Example:** Metrics that correlate with correctness but have overlap.

### Non-Identifying Metrics

No systematic relationship between metric and correctness.

**Example:** Pure length metrics, validity without semantic checks.

---

## Disagreement Mass Analysis

### Intuition

**Disagreement mass** quantifies how much metric values overlap across different correctness levels.

If correct and incorrect solutions produce **the same metric distribution**, identifiability is zero.

### Formal Definition

Let $M_C$ = metric distribution for correct solutions
Let $M_I$ = metric distribution for incorrect solutions

**Disagreement mass:**

$$D = \int \min(P(M_C), P(M_I)) \, dM$$

- $D = 0$: Perfect separation (fully identifiable)
- $D = 1$: Complete overlap (non-identifiable)

### Interpretation

| Disagreement Mass | Meaning |
|-------------------|---------|
| $D < 0.1$ | Strong identifiability |
| $0.1 \leq D < 0.3$ | Moderate identifiability |
| $0.3 \leq D < 0.5$ | Weak identifiability |
| $D \geq 0.5$ | Identifiability failure |

---

## Goodhart's Law

### Statement

> "When a measure becomes a target, it ceases to be a good measure."

— Charles Goodhart (1975)

### Strong Form

When optimization pressure is applied to a metric:

1. Models exploit **shortcuts** that increase the metric
2. These shortcuts are **uncorrelated** with true competence
3. The metric becomes **adversarially compromised**

### In LLM Context

| Metric | Goodhart Failure Mode |
|--------|----------------------|
| Length | Pad outputs with repetition |
| Validity | Generate valid but aimless steps |
| Progress | Make local improvements that dead-end |
| Perplexity | Memorize training data verbatim |

### SED Benchmarks as Goodhart Detector

SED-style tasks exhibit **multiple Goodhart modes simultaneously**:

- Models can maximize validity without solving tasks
- Models can show progress while moving away from solutions
- Models can be verbose while being wrong

This makes them excellent **stress tests** for evaluation metrics.

---

## Implications for Evaluation Design

### What Must Change

1. **Primary metric must be semantic correctness**
   - Did the sequence reach the goal?
   - This is non-negotiable.

2. **Auxiliary metrics must be validated**
   - Show empirically that they correlate with correctness
   - Report disagreement mass

3. **Metrics must be adversarially tested**
   - Can a model game the metric without solving tasks?
   - If yes, the metric is compromised.

4. **Report identifiability explicitly**
   - How much can we trust the metric to reflect competence?
   - What are the failure modes?

### The Fundamental Tradeoff

| Metric Property | Easy to Compute | Identifies Competence |
|-----------------|-----------------|----------------------|
| Length | ✓ | ✗ |
| Validity | ✓ | Partial |
| Progress | ✓ | Partial |
| **Correctness** | Harder | ✓ |

There is no free lunch. Identifying metrics require **semantic verification**.

---

## Summary

> **Identifiability failure means the metric cannot distinguish reasoning from mimicry.**

When validity, progress, and verbosity are non-identifying, we cannot conclude that high scores reflect understanding. We can only conclude that models produce **outputs that look right**.

This is the central diagnostic: **LLMs may not be reasoning poorly; we may be measuring poorly.**

---

*Previous: [← Metric Misalignment](04-metric-misalignment.md) | Next: [Discussion →](06-discussion.md)*

