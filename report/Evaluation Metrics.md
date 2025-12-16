# Evaluation Metrics: A Mathematical Framework

## Abstract

We formalize four evaluation metrics for assessing LLM performance on sequential reasoning tasks. Through correlation analysis and edge-case decomposition, we demonstrate that syntactic validity is non-predictive of task success, motivating composite metrics that jointly capture semantic progress and rule compliance.

---

## 1. Metric Definitions

Let $s_0$ denote the initial string, $s_f$ the final string after applying the model's solution, and $\varepsilon$ the goal state (empty string).

### 1.1 Binary Accuracy

$$A_{\text{bin}} = \mathbb{1}[s_f = \varepsilon]$$

Binary accuracy is an indicator function returning 1 if the task is solved exactly, 0 otherwise. It provides an unambiguous correctness signal but discards all information about partial progress.

**Properties:**
- Range: $\{0, 1\}$
- Discontinuous at $s_f = \varepsilon$
- Information loss: treats 99% progress identically to 0%

### 1.2 Progress Score

$$P = \frac{|s_0| - |s_f|}{|s_0|}$$

The progress score measures fractional string reduction, capturing how close the model comes to the goal.

**Properties:**
- Range: $[0, 1]$ (assuming $|s_f| \leq |s_0|$)
- $P = 1 \iff s_f = \varepsilon$ (solved)
- $P = 0 \iff |s_f| = |s_0|$ (no progress)
- Continuous in $|s_f|$

**Limitation:** Does not distinguish valid from invalid intermediate steps.

### 1.3 Valid Steps Ratio

Let $n_{\text{valid}}$ denote the number of syntactically valid rule applications and $n_{\text{total}}$ the total attempted steps.

$$V = \frac{n_{\text{valid}}}{n_{\text{total}}}$$

**Properties:**
- Range: $[0, 1]$
- $V = 1 \iff$ all attempted steps are valid
- Undefined if $n_{\text{total}} = 0$ (convention: $V = 0$)

**Limitation:** High validity does not imply semantic progress.

### 1.4 Composite Score

$$C = w_1 \cdot A_{\text{bin}} + w_2 \cdot P + w_3 \cdot V$$

where $w_1 + w_2 + w_3 = 1$ and $w_i \geq 0$.

**Default weights:** $w_1 = 0.5$, $w_2 = 0.3$, $w_3 = 0.2$

**Properties:**
- Range: $[0, 1]$
- Convex combination of component metrics
- Balances correctness, progress, and validity

---

## 2. Correlation Analysis

### 2.1 Empirical Correlation Matrix

Let $\rho(X, Y)$ denote Pearson correlation between metrics $X$ and $Y$.

$$
\begin{array}{c|cccc}
 & A_{\text{bin}} & P & V & C \\
\hline
A_{\text{bin}} & 1.000 & 0.753 & 0.111 & 0.963 \\
P & 0.753 & 1.000 & 0.286 & 0.861 \\
V & 0.111 & 0.286 & 1.000 & 0.330 \\
C & 0.963 & 0.861 & 0.330 & 1.000 \\
\end{array}
$$

### 2.2 Key Observations

**Observation 1:** $\rho(V, A_{\text{bin}}) = 0.111 \approx 0$

> Syntactic validity is effectively uncorrelated with task success.

This implies that a model can achieve high validity ($V \to 1$) while maintaining low accuracy ($A_{\text{bin}} \to 0$). Formally:

$$\text{Var}(A_{\text{bin}} | V) \approx \text{Var}(A_{\text{bin}})$$

Validity provides negligible information about correctness.

**Observation 2:** $\rho(P, A_{\text{bin}}) = 0.753$

Progress is moderately predictive of success, but substantial variance remains unexplained ($R^2 = 0.57$).

**Observation 3:** $\rho(C, A_{\text{bin}}) = 0.963$

The composite score is highly correlated with binary accuracy by construction (due to $w_1 = 0.5$), but provides continuous gradation for incorrect solutions.

---

## 3. Identifiability Analysis

### 3.1 Definition

A metric $M$ is **identifying** with respect to latent competence $\theta$ if:

$$M(Y_1) = M(Y_2) \implies \theta(Y_1) = \theta(Y_2)$$

Equal metric values imply equal underlying competence.

### 3.2 Validity as Non-Identifying

Consider two model outputs:
- $Y_1$: All steps valid, reaches goal ($A = 1$, $V = 1$)
- $Y_2$: All steps valid, does not reach goal ($A = 0$, $V = 1$)

Both achieve $V = 1$, but represent fundamentally different reasoning states. Thus:

