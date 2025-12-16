# Discussion

## Reframing "LLM Failures"

### What We Usually Hear

> "The model hallucinated."
> "The model was lazy."
> "The model doesn't understand."

These framings are:
- **Anthropomorphic** — Attributing human traits to statistical processes
- **Moralizing** — Treating failures as character flaws
- **Unproductive** — Offering no path to improvement

### What We Should Say

> "The metric failed to identify competence."
> "The evaluation rewarded surface compliance."
> "The benchmark has low identifiability."

These framings are:
- **Mechanistic** — Point to specific design failures
- **Diagnostic** — Suggest concrete improvements
- **Actionable** — Enable better evaluation

---

## Why LLMs "Fail" on Structured Tasks

### The Actual Mechanism

1. Models are trained to **maximize likelihood** of human-like text
2. Human-like text is often **verbose, confident, and locally coherent**
3. Evaluation metrics reward **verbosity, validity, and progress**
4. These proxy objectives **diverge** from semantic correctness
5. Models optimize proxies → high scores, low correctness

### Not Laziness, But Optimization

The model is doing exactly what it was trained to do:
- Generate plausible continuations
- Maintain local coherence
- Produce confident, fluent output

If this doesn't correlate with task success, that's a **training objective problem**, not a model defect.

---

## Why Moralizing Failure Is Wrong

### The Stoic Perspective Revisited

Marcus Aurelius would not say:
> "This person is bad for behaving predictably."

He would say:
> "I should have expected this behavior. How do I design around it?"

Similarly:
> "The model is not bad for optimizing its objective. How do we align evaluation with true goals?"

### The Engineering Perspective

Blaming models for metric gaming is like blaming water for flowing downhill.

If your metric rewards X and the model produces X, the metric is working. The question is whether X is what you actually wanted.

---

## Implications for Benchmark Design

### Principle 1: Semantic Verification Is Non-Negotiable

Every benchmark should include:

```
Correctness = Execute(Y, s_0) ∈ G
```

No proxy. No approximation. Execute and check.

### Principle 2: Auxiliary Metrics Must Be Validated

Before using validity, progress, or length as metrics:

1. Compute correlation with correctness
2. Report disagreement mass
3. Show that the metric adds information beyond random

If a metric doesn't survive this test, **don't use it**.

### Principle 3: Adversarial Stress Testing

For every metric, ask:

> "Can a model maximize this metric without solving the task?"

If yes, the metric is vulnerable. Report this vulnerability.

### Principle 4: Report Identifiability

Every evaluation should state:

- What latent competence is being measured
- How identifiable it is from the metric
- What the known failure modes are

---

## Future Directions

### Better Metrics

- **Compositional correctness** — Check that partial solutions extend to full solutions
- **Counterfactual testing** — Would the model succeed with slightly different inputs?
- **Trajectory analysis** — Did the model ever pass through a solvable state?

### Better Benchmarks

- **Controlled difficulty** — Systematically vary complexity factors
- **Trap detection** — Include problems where greedy strategies fail
- **Distribution coverage** — Test across reasoning types, not just accuracy on one type

### Better Understanding

- **When do proxy metrics work?** — Under what conditions does validity correlate with correctness?
- **What makes tasks hard for LLMs?** — Is it search depth? Constraint satisfaction? Non-monotonicity?
- **Can we predict identifiability?** — Given a metric and task, can we estimate disagreement mass a priori?

---

## The Central Takeaway

> **LLMs are not failing the benchmark; the benchmark is revealing where reasoning is not identifiable from surface behavior.**

This is not a pessimistic conclusion. It's a **diagnostic** one.

Once we understand that:
- Metrics can fail to identify competence
- Surface compliance can diverge from semantic success
- Evaluation design determines what we learn

...we can build better evaluations, better benchmarks, and ultimately better models.

---

## Summary of Key Points

| Concept | Implication |
|---------|-------------|
| Syntax ≠ Semantics | Valid steps don't guarantee correct outcomes |
| Local ≠ Global | Progress doesn't guarantee success |
| Observable ≠ Latent | Metrics don't guarantee competence identification |
| Goodhart's Law | Optimized metrics lose their meaning |

---

## Conclusion

This document formalizes a key failure mode in modern LLM evaluation: **the inability of common metrics to identify semantic reasoning competence**.

By separating:
- Syntax from semantics
- Local from global correctness
- Observables from latent computation

...we show that many alarming LLM behaviors are **predictable consequences of metric design**, not fundamental model limitations.

Future evaluation must shift from **rewarding plausibility** to **enforcing semantic soundness** under true task dynamics.

---

## References

- Goodhart, C. (1975). *Problems of Monetary Management: The U.K. Experience*
- Russell, S., & Norvig, P. *Artificial Intelligence: A Modern Approach*
- Marcus Aurelius. *Meditations*
- Strathern, M. (1997). "Improving ratings": audit in the British University system
- Contemporary work on reasoning benchmarks and proxy objectives in LLMs

---

*Previous: [← Identifiability](05-identifiability.md) | [Back to Overview](../README.md)*

