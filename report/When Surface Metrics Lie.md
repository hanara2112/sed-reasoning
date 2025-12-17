# Identifiability Failures in LLM Reasoning Evaluation

> *"When a measure becomes a target, it ceases to be a good measure."*
> — **Charles Goodhart (1975)**

## Abstract

Large Language Models are increasingly evaluated on multi-step reasoning tasks using surface-level metrics—step validity, progress, and length—treated as proxies for semantic correctness. We demonstrate that even in highly controlled symbolic reasoning domains, these metrics fail to identify true problem-solving competence. Using String Edit Distance (SED) puzzles as a minimal testbed, we formalize reasoning evaluation as a statistical identifiability problem and quantify  *disagreement mass* : the probability that observable metrics indicate success while the solution remains semantically incorrect. Our empirical analysis reveals substantial disagreement mass across difficulty levels, monotonically increasing with task complexity. These findings challenge the validity of metric-based reasoning benchmarks and motivate a principled rethinking of evaluation methodology.

**Contributions (summary).**

1. Formalize reasoning evaluation as an *identifiability* problem: can latent competence be inferred from observed surface metrics?
2. Introduce and operationalize **disagreement mass** as a diagnostic for non-identifiability.
3. Empirically show disagreement increases sharply with difficulty on SED puzzles, even when step-level validity is high.

---

## 1. Introduction

The evaluation of reasoning in Large Language Models relies heavily on surface-level metrics. Practitioners commonly measure:

* **Validity** : the fraction of syntactically correct steps
* **Progress** : reduction in problem state (e.g., string length)
* **Efficiency** : solution length relative to an optimal baseline

These metrics are intuitive, computable, and amenable to automated scoring. However, they are rarely validated against the ground truth they purport to measure: whether the LLM has genuinely solved the problem.

### 1.1 The Core Problem

A fundamental assumption underlies current practice:

> **High metric values ⟹ Semantic correctness**

This assumption is rarely formalized or tested. We ask:

> **Central Question:** Can semantic correctness be reliably **identified** from standard evaluation metrics, even in maximally controlled reasoning settings?

### 1.2 Why This Matters

If metrics fail to identify reasoning ability in controlled domains, they likely fail in open-ended benchmarks as well. This has immediate practical consequences:

1. **False positives** : Models appear capable when they are not.
2. **Misaligned optimization** : Metric maximization diverges from problem-solving.
3. **Benchmark validity** : Leaderboards may not measure what they claim.

---

## 2. Problem Setting: String Edit Distance Puzzles

### 2.1 Formal Definition

We study **String Edit Distance (SED)** puzzles—a well-defined class of symbolic reasoning tasks:

**Definition (SED Puzzle).** An SED puzzle is a tuple $(\Sigma, s_0, T, \varepsilon)$ where:

* $\Sigma$ is a finite alphabet
* $s_0 \in \Sigma^*$ is the initial string
* $T = {u_i \to v_i}_{i=1}^{|T|}$ is a finite set of rewrite rules (substitutions)
* $\varepsilon$ is the goal (the empty string)

A **solution** is a sequence of rule applications:

$$
s_0 \to s_1 \to \cdots \to s_k = \varepsilon
$$

### 2.2 Why SED as a Testbed?

SED puzzles provide maximal structural control while remaining cognitively challenging:

1. **Local checkability** : Each step is syntactically verifiable.
2. **Global optimality** : A shortest solution exists and is computable.
3. **Semantic unambiguity** : Success/failure is objectively defined.
4. **Controlled complexity** : Difficulty varies systematically with problem size.
5. **Fundamental non-implication** :

$$
(\forall i,\ a_i \in \mathcal{A}(s_{i-1})) \;\not\Rightarrow\; (s_k = \varepsilon)
$$

   This is the key property isolating local from global correctness.

---

## 3. Standard Metrics and Their Failure Modes

### 3.1 Three Widely Used Proxies

We analyze the most common reasoning metrics:

1. **Validity ($V$)** : Fraction of steps that apply a rule from $T$ to a valid substring.