$$V(Y_1) = V(Y_2) = 1 \quad \text{but} \quad \theta(Y_1) \neq \theta(Y_2)$$

**Conclusion:** Validity is non-identifying for reasoning competence.

### 3.3 Disagreement Mass

Define the **disagreement mass** between correct and incorrect solution distributions:

$$D_M = \int \min\left(p_M(x | A = 1), p_M(x | A = 0)\right) dx$$

where $p_M(x | A)$ is the metric distribution conditioned on correctness.

| Metric | Disagreement Mass | Interpretation |
|--------|-------------------|----------------|
| $A_{\text{bin}}$ | 0.00 | Perfectly identifying (by definition) |
| $P$ | 0.24 | Moderate overlap |
| $V$ | 0.71 | High overlap (poor identifiability) |
| $C$ | 0.18 | Low overlap (good identifiability) |

---

## 4. Edge Case Taxonomy

### 4.1 Formal Categories

Define outcome categories based on metric values:

| Category | $A_{\text{bin}}$ | $P$ | $V$ | Interpretation |
|----------|------------------|-----|-----|----------------|
| Correct Optimal | 1 | 1 | 1 | Ideal |
| Correct Suboptimal | 1 | 1 | $<1$ | Redundant steps |
| Near Miss | 0 | $>0.9$ | $<1$ | Almost solved |
| Valid Failure | 0 | $<0.5$ | 1 | Rule compliance without progress |
| Invalid Failure | 0 | $<0.5$ | $<0.5$ | Complete failure |

### 4.2 Distribution (n = 480)

| Category | Count | Percentage |
|----------|-------|------------|
| Correct | 244 | 50.8% |
| Near Miss ($P > 0.9$) | 47 | 9.8% |
| Valid Failure ($V = 1, P < 0.5$) | 31 | 6.5% |
| Other Incorrect | 158 | 32.9% |

**Observation:** 6.5% of outputs achieve perfect validity while making less than 50% progress—clear evidence of non-identifying behavior.

---

## 5. Metric Selection Theory

### 5.1 Discrimination Power

Define discrimination power as the variance of metric means across models:

$$\sigma^2_M = \text{Var}(\mathbb{E}[M | \text{model}])$$

| Metric | $\sigma^2_M$ | Range |
|--------|--------------|-------|
| $V$ | 0.0158 | 0.251 |
| $C$ | 0.0068 | 0.151 |
| $A_{\text{bin}}$ | 0.0062 | 0.156 |
| $P$ | 0.0062 | 0.149 |

**Observation:** Validity has highest discrimination ($\sigma^2 = 0.016$) but is non-identifying. This is a Goodhart effect: optimizing validity does not improve reasoning.

### 5.2 Recommendation

For evaluation use cases:

| Purpose | Metric | Rationale |
|---------|--------|-----------|
| Task completion | $A_{\text{bin}}$ | Unambiguous correctness |
| Model ranking | $C$ | Balances correctness and gradation |
| Failure diagnosis | $(P, V)$ jointly | Separates semantic from syntactic failure |
| Optimization target | $C$ | Smooth, differentiable signal |

---

## 6. Theoretical Implications

### 6.1 Goodhart's Law

> "When a measure becomes a target, it ceases to be a good measure."

If models optimize for $V$ (validity), they may achieve high scores without improving reasoning:

$$\max_\theta V(\theta) \not\Rightarrow \max_\theta A_{\text{bin}}(\theta)$$

### 6.2 Metric Misalignment

A metric $M$ is **misaligned** if:

$$\arg\max_Y M(Y) \neq \arg\max_Y A_{\text{bin}}(Y)$$

Validity is misaligned: a model can maximize $V$ by producing long sequences of valid but unproductive steps.

### 6.3 Composite Metrics as Regularization

The composite score $C$ mitigates misalignment by incorporating $A_{\text{bin}}$ directly:

$$C = w_1 A_{\text{bin}} + (1 - w_1)(w_2' P + w_3' V)$$

With $w_1 > 0$, optimizing $C$ necessarily considers correctness, reducing Goodhart risk.

---

## 7. Conclusion

1. **Validity is non-identifying** — $\rho(V, A) = 0.111$
2. **Progress is partially identifying** — $\rho(P, A) = 0.753$
3. **Composite scores balance identifiability and gradation**
4. **Binary accuracy remains the ground truth** for task completion

Evaluation should use **multiple metrics jointly**, with binary accuracy as the primary signal and composite/progress scores for diagnosing failure modes.

---

## References

- Analysis: `notebooks/metrics_analysis.ipynb`
- Data: `results/metrics_full_analysis.csv`

