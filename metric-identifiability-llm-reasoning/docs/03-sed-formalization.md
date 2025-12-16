# SED Formalization

## Problem Setting: SED-Style Reasoning Tasks

SED (String Edit Distance) puzzles provide an ideal testbed for studying reasoning evaluation because:

1. **Ground truth exists** — Solutions are verifiable
2. **Steps are discrete** — Each action is clearly defined
3. **Semantics are deterministic** — No ambiguity in execution
4. **Complexity is controllable** — Difficulty can be systematically varied

---

## Informal Task Description

- Start with an **initial string**
- Apply **allowed substring-removal operations** (transitions)
- Reach a **goal state** (typically the empty string)
- **Order of operations matters**

---

## State-Action Formalization

### Definitions

| Symbol | Meaning |
|--------|---------|
| $s_0$ | Initial state (string) |
| $s_i$ | State after step $i$ |
| $\Sigma^*$ | Set of all strings over alphabet $\Sigma$ |
| $\mathcal{A}(s)$ | Set of allowed actions in state $s$ |
| $a_i$ | Action taken at step $i$ |
| $T$ | Transition function |
| $G$ | Set of goal states |
| $Y$ | Model-generated action sequence |

---

### Action Applicability

An action $a = (\alpha \to \beta)$ (replace substring $\alpha$ with $\beta$) is **applicable** in state $s$ if and only if $\alpha$ is a substring of $s$:

$$a \in \mathcal{A}(s) \iff \alpha \sqsubseteq s$$

where $\sqsubseteq$ denotes the substring relation.

---

### Transition Function

The transition function $T$ maps state-action pairs to successor states:

$$T(s, a) = \begin{cases} 
s' & \text{if } a \in \mathcal{A}(s) \\
\text{undefined} & \text{otherwise}
\end{cases}$$

For string replacement $a = (\alpha \to \beta)$:

$$s' = u \cdot \beta \cdot v \quad \text{where } s = u \cdot \alpha \cdot v \text{ and } \alpha \not\sqsubseteq u$$

(Replace the **first occurrence** of $\alpha$.)

---

### Sequence Execution

Given an action sequence $Y = (a_1, a_2, \ldots, a_n)$, the final state is:

$$s_n = T(a_n \circ a_{n-1} \circ \cdots \circ a_1)(s_0)$$

This can be computed iteratively:

$$s_i = T(s_{i-1}, a_i) \quad \text{for } i = 1, \ldots, n$$

---

## Validity and Correctness

### Syntactic Validity (Per-Step)

Step $i$ is **syntactically valid** if the action is applicable:

$$\text{valid}(a_i, s_{i-1}) \iff a_i \in \mathcal{A}(s_{i-1})$$

### Sequence Validity

A sequence $Y$ is **fully valid** if every step is valid:

$$\text{valid}(Y) \iff \forall i \in [1,n]: a_i \in \mathcal{A}(s_{i-1})$$

### Semantic Correctness

A sequence $Y$ is **semantically correct** if it reaches a goal state:

$$\text{correct}(Y) \iff s_n \in G$$

---

## The Key Non-Implication

$$\text{valid}(Y) \not\Rightarrow \text{correct}(Y)$$

This is the fundamental gap that many evaluation metrics fail to address.

---

## Concrete Example

### Puzzle Instance

- **Initial:** $s_0 = $ `"AAAA#"`
- **Transitions:**
  - $t_0$: `A → B`
  - $t_1$: `BB → ""`
  - $t_2$: `# → ""`
  - $t_3$: `AA → ""` (trap!)
- **Goal:** $G = \{\varepsilon\}$ (empty string)

### Correct Solution

$$Y_{\text{correct}} = [0, 0, 0, 0, 1, 1, 2]$$

**Trace:**
```
"AAAA#" → [A→B] → "BAAA#"
"BAAA#" → [A→B] → "BBAA#"
"BBAA#" → [A→B] → "BBBA#"
"BBBA#" → [A→B] → "BBBB#"
"BBBB#" → [BB→""] → "BB#"
"BB#" → [BB→""] → "#"
"#" → [#→""] → "" ✓
```

### Trap Path (Valid but Wrong)

$$Y_{\text{trap}} = [3, 3]$$

**Trace:**
```
"AAAA#" → [AA→""] → "AA#"
"AA#" → [AA→""] → "#"
"#" → ??? (no applicable rule leads to "")
```

Wait—Rule 2 (`# → ""`) applies!

$$Y_{\text{trap}} = [3, 3, 2]$$

```
"AAAA#" → [AA→""] → "AA#" → [AA→""] → "#" → [#→""] → "" ✓
```

This also works! So the trap isn't universal. Let's try with $s_0 = $ `"AAA#"`:

$$Y = [3]$$
```
"AAA#" → [AA→""] → "A#"
```

Now stuck: neither `A→B` (produces `B#`), nor `AA→""` (no `AA`), nor `BB→""` (no `BB`), nor `#→""` (leaves `A`).

**The trap rule is dangerous when the count is odd.**

---

## Why Formalization Matters

1. **Precision** — Ambiguity-free definitions enable rigorous analysis
2. **Generality** — Framework applies to any state-transition task
3. **Verification** — Correctness can be mechanically checked
4. **Metric Design** — Reveals what metrics must capture (and what they miss)

---

## Mathematical Maturity Signal

The formalization demonstrates:

- Familiarity with **state-space search**
- Understanding of **transition semantics**
- Ability to **separate local from global** properties
- Recognition that **computation ≠ observation**

This is the foundation for the metric analysis that follows.

---

*Previous: [← Syntax vs Semantics](02-syntax-vs-semantics.md) | Next: [Metric Misalignment →](04-metric-misalignment.md)*

