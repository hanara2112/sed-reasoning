# LaTeX Report

## Compiling the Report

### Using Overleaf (Recommended)
1. Go to [Overleaf](https://www.overleaf.com/)
2. Create a new project
3. Upload `main.tex`
4. Click "Compile"

### Using Local LaTeX Installation

```bash
cd report/
pdflatex main.tex
pdflatex main.tex  # Run twice for TOC
```

### Required Packages
- geometry, graphicx, booktabs
- amsmath, amssymb
- hyperref, xcolor
- listings, float, subcaption
- algorithm, algpseudocode
- tikz, pgfplots
- tcolorbox, enumitem
- multirow, array

Most are included in standard TeX distributions (TeX Live, MiKTeX).

## Report Structure

1. **Introduction** - Motivation, AI alignment context, research questions
2. **Dataset Generation** - Pipeline, generators, difficulty metrics
3. **LLM Evaluation Framework** - Models, prompting techniques
4. **Novel Evaluation Metrics** - Progress Score, Valid Steps Ratio, Composite Score
5. **Results and Analysis** - Performance tables and analysis
6. **Human vs Machine** - Cognitive gap analysis
7. **Why LLMs Fail** - Detailed failure mode analysis
8. **AI Alignment Implications** - Reliability concerns
9. **Future Directions** - Research extensions
10. **Conclusion** - Key contributions and findings

## Figures

To include your generated figures, add them to the report folder and uncomment the figure blocks in the LaTeX source.

Available figures in `results/`:
- `metrics_distributions.png`
- `metrics_by_model.png`
- `metrics_by_prompt.png`
- `human_vs_machine_by_type.png`
- `human_vs_machine_comparison.png`
- `model_comparison.png`
- `difficulty_analysis.png`

