# Metric Misalignment

## Overview

This section identifies three recurring pathologies in LLM evaluation metrics, each representing a failure mode where the metric rewards something other than task success.

---

## Pathology 1: Length / Verbosity Bias

### Definition

> The metric assigns higher scores to longer outputs, independent of correctness.

### Formal Signature

$$
\frac{\partial \mathbb{E}[\text{Score}]}{\partial |Y|} > 0 \quad \text{(holding correctness fixed)}
$$

The expected score increases with output length, even when correctness is constant.

### Where It Appears

| Metric Type               | How Length Bias Manifests                    |
| ------------------------- | -------------------------------------------- |
| ROUGE                     | More tokens → more potential matches        |
| Likelihood-based          | Longer sequences accumulate probability mass |
| Character/word counts     | Explicitly length-dependent                  |
| "Reasoning trace" metrics | Longer traces scored as "more reasoning"     |

### Why It's Problematic

- Models learn to be **verbose** rather than **correct**
- Longer wrong answers score higher than shorter correct ones
- Encourages **padding** and **repetition**

### Empirical Signature

If you observe:

- High correlation between output length and score
- Correct short answers scoring below incorrect long answers
- Models "rambling" without improving accuracy

...you likely have length bias.

---

## Pathology 2: Syntactic Validity Bias

### Definition

> The metric rewards well-formed structure without enforcing semantic soundness.

### Analogies

| Domain   | Syntactic Validity Bias                             |
| -------- | --------------------------------------------------- |
| Code     | Program compiles but computes wrong function        |
| Math     | Proof steps are valid but conclusion doesn't follow |
| Planning | Actions are applicable but goal is never reached    |
| Language | Sentence is grammatical but false/meaningless       |

### The "Valid Steps Ratio" Problem

Consider a metric:

$$
\[
\mathrm{VSR}
= \frac{\#\,\mathrm{valid\ steps}}{\#\,\mathrm{total\ steps}}
\]


$$

A model can achieve **100% validity** while achieving **0% correctness**.

**Example:**

- Puzzle has solution length 5
- Model outputs 10 valid but aimless steps
- Valid Steps Ratio: 10/10 = 100%
- Task Correctness: 0%

### Why It's Seductive

- Easy to compute (no execution required)
- Looks rigorous ("we checked every step!")
- Correlates with correctness in easy cases

### Why It Fails

- Validity is **necessary but not sufficient**
- No guarantee that valid steps **compose** into solutions
- Rewards **confident wrong answers**

---

## Pathology 3: Myopic Progress Bias

### Definition

> The metric rewards short-horizon improvements that are uncorrelated—or negatively correlated—with final success.

### The Intuition

Progress metrics assume:

> "Getting closer to the goal is always good."

But in structured tasks, this is often **false**:

- Local progress can lead to **dead ends**
- The "closest" intermediate state may be **unreachable** from the goal
- Greedy optimization fails in non-convex search spaces

### Formal Signature

$$
\text{corr}(\text{Progress}, \text{Correctness}) < 0
$$

If progress and correctness are negatively correlated, the metric is **actively misleading**.

### Example: String Length as Progress

**Metric:** $\text{Progress} = |s_0| - |s_{\text{final}}|$

**Assumption:** Shorter = closer to empty string = better.

**Counterexample:**

```
Initial: "ABAB"
Goal: ""

Path A: "ABAB" → "AB" → ""     (Progress: 4-0 = 4, Correct ✓)
Path B: "ABAB" → "BB" → stuck  (Progress: 4-2 = 2, but Incorrect ✗)
```

A metric rewarding progress would prefer Path A—correctly here. But:

```
Path C: "ABAB" → "BAB" → "BB" → stuck  (Progress: 4-2 = 2)
Path D: "ABAB" → "AABB" → "AB" → ""    (Progress: 4-0 = 4, but intermediate went UP)
```

Path D **increases** string length temporarily but succeeds. A myopic progress metric would penalize it at the intermediate step.

### The Admissibility Problem

In search algorithms, a heuristic $h$ is **admissible** if:

$$
h(s) \leq h^*(s) \quad \forall s
$$

where $h^*(s)$ is the true distance to goal.

Most "progress" metrics in LLM evaluation are **not admissible**:

- They overestimate how "close" a state is
- They can't distinguish promising states from dead ends
- They reward local improvement that leads nowhere

---

## Unified Diagnosis: Metric Misalignment

### Definition

**Metric Misalignment** occurs when:

$$
\underset{Y}{\arg\max} \, M(Y) \neq \underset{Y}{\arg\max} \, \mathbb{1}[\text{correct}(Y)]
$$

The metric-maximizing output is not the correctness-maximizing output.

### Manifestations

| Bias Type | What's Rewarded   | What's Needed            |
| --------- | ----------------- | ------------------------ |
| Length    | More tokens       | Minimal correct solution |
| Validity  | Well-formed steps | Goal-reaching sequence   |
| Progress  | Local improvement | Global success           |

### Root Cause

All three biases stem from **optimizing proxies**:

- Length proxies for "effort"
- Validity proxies for "reasoning"
- Progress proxies for "success"

But proxies are not the target. When they diverge, metrics fail.

---

## Diagnostic Table

| Informal Observation        | Technical Term                |
| --------------------------- | ----------------------------- |
| Rewards longer outputs      | Length / Verbosity Bias       |
| Rewards valid-looking steps | Syntactic Validity Bias       |
| Rewards local improvement   | Myopic Progress Bias          |
| **All combined**      | **Metric Misalignment** |

---

## Implications

1. **Don't trust composite metrics** that mix these biases
2. **Always report correctness** as the primary metric
3. **Stress-test metrics** with adversarial examples (long wrong answers, valid dead-ends)
4. **Be suspicious** of high validity + low accuracy combinations

---

*Previous: [← SED Formalization](03-sed-formalization.md) | Next: [Identifiability →](05-identifiability.md)*
