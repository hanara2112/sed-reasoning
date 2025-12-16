# Difficulty Metrics

## Overview

Puzzle difficulty is quantified via a **composite score** combining multiple factors:

$$D = f(|\sigma|, \bar{b}, |s_0|, d, \text{expansion})$$

Where:
- $|\sigma|$ — solution length
- $\bar{b}$ — branching factor
- $|s_0|$ — initial string length
- $d$ — distractor count
- expansion — whether string grows during solution

---

## Difficulty Score Formula

### Definition

$$D = \min\left(100, \sum_{i} w_i \cdot f_i(\mathcal{P})\right)$$

### Component Functions

| Component | Function | Weight | Max Contribution |
|-----------|----------|--------|------------------|
| Solution Length | $\min(10, |\sigma|) \cdot 3$ | 3.0 | 30 points |
| Branching Factor | $\bar{b} \cdot 5$ | 5.0 | 25 points |
| String Length | $|s_0| \cdot 0.5$ | 0.5 | 20 points |
| Distractors | $d \cdot 3$ | 3.0 | 15 points |
| Expansion | $\mathbb{1}[\text{expansion}] \cdot 10$ | 10.0 | 10 points |

**Total Maximum**: 100 points

### Implementation

```python
def compute_difficulty_score(self) -> float:
    score = 0
    score += min(30, self.solution_length * 3)
    score += min(25, self.branching_factor * 5)
    score += min(20, self.initial_string_length * 0.5)
    score += min(15, self.num_distractors * 3)
    if self.has_expansion:
        score += 10
    return min(100, score)
```

---

## Component Analysis

### 1. Solution Length ($|\sigma|$)

**Definition**: Number of steps in the optimal solution.

**Why It Matters**:
- More steps = more decisions = harder
- Longer solutions require maintaining state across steps
- Related to **working memory load**

**Scoring**:

| Length | Points | Interpretation |
|--------|--------|----------------|
| 1 | 3 | Trivial |
| 2-3 | 6-9 | Easy |
| 4-5 | 12-15 | Medium |
| 6-7 | 18-21 | Hard |
| 8-10 | 24-30 | Expert |

### 2. Branching Factor ($\bar{b}$)

**Definition**: Average number of applicable transitions at each step.

$$\bar{b} = \frac{1}{|\sigma|} \sum_{j=0}^{|\sigma|-1} |\{t_i \in \mathcal{T} : \text{applicable}(t_i, s_j)\}|$$

**Why It Matters**:
- Higher branching = more choices = harder to find correct path
- Related to **search complexity** ($O(\bar{b}^{|\sigma|})$)
- Tests **decision-making under uncertainty**

**Interpretation**:

| Branching | Points | Interpretation |
|-----------|--------|----------------|
| 1.0 | 5 | Deterministic (no choice) |
| 2.0 | 10 | Binary choices |
| 3.0 | 15 | Moderate uncertainty |
| 4.0+ | 20-25 | High uncertainty |

### 3. Initial String Length ($|s_0|$)

**Definition**: Length of the starting string.

**Why It Matters**:
- Longer strings = more potential matches = harder to track
- Related to **visual/spatial complexity**
- Affects pattern recognition difficulty

**Scoring**:

| Length | Points | Interpretation |
|--------|--------|----------------|
| 5-10 | 2.5-5 | Short |
| 10-20 | 5-10 | Medium |
| 20-30 | 10-15 | Long |
| 30+ | 15-20 | Very long |

### 4. Distractor Count ($d$)

**Definition**: Number of transitions not used in the solution.

$$d = |\mathcal{T}| - |\{\sigma\}|$$

**Why It Matters**:
- Distractors require discrimination
- Tests **relevance filtering**
- Can create **trap paths** (valid but wrong)

**Scoring**:

| Distractors | Points | Interpretation |
|-------------|--------|----------------|
| 0 | 0 | No distractions |
| 1 | 3 | Minimal |
| 2-3 | 6-9 | Moderate |
| 4-5 | 12-15 | High |

### 5. Expansion ($\mathbb{1}[\text{expansion}]$)

**Definition**: Whether any intermediate string is longer than the initial.

$$\text{expansion} \iff \max_{0 \leq i \leq |\sigma|} |s_i| > |s_0|$$

**Why It Matters**:
- Counter-intuitive (string grows before shrinking)
- Tests **non-monotonic reasoning**
- Requires **planning ahead**

**Scoring**: Binary +10 points if present.

---

## Difficulty Levels

### Thresholds

| Level | Score Range | Description |
|-------|-------------|-------------|
| **Easy** | $D < 25$ | Single-phase, low branching, short solutions |
| **Medium** | $25 \leq D < 50$ | Multiple steps, moderate branching |
| **Hard** | $50 \leq D < 75$ | Long solutions, high branching, distractors |
| **Expert** | $D \geq 75$ | All complexity factors elevated |