$$
V = \frac{\#\text{ valid steps}}{\#\text{ total steps}}
$$

2. **Progress ($P$)** : Reduction in string length between the initial and final state.

$$
P = 1 - \frac{|s_{\text{final}}|}{|s_0|}
$$

3. **Efficiency ($E$)** : Normalized ratio of optimal length to produced length (for correct solutions).

$$
E = \min\left(1, \frac{L^*}{L}\right)\ \text{if } s_{\text{final}}=\varepsilon,\ \text{else } 0
$$

where $L^*$ is the optimal (shortest) solution length and $L$ is the model’s solution length.

### 3.2 Failure Modes

Each metric can be systematically optimized without reaching the goal:

**Validity Bias:** A trajectory applies only valid rules yet terminates in a dead state (no further rules apply), failing to reach $\varepsilon$.

**Progress Bias:** Rules are applied to maximize $|s_0| - |s_{\text{final}}|$, but the trace enters a local minimum and cannot reach $\varepsilon$.

**Length Bias:** A short, confident-looking trace halts prematurely without achieving the goal.

These pathologies reveal that metrics measure **symptoms** of competence, not competence itself.

---

## 4. Identifiability Formalization

### 4.1 The Identifiability Framework

We frame reasoning evaluation as a statistical identifiability problem:

**Definition (Identifiability).** Let $\theta$ denote latent reasoning competence (semantic correctness) and $M$ denote observable metrics (validity, progress, length). $\theta$ is **identifiable** from $M$ if the posterior $p(\theta \mid M)$ concentrates near the true value under suitable conditions.

**Main Claim:** Semantic reasoning competence is **not identifiable** from standard metrics, even in maximally controlled domains.

### 4.2 Quantifying Disagreement

To operationalize non-identifiability, we introduce **disagreement mass**.

**Definition (Disagreement Mass).** Let $S_{\text{fail}}$ denote semantic failure and let “high proxy” mean high surface scores on at least one proxy. In our experiments we instantiate:

$$
S_{\text{fail}} := (s_{\text{final}} \neq \varepsilon)
$$

$$
M_{\text{high}} := (P > \tau_P)\ \lor\ (V > \tau_V)
$$

with thresholds $\tau_P = 0.5$ and $\tau_V = 0.8$. Disagreement mass is:

$$
D = \mathbb{P}(M_{\text{high}} \wedge S_{\text{fail}})
$$

where the probability is estimated over the distribution of LLM-generated traces.

Intuitively, disagreement mass is the frequency with which the metrics would declare success while the solution is incorrect. High disagreement mass indicates weak identifiability.

---

## 5. Empirical Analysis

### 5.1 Experimental Setup

We generate SED puzzles across multiple difficulty levels and collect LLM-generated reasoning traces. For each trace, we compute:

* Validity, progress, and efficiency metrics
* Ground-truth semantic correctness (whether $s_{\text{final}} = \varepsilon$)

### 5.2 Key Findings

**Headline results (this dataset).**

- **High validity does not imply correctness**: among traces with \(V\\ge 0.8\), **41.9%** are still incorrect.
- **Union-based disagreement is substantial**: $D \approx 0.277$ (**133/480**) for $M_{\text{high}}=(P>0.5)\lor(V>0.8)$.
- **Identifiability degrades with difficulty** (same definition of \(D\)):
  - easy: **0.025**
  - medium: **0.167**
  - hard: **0.556**
- **Near-perfect validity still fails**: among traces with \(V\\ge 0.99\), **36.5%** are incorrect.

These findings show that even in a controlled symbolic domain, surface proxies can strongly mislead evaluation—especially on hard instances.

---

## 6. Implications and Research Directions

### 6.1 What This Means

If surface metrics fail to identify reasoning in controlled, symbolic domains:

* They cannot be trusted as reliable proxies in open-ended benchmarks.
* Metric-based leaderboards may misrank models.
* Model selection and fine-tuning decisions may be misaligned with true capability.

### 6.2 Toward Better Evaluation

We propose several research directions:

1. **Semantics-aware metrics** : Develop proxies with formal identifiability guarantees.
2. **Learned evaluators** : Train neural evaluators with explicit non-identifiability constraints.
3. **Adversarial task design** : Construct reasoning benchmarks where proxy optimization is provably impossible.
4. **Ensemble validation** : Cross-validate metrics against multiple independent ground-truth measures.

---

## 7. Discussion

SED puzzles serve as a  **minimal counterexample** : if reasoning metrics fail here, they cannot be assumed to work in less structured domains. This work reframes evaluation as a statistical problem requiring rigorous validation, rather than a leaderboard optimization exercise.

The stakes are high: if we cannot reliably measure reasoning in controlled settings, our confidence in LLM capabilities rests on an uncertain foundation.

---

## Acknowledgments

We acknowledge the importance of rigorous evaluation methodology in advancing our understanding of LLM reasoning.

---

## References

- Goodhart, C. A. E. (1975). *Problems of Monetary Management: The U.K. Experience*.
- Korzybski, A. (1933). *Science and Sanity* (“the map is not the territory”).
- Standard statistical inference / identifiability references (e.g., econometrics texts) for identifiability definitions.
