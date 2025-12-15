# LLM Evaluation Module

Evaluates LLMs on SED (String Edit Distance) puzzles using different prompting techniques.

## Supported Models

### FREE Models (Recommended)
| Model | Provider | Limits | API Key |
|-------|----------|--------|---------|
| **Llama 3 8B** | Groq | 30 req/min, 14,400/day | [Get free key](https://console.groq.com/keys) |
| **Llama 3 70B** | Groq | 30 req/min, 14,400/day | Same as above |
| **Mixtral 8x7B** | Groq | 30 req/min, 14,400/day | Same as above |
| Gemini Flash | Google | 15 req/min, daily quota | [Get free key](https://makersuite.google.com/app/apikey) |

### Paid Models
- OpenAI GPT-4o-mini, GPT-4o
- Anthropic Claude

## Quick Start

```bash
# 1. Get FREE Groq API key: https://console.groq.com/keys
# 2. Add to api_keys.env:
GROQ_API_KEY=your-key-here

# 3. Run evaluation
python -m llm_evaluation.run_evaluation \
    --models llama-3-8b mixtral-8x7b \
    --prompt-types few_shot \
    --max-puzzles 10
```

## Prompting Techniques

- **zero_shot**: Direct problem statement
- **few_shot**: Include solved examples
- **cot**: Chain-of-Thought reasoning

## Output

Results saved to `results/`:
- `{model}_{prompt}_summary.json`: Detailed results
- `comparison_{prompt}.txt`: Model comparison report