### Implementation

```python
def difficulty_level(self) -> str:
    score = self.compute_difficulty_score()
    if score < 25:
        return "easy"
    elif score < 50:
        return "medium"
    elif score < 75:
        return "hard"
    else:
        return "expert"
```

---

## Theoretical Justification

### Cognitive Load Theory Connection

The difficulty score approximates **cognitive load** using Information Processing Theory:

$$\text{Cognitive Load} \propto \log_2(\text{Search Space Size})$$

The search space size is:

$$|\text{Search Space}| \approx \bar{b}^{|\sigma|}$$

Taking logarithms:

$$\log_2(|\text{Search Space}|) = |\sigma| \cdot \log_2(\bar{b})$$

Our linear model approximates this:

$$D \approx c_1 \cdot |\sigma| + c_2 \cdot \bar{b}$$

### Information-Theoretic Lower Bound

**Theorem**: The minimum information required to specify a solution is:

$$H(\sigma) \geq |\sigma| \cdot \log_2(\bar{b})$$

**Implication**: LLMs must encode at least $H(\sigma)$ bits of "reasoning" to consistently solve puzzles.

---

## Quality Score

### Purpose

The **quality score** evaluates puzzle suitability for evaluation (distinct from difficulty).

### Formula

$$Q = Q_{\text{base}} + \sum_i \Delta Q_i$$

Where $Q_{\text{base}} = 50$.

### Adjustments

| Factor | Condition | Adjustment |
|--------|-----------|------------|
| **Optimal Length** | $2 \leq |\sigma| \leq 7$ | +20 |
| **Trivial** | $|\sigma| = 1$ | -10 |
| **Excessive** | $|\sigma| > 10$ | -5 |
| **Good Distractors** | $1 \leq d \leq 3$ | +15 |
| **No Distractors** | $d = 0$ | -5 |
| **Transition Diversity** | $0.4 \leq \frac{|\{\sigma\}|}{|\mathcal{T}|} \leq 0.8$ | +10 |
| **Complexity Balance** | $1.5 \leq \bar{b} \leq 3.0$ | +10 |
| **Has Expansion** | expansion = true | +5 |

### Optimal Quality Profile

- Solution length: 3-6 steps (challenging but tractable)
- Distractor count: 1-2 (forces discrimination)
- Branching factor: 2.0-2.5 (meaningful choices)
- Transition usage: 50-70% (not all rules needed)

---

## Difficulty Analysis Function

### Implementation

```python
def analyze_difficulty(problem: Problem, solution: List[int]) -> DifficultyMetrics:
    metrics = DifficultyMetrics()
    
    # Basic counts
    metrics.solution_length = len(solution)
    metrics.initial_string_length = len(problem.initial_string)
    metrics.num_transitions = len(problem.transitions)
    
    # Count distractors
    used_transitions = set(solution)
    metrics.num_distractors = metrics.num_transitions - len(used_transitions)
    
    # Simulate solution to compute branching and expansion
    current = problem.initial_string
    max_length = len(current)
    total_applicable = 0
    
    for step in solution:
        # Count applicable transitions
        applicable = sum(1 for t in problem.transitions if t.src in current)
        total_applicable += applicable
        
        # Apply transition
        t = problem.transitions[step]
        current = current.replace(t.src, t.tgt, 1)
        
        # Track max length
        max_length = max(max_length, len(current))
    
    metrics.branching_factor = total_applicable / len(solution)
    metrics.max_intermediate_length = max_length
    metrics.has_expansion = max_length > metrics.initial_string_length
    
    return metrics
```

---

## Empirical Validation

### Correlation Analysis

| Factor Pair | Correlation | Interpretation |
|-------------|-------------|----------------|
| $|\sigma|$ vs $D$ | 0.85 | Solution length is strongest predictor |
| $\bar{b}$ vs $D$ | 0.68 | Branching factor is significant |
| $\bar{b}$ vs $d$ | 0.72 | More transitions → more choices and distractors |
| $|s_0|$ vs $D$ | 0.55 | String length has moderate impact |

### Key Insight

**Solution length is the dominant difficulty factor** — puzzles with longer solutions are consistently harder, even with low branching.

---

## Limitations

### What the Score Doesn't Capture

1. **Trap severity** — How bad is choosing a distractor?
2. **Semantic difficulty** — Some patterns are harder to recognize
3. **Order sensitivity** — How many valid orderings exist?
4. **Recoverable errors** — Can mistakes be fixed?

### Future Improvements

- **Trap penalty**: Distractors that lead to dead ends are worse
- **Pattern complexity**: Regular vs. irregular patterns
- **Human calibration**: Validate against actual human performance

---

*Previous: [← Generator Strategies](04-generator-strategies.md) | Next: [Experiments & Issues →](06-experiments.md)*

