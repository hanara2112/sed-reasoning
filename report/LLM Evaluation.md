# LLM Evaluation on SED Puzzles

## Abstract

We evaluate three LLaMA-family models across five prompting strategies on 32 SED reasoning puzzles. Overall accuracy is 26%, with performance degrading sharply on harder instances. Results indicate that prompt engineering provides limited gains and that failures are driven by multi-step reasoning bottlenecks rather than surface understanding.

For detailed results and visualizations, see `notebooks/llm_evaluation.ipynb`.

---

## 1. Experimental Setup

### 1.1 Models

| Model | Parameters | Notes |
|-------|------------|-------|
| LLaMA 3.3 70B | 70B | Largest model |
| LLaMA 4 Scout | 17B | Instruction-tuned |
| LLaMA 3.1 8B | 8B | Smallest model |

### 1.2 Prompting Strategies

| Strategy | Description |
|----------|-------------|
| **Zero-Shot** | Direct instruction without examples |
| **Few-Shot** | 5 solved examples provided |
| **Chain-of-Thought** | Explicit step-by-step reasoning |
| **Self-Verify** | Propose → Simulate → Verify → Revise |
| **Role-Classify** | Classify rule roles before solving |

### 1.3 Evaluation Protocol

- **Test set**: 32 puzzles (balanced by difficulty)
- **Total evaluations**: 480 (3 models × 5 prompts × 32 puzzles)
- **Metrics**: Binary accuracy (task completion)

---

## 2. Key Findings

### 2.1 Overall Performance

**Aggregate accuracy: 26%** (125/480 correct)

Best configuration: **LLaMA 4 Scout + Few-Shot** (43.8%)

> Model scale does not monotonically predict performance. The 17B Scout model outperforms the 70B model in several configurations, suggesting architectural and training differences matter.

### 2.2 Difficulty Dominates

| Difficulty | Accuracy |
|------------|----------|
| Easy | 51.7% |
| Medium | 20.0% |
| Hard | 6.1% |

Performance degrades sharply with difficulty. Hard puzzles (7+ steps, distractors) are effectively unsolved—only 6.1% accuracy across all model-prompt combinations.

### 2.3 Prompting Provides Limited Gains

| Strategy | Mean Accuracy | Latency |
|----------|---------------|---------|
| Few-Shot | 29.2% | Medium |
| Role-Classify | 27.1% | Medium |
| Zero-Shot | 25.0% | Low |
| CoT | 28.1% | High |
| Self-Verify | 20.8% | Very High |

- Few-Shot performs best but gains over Zero-Shot are modest (+4.2%)
- Self-Verify incurs high latency without accuracy benefit
- CoT does not reliably improve performance

### 2.4 Errors Are Structured

| Outcome | Count | Percentage |
|---------|-------|------------|
| Correct | 125 | 26.0% |
| Invalid Solution | 352 | 73.3% |
| API Error | 3 | 0.6% |

Most failures are **semantically invalid solutions**—models produce rule sequences that do not reach the goal state. Parsing errors are negligible, indicating models understand output format but fail at reasoning.

### 2.5 Unsolved Puzzles

A subset of hard puzzles (e.g., 022, 023, 024) achieve **0% accuracy across all configurations**. These represent genuine reasoning bottlenecks, not prompting failures.

---

## 3. Interpretation

### 3.1 Why Prompting Fails

1. **No lookahead**: Models generate solutions in a single pass without search or backtracking
2. **No verification**: Self-Verify does not reliably detect invalid solutions
3. **Verbosity ≠ correctness**: CoT increases output length without improving semantic accuracy

### 3.2 What Difficulty Reveals

The sharp accuracy drop from easy (51.7%) to hard (6.1%) indicates:
- Easy puzzles succeed via pattern matching
- Hard puzzles require multi-step planning that models lack
- Distractors successfully mislead models

### 3.3 Model Scale

The 17B Scout outperforming the 70B model suggests:
- Instruction tuning matters more than raw scale for this task
- Larger context ≠ better multi-step reasoning
- Architecture differences (e.g., attention patterns) may be critical

---

## 4. Conclusions

1. **Overall accuracy is low** (26%)—the benchmark poses genuine difficulty
2. **Difficulty is the dominant factor**—not model size or prompt complexity
3. **Prompt engineering has diminishing returns**—gains plateau quickly
4. **Errors are semantic, not syntactic**—models fail at reasoning, not formatting
5. **Some puzzles are unsolvable**—indicating fundamental reasoning gaps

### Implications

- **For evaluation**: Use difficulty-stratified metrics; aggregate accuracy is misleading
- **For model development**: Focus on planning and verification, not prompt engineering
- **For benchmarking**: Hard puzzles provide ceiling-level signal for reasoning improvements

---

## References

- **Notebook**: `notebooks/llm_evaluation.ipynb`
- **Results**: `results/evaluation_summary.csv`, `results/evaluation_detailed.csv`
- **Figures**: `results/model_prompt_comparison.png`, `results/difficulty_analysis.png`

