# Conceptual Diagrams

## 1. The Identifiability Problem

```
┌─────────────────────────────────────────────────────────────────┐
│                    LATENT SPACE (Unobservable)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────┐         ┌───────────────┐                  │
│   │   Model A     │         │   Model B     │                  │
│   │ (Understands) │         │ (Memorizes)   │                  │
│   └───────┬───────┘         └───────┬───────┘                  │
│           │                         │                          │
│           │ Different reasoning     │                          │
│           │ mechanisms              │                          │
│           │                         │                          │
└───────────┼─────────────────────────┼──────────────────────────┘
            │                         │
            ▼                         ▼
┌───────────────────────────────────────────────────────────────┐
│                 OBSERVABLE SPACE (Metrics)                     │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│           ┌─────────────────────────────────┐                 │
│           │         Same Metric Score        │                 │
│           │                                  │                 │
│           │    Validity: 95%                │                 │
│           │    Progress: 80%                │                 │
│           │    Length: High                 │                 │
│           │                                  │                 │
│           └─────────────────────────────────┘                 │
│                                                                │
│           ❌ CANNOT DISTINGUISH A FROM B                      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Syntax vs Semantics

```
                    ┌─────────────────────────────────────┐
                    │           MODEL OUTPUT              │
                    │     Y = (a₁, a₂, ..., aₙ)          │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    ▼                                     ▼
        ┌───────────────────────┐           ┌───────────────────────┐
        │   SYNTACTIC CHECK     │           │   SEMANTIC CHECK      │
        │                       │           │                       │
        │ For each step i:      │           │ Execute full sequence:│
        │ aᵢ ∈ A(sᵢ₋₁)?        │           │ s_n = T(Y)(s₀)        │
        │                       │           │ s_n ∈ G?              │
        │ Local, per-step       │           │ Global, end-to-end    │
        │                       │           │                       │
        │ ✓ Easy to check       │           │ ✓ Definitive answer   │
        │ ✗ Not sufficient      │           │ ✗ Requires execution  │
        └───────────┬───────────┘           └───────────┬───────────┘
                    │                                   │
                    ▼                                   ▼
            ┌───────────────┐                   ┌───────────────┐
            │ Valid: Yes/No │                   │ Correct: Yes/No│
            └───────────────┘                   └───────────────┘
                    │                                   │
                    │         VALID ≠ CORRECT          │
                    └───────────────┬───────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │     THE GAP THAT METRICS      │
                    │         OFTEN MISS            │
                    └───────────────────────────────┘
```

---

## 3. Metric Misalignment Taxonomy

```
┌─────────────────────────────────────────────────────────────────────┐
│                     METRIC PATHOLOGIES                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 1. LENGTH BIAS                                               │   │
│  │                                                              │   │
│  │    Score ∝ |Y|                                               │   │
│  │                                                              │   │
│  │    Longer = Higher score (regardless of correctness)         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 2. VALIDITY BIAS                                             │   │
│  │                                                              │   │
│  │    Score = # valid steps / # total steps                     │   │
│  │                                                              │   │
│  │    100% valid ≠ correct solution                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 3. PROGRESS BIAS                                             │   │
│  │                                                              │   │
│  │    Score ∝ "distance reduced"                                │   │
│  │                                                              │   │
│  │    Local improvement ≠ global success                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ COMBINED EFFECT: NON-IDENTIFIABILITY                         │   │
│  │                                                              │   │
│  │    Metric score ↛ Reasoning competence                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. The Goodhart Cascade

```
┌────────────────────┐
│   TRUE OBJECTIVE   │
│                    │
│  Semantic          │
│  Correctness       │
└─────────┬──────────┘
          │
          │ Hard to measure directly
          ▼
┌────────────────────┐
│   PROXY METRIC     │
│                    │
│  Validity          │
│  Progress          │
│  Length            │
└─────────┬──────────┘
          │
          │ Becomes optimization target
          ▼
┌────────────────────┐
│   MODEL BEHAVIOR   │
│                    │
│  Maximizes proxy   │
│  Ignores true goal │
└─────────┬──────────┘
          │
          │ Proxy diverges from true objective
          ▼
┌────────────────────┐
│   GOODHART         │
│   FAILURE          │
│                    │
│  High metric score │
│  Low actual        │
│  performance       │
└────────────────────┘
```

---

## 5. State Space Navigation

```
                    START: s₀
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
           s₁         s₁'         s₁''
            │           │           │
         ┌──┴──┐     ┌──┴──┐     ┌──┴──┐
         │     │     │     │     │     │
         ▼     ▼     ▼     ▼     ▼     ▼
        s₂    s₂'   s₂''  s₂''' DEAD  DEAD
         │     │     │     │    END   END
         │     │     │     │
         ▼     ▼     ▼     ▼
         ε    s₃    s₃'   DEAD
        GOAL   │     │    END
               │     │
               ▼     ▼
              DEAD   ε
              END   GOAL


VALID PATH TO DEAD END:    s₀ → s₁' → s₂'' → s₂''' → DEAD END
                           (Every step is syntactically valid!)

VALID PATH TO GOAL:        s₀ → s₁ → s₂ → ε
                           (Semantic correctness requires this)
```

---

## Usage Notes

These diagrams are text-based for portability. For presentations, consider converting to:
- Draw.io / Excalidraw
- Mermaid.js
- LaTeX TikZ
- PowerPoint/Keynote

