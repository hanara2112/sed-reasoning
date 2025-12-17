# Connecting SED-Puzzle Reasoning to Preference Circuits Research

## Research Question
**"Manifold manipulation of preference circuits in SLMs under distribution shift"**

## How SED-Puzzles Relate to Your Research

### 1. **Distribution Shift as Core Challenge**

**Connection:**
- SED-puzzles are **out-of-distribution** for most LLMs
- Models haven't seen these specific puzzle patterns in training
- Tests how models generalize to novel reasoning tasks

**Research Value:**
- Evaluates robustness of preference circuits when encountering unfamiliar problem structures
- Measures how well circuits adapt vs. fail catastrophically
- Provides controlled testbed for distribution shift scenarios

---

### 2. **Preference Circuits as Decision-Making Mechanisms**

**Connection:**
- Each puzzle requires LLM to make **sequential decisions** (which transition to apply)
- These decisions reveal the model's internal "preferences" or heuristics
- Different prompting strategies activate different reasoning pathways

**Research Value:**
- **Zero-shot**: Reveals default preference circuits (greedy, pattern-matching)
- **Few-shot**: Shows how examples modify preference circuits (inductive bias)
- **Chain-of-Thought**: Exposes step-by-step decision-making process

**What We Can Measure:**
- Which transitions models prefer (even when wrong)
- How preferences change with different prompts
- Whether preferences align with optimal solutions

---

### 3. **Manifold Structure of Solution Space**

**Connection:**
- Each puzzle defines a **solution manifold** (all possible paths from initial → empty)
- Different prompts navigate this manifold differently
- Some paths are "preferred" by the model's circuits

**Research Value:**
- **Manifold geometry**: Solution space has structure (easy paths, hard paths, dead ends)
- **Manifold manipulation**: Prompting strategies change how model explores this space
- **Circuit activation**: Different parts of the model activate for different path types

**Visualization:**
```
Solution Manifold:
  Initial String
    ├─ Path A (preferred by default circuits) → Dead end
    ├─ Path B (requires manipulation) → Solution
    └─ Path C (distractor) → Wrong answer
```

---

### 4. **Preference Circuit Analysis Through Metrics**

**Connection:**
- Our metrics reveal **what the model prefers**:
  - **Path Similarity**: Which transitions does model prefer?
  - **Sequence Similarity**: What order does model prefer?
  - **Progress Score**: Does model prefer safe vs. risky moves?

**Research Value:**
- Quantifies preference circuit behavior
- Shows how preferences change under distribution shift
- Identifies when circuits fail (wrong preferences)

---

### 5. **Human vs. Machine: Preference Circuit Differences**

**Connection:**
- Humans and LLMs have **different preference circuits**
- Humans prefer: semantic patterns, visual intuition
- LLMs prefer: systematic search, pattern matching

**Research Value:**
- Reveals **what preference circuits encode**
- Shows **distribution shift effects** (what works in training vs. what's needed)
- Identifies **circuit limitations** (what preferences are missing)

---

## Research Framework

### Phase 1: Baseline (Current Work)
- ✅ Generate diverse puzzle dataset (distribution shift testbed)
- ✅ Evaluate LLM performance (preference circuit behavior)
- ✅ Develop metrics (preference circuit analysis)

### Phase 2: Preference Circuit Analysis
- **Identify circuits**: Which model components handle puzzle reasoning?
- **Circuit preferences**: What heuristics do circuits encode?
- **Distribution shift effects**: How do circuits fail on OOD puzzles?

### Phase 3: Manifold Manipulation
- **Prompt engineering**: How to manipulate circuits to prefer better paths?
- **Fine-tuning**: Can we modify preference circuits for better OOD performance?
- **Circuit intervention**: Direct manipulation of circuit activations

### Phase 4: Generalization
- **Transfer learning**: Do manipulated circuits generalize?
- **Robustness**: Performance across different puzzle types
- **Theoretical insights**: Understanding preference circuit structure

---

## Key Research Questions This Enables

1. **How do preference circuits handle distribution shift?**
   - Measure performance drop on OOD puzzles
   - Identify which circuits fail first

2. **Can we manipulate preference circuits via prompting?**
   - Compare zero-shot vs. few-shot vs. CoT
   - Measure circuit activation changes

3. **What preferences do circuits encode?**
   - Analyze which transitions/models are preferred
   - Compare to optimal preferences

4. **How do preferences differ across models?**
   - Compare different LLMs on same puzzles
   - Identify model-specific preference patterns

5. **Can we improve OOD performance by manipulating preferences?**
   - Test intervention strategies
   - Measure generalization

---

## Experimental Design

### Dataset as Distribution Shift Testbed
- **In-distribution**: Simple concatenation puzzles (similar to training)
- **Out-of-distribution**: Complex multi-phase puzzles (novel structure)
- **Controlled difficulty**: Measure gradual performance degradation

### Metrics as Preference Circuit Proxies
- **Binary accuracy**: Overall circuit success
- **Path similarity**: Preference for specific transitions
- **Progress score**: Preference for safe vs. optimal moves
- **Efficiency**: Preference for short vs. long solutions

### Prompting as Circuit Manipulation
- **Zero-shot**: Baseline circuit behavior
- **Few-shot**: Circuit adaptation via examples
- **CoT**: Circuit activation via explicit reasoning

---

## Expected Contributions

1. **Novel evaluation framework** for preference circuits under distribution shift
2. **Quantitative metrics** for measuring circuit preferences
3. **Empirical findings** on how circuits handle OOD reasoning
4. **Intervention strategies** for improving OOD performance
5. **Theoretical insights** into preference circuit structure

---

## Next Steps for Your Research

1. **Circuit Analysis**:
   - Use activation patching to identify relevant circuits
   - Measure circuit activations for different puzzle types
   - Compare activations for correct vs. incorrect solutions

2. **Preference Mapping**:
   - Analyze which transitions/models circuits prefer
   - Map preferences to circuit locations
   - Identify preference biases

3. **Manifold Exploration**:
   - Visualize solution space structure
   - Track how circuits navigate this space
   - Identify "preferred paths" vs. "optimal paths"

4. **Intervention Experiments**:
   - Test direct circuit manipulation
   - Measure preference changes
   - Evaluate generalization

5. **Theoretical Development**:
   - Model preference circuits mathematically
   - Understand manifold structure
   - Predict distribution shift effects

---

## Connection Summary

| Research Component | SED-Puzzle Connection |
|-------------------|----------------------|
| **Distribution Shift** | Puzzles are OOD for LLMs |
| **Preference Circuits** | Decision-making in puzzle solving |
| **Manifold Structure** | Solution space geometry |
| **Manipulation** | Prompting strategies |
| **Evaluation** | Metrics reveal preferences |
| **Generalization** | Performance across puzzle types |

This project provides a **controlled, interpretable testbed** for studying preference circuits under distribution shift, with clear metrics and diverse scenarios.

