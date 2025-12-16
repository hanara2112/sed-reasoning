# Syntax vs Semantics

## The Fundamental Distinction

This is the conceptual core of the entire analysis.

| Aspect | Syntax | Semantics |
|--------|--------|-----------|
| **Question** | Is this step allowed? | Does this sequence solve the task? |
| **Scope** | Local (single step) | Global (entire computation) |
| **Verification** | Check rule applicability | Execute and verify final state |
| **Analogy** | Grammar | Meaning |

---

## Syntactic Validity

Syntactic validity checks whether each step is *locally allowed*.

> "Can I apply this operation right now?"

**Formal definition:** An action $a_i$ is syntactically valid in state $s_{i-1}$ if:

$$a_i \in \mathcal{A}(s_{i-1})$$

where $\mathcal{A}(s)$ is the set of allowed actions in state $s$.

### Examples of Syntactic Checks

| Domain | Syntactic Validity |
|--------|-------------------|
| String editing | Substring exists in current string |
| Code execution | Statement compiles / type-checks |
| Proof writing | Inference rule is applicable |
| Planning | Preconditions are satisfied |

---

## Semantic Correctness

Semantic correctness evaluates the *global meaning* of the sequence.

> "If I execute all these steps in order, do I solve the task?"

**Formal definition:** A sequence $Y = (a_1, \ldots, a_n)$ is semantically correct if:

$$s_n \in G$$

where $s_n$ is the final state after execution and $G$ is the set of goal states.

### The Composition Problem

**Critical insight:** Local validity does not compose into global correctness.

$$\forall i: a_i \in \mathcal{A}(s_{i-1}) \quad \not\Rightarrow \quad s_n \in G$$

Every step can be valid, yet the final result can be wrong—or even unreachable.

---

## Canonical Failure Mode

### Example: String Removal Task

**Initial state:** `"ABCABC"`

**Rules:**
- Rule 0: `"AB"` → `""`
- Rule 1: `"CABC"` → `""`
- Rule 2: `"C"` → `""`

**Goal:** Reach empty string `""`

---

**Correct solution:** `[0, 1]`

```
"ABCABC" → [Rule 0] → "CABC" → [Rule 1] → "" ✓
```

---

**Syntactically valid but wrong:** `[0, 0]`

```
"ABCABC" → [Rule 0] → "CABC" → [Rule 0] → "CABC"
```
Wait—Rule 0 (`"AB"`) is not applicable to `"CABC"`. So this is **invalid**.

---

**More subtle failure:** `[0, 2, 2]`

```
"ABCABC" → [Rule 0] → "CABC" → [Rule 2] → "ABC" → [Rule 2] → "AB"
```

Every step is **syntactically valid**. But:
- Final state: `"AB"`
- Goal state: `""`
- **Semantically incorrect** ✗

The model made "progress" (string got shorter) but reached an **unsolvable state**.

---

## Why This Matters for LLM Evaluation

If a metric only checks:
- "Was each step valid?" → High score
- "Did the string get shorter?" → High score

It will **reward** the failing sequence `[0, 2, 2]` despite task failure.

This is precisely what happens with metrics like:
- **Valid Steps Ratio** — counts syntactically correct steps
- **Progress Score** — measures intermediate improvement
- **Length-based metrics** — reward longer outputs

---

## The Core Problem

> **Syntactic validity is necessary but not sufficient for semantic correctness.**

Metrics that conflate these concepts will systematically:
1. Reward confident failures
2. Miss silent successes
3. Fail to discriminate reasoning from pattern-matching

---

## Analogies Across Domains

| Domain | Syntax | Semantics |
|--------|--------|-----------|
| Programming | Code compiles | Code computes correct output |
| Mathematics | Proof steps are valid | Proof establishes theorem |
| Planning | Actions are applicable | Plan achieves goal |
| Language | Sentence is grammatical | Sentence is true/meaningful |

In every case, **local well-formedness ≠ global correctness**.

---

*Previous: [← Introduction](01-introduction.md) | Next: [SED Formalization →](03-sed-formalization.md)*

