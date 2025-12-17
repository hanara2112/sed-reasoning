# SED Reasoning

Evaluating LLM reasoning on String Edit Distance puzzles.

---

## Problem

An SED puzzle consists of:

- An **initial string** (e.g., `"ABCDEF"`)
- **Transformation rules** (e.g., `"ABC" → ""`, `"DEF" → ""`)
- **Goal**: Apply rules to reach empty string `""`

```
Initial: "ABCDEF"
Rules:   0: "ABC" → ""   1: "DEF" → ""
Solution: [0, 1]
Trace:   "ABCDEF" → "DEF" → ""
```

---

## Structure

```
sed-reasoning/
├── data/                    # 100 puzzles + solutions + metadata
├── dataset_generation/      # Puzzle generators, BFS solver
├── llm_evaluation/          # Evaluation pipeline, prompts
├── results/                 # CSVs, figures, model outputs
├── notebooks/               # Analysis notebooks
└── report/                  # Technical reports (markdown)
```

---

## Tasks

### Task 1: Dataset Generation

- 100 puzzles across 8 generator types
- 3 difficulty levels (easy, medium, hard)
- BFS-verified solutions

### Task 2: LLM Evaluation

- 3 models: LLaMA 3.3 70B, LLaMA 4 Scout 17B, LLaMA 3.1 8B
- 5 prompting strategies: Zero-Shot, Few-Shot, CoT, Self-Verify, Role-Classify
- 480 total evaluations

### Task 3: Metrics Analysis

- Binary accuracy, progress score, valid steps ratio, composite score
- Correlation analysis, identifiability theory

### Task 4: Human vs Machine

- Cognitive asymmetry analysis
- Generator-stratified performance comparison

---

## Key Results

| Model             | Best Accuracy | Best Prompt   |
| ----------------- | ------------- | ------------- |
| LLaMA 4 Scout 17B | 43.8%         | Few-Shot      |
| LLaMA 3.3 70B     | 34.4%         | Few-Shot      |
| LLaMA 3.1 8B      | 18.8%         | Role-Classify |

**Overall accuracy: 26%** — the benchmark poses genuine difficulty.

---

## Key Findings

1. **Difficulty dominates** — Easy: 52%, Medium: 20%, Hard: 6%
2. **Validity ≠ correctness** — r = 0.111 (near-zero correlation)
3. **Sorting puzzles expose LLM weakness** — 84% human-LLM gap
4. **Prompt engineering has diminishing returns**

---

## Usage

```bash
# Install
pip install -r requirements.txt

# Generate dataset
python -m dataset_generation.main

# Run evaluation
python -m llm_evaluation.run_evaluation --models llama-4-scout --prompt-types few_shot

# Analysis
jupyter notebook notebooks/
```

---

## Reports

* **SED Puzzle Dataset** : Describes how the string-edit puzzles are generated, structured, and verified.
* **LLM Evaluation** : Summarizes the evaluation setup, models, prompting strategies, and overall performance results.
* **Evaluation Metrics** : Defines the metrics used to assess reasoning quality, including correctness, progress, and validity.
* **Human vs Machine** : Analyzes differences between human and LLM performance, highlighting cognitive asymmetries across puzzle types.

## References

1. Trinh, T.H., Wu, Y., Le, Q.V., He, H., & Luong, T. (2024). **Solving olympiad geometry without human demonstrations**. *Nature*, 625, 476–482. https://doi.org/10.1038/s41586-023-06747-5
2. Wei, J., Wang, X., Schuurmans, D., et al. (2022). **Chain-of-Thought Prompting Elicits Reasoning in Large Language Models**. *NeurIPS 2022*. https://arxiv.org/abs/2201.11903
3. Brown, T.B., Mann, B., Ryder, N., et al. (2020). **Language Models are Few-Shot Learners**. *NeurIPS 2020*. https://arxiv.org/abs/2005.14165
4. Xia, W., Qin, L., & Radev, D. (2024). **Evaluating Mathematical Reasoning Beyond Accuracy: Validity and Redundancy in Step-by-Step Traces**. *arXiv preprint*. https://arxiv.org/html/2404.05692v1
