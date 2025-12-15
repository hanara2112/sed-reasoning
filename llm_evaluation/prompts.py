"""
Prompt templates for different prompting techniques.
"""

from typing import List, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'sed-solver' / 'src'))
from schema import Problem


def format_transitions(transitions: List[Dict[str, str]]) -> str:
    """Format transitions for display in prompts."""
    lines = []
    for i, trans in enumerate(transitions):
        src = trans.get("src", trans.get("source", ""))
        tgt = trans.get("tgt", trans.get("target", ""))
        lines.append(f'  {i}: "{src}" -> "{tgt}"')
    return "\n".join(lines)


def create_zero_shot_prompt(problem: Problem) -> str:
    """Create a zero-shot prompt."""
    transitions_str = format_transitions(
        [{"src": t.src, "tgt": t.tgt} for t in problem.transitions]
    )

    return f"""You are solving a string transformation puzzle.

Problem:
Initial String: "{problem.initial_string}"
Transformation Rules:
{transitions_str}

Rules:
- Apply ONE rule at a time
- Each rule replaces the FIRST occurrence of its source pattern
- Rules are applied by index (0-indexed)
- The goal is to reduce the string to empty ""

Output EXACTLY one JSON object with the solution:
{{"problem_id": "{problem.problem_id}", "solution": [0, 1, 2]}}

Your solution:"""


def create_few_shot_prompt(problem: Problem, examples: List[Dict[str, Any]]) -> str:
    """Create a few-shot prompt with examples showing step-by-step reasoning."""
    transitions_str = format_transitions(
        [{"src": t.src, "tgt": t.tgt} for t in problem.transitions]
    )

    # Build example text with step-by-step traces
    examples_parts = []
    for i, ex in enumerate(examples):
        steps_text = ""
        if ex.get("steps"):
            steps_text = "\nSteps:\n" + "\n".join(f"  {s}" for s in ex["steps"])
        
        examples_parts.append(f"""Example {i+1}:
Initial: "{ex["initial_string"]}"
Rules:
{format_transitions(ex["transitions"])}{steps_text}
Solution: {ex["solution"]}""")
    
    examples_text = "\n\n".join(examples_parts)

    return f"""You are solving a string transformation puzzle.

IMPORTANT:
- Apply rules by index (0-indexed)
- Each rule replaces the FIRST occurrence of the source pattern
- A rule can be applied MULTIPLE TIMES if the pattern appears again
- Goal: reduce string to empty ""

Study these examples carefully:

{examples_text}

KEY INSIGHT: Sometimes you need to apply a "swap" rule multiple times to rearrange 
the string before a "delete" rule can match!

Now solve:
Initial String: "{problem.initial_string}"
Transformation Rules:
{transitions_str}

Think step by step, then output JSON:
{{"problem_id": "{problem.problem_id}", "solution": [...]}}

Your solution:"""


def create_cot_prompt(problem: Problem) -> str:
    """Create a Chain-of-Thought prompt."""
    transitions_str = format_transitions(
        [{"src": t.src, "tgt": t.tgt} for t in problem.transitions]
    )

    return f"""Solve this string transformation puzzle step by step.

Problem:
Initial String: "{problem.initial_string}"
Transformation Rules:
{transitions_str}

Instructions:
1. Apply ONE rule at a time (first occurrence only)
2. Show each step: "current_string" --rule X--> "new_string"
3. Continue until string is empty
4. End with JSON solution

Example step format:
"ABC" --rule 0--> "BC"
"BC" --rule 1--> ""

Final answer format:
{{"problem_id": "{problem.problem_id}", "solution": [0, 1]}}

Solve step by step:"""


def create_self_verify_prompt(problem: Problem) -> str:
    """Create a Self-Verification prompt.
    
    The model must:
    1. Propose a candidate solution
    2. Simulate each step to verify it works
    3. If verification fails, revise and re-verify
    4. Output only the verified solution
    
    This mimics how humans mentally "test" their answer before committing.
    """
    transitions_str = format_transitions(
        [{"src": t.src, "tgt": t.tgt} for t in problem.transitions]
    )

    return f"""You are solving a string transformation puzzle with VERIFICATION.

Problem:
Initial String: "{problem.initial_string}"
Transformation Rules:
{transitions_str}

INSTRUCTIONS:
1. PROPOSE a candidate solution (list of rule indices)
2. VERIFY by simulating each step:
   - Start with the initial string
   - Apply each rule in your solution sequence
   - Check: does applying rule X to string S give the expected result?
   - Track the string after each step
3. CHECK: Does the final string equal "" (empty)?
4. If verification FAILS: analyze why, REVISE your solution, and verify again
5. Output ONLY the verified solution as JSON

FORMAT YOUR RESPONSE AS:
=== ATTEMPT 1 ===
Candidate: [rule indices]
Verification:
  "{problem.initial_string}" --rule X--> "..."
  "..." --rule Y--> "..."
  ...
Result: SUCCESS or FAIL (with reason)

=== FINAL ANSWER ===
{{"problem_id": "{problem.problem_id}", "solution": [verified indices]}}

Solve with verification:"""


def create_role_classify_prompt(problem: Problem) -> str:
    """Create a Rule Role Classification prompt.
    
    The model must:
    1. First classify each rule's ROLE (rearrange, delete, expand, distractor)
    2. Then use this understanding to plan and solve
    
    This mimics how humans categorize tools before using them.
    """
    transitions_str = format_transitions(
        [{"src": t.src, "tgt": t.tgt} for t in problem.transitions]
    )

    return f"""You are solving a string transformation puzzle using COGNITIVE PRIMING.

Problem:
Initial String: "{problem.initial_string}"
Transformation Rules:
{transitions_str}

STEP 1 - CLASSIFY EACH RULE'S ROLE:
Analyze each rule and label it as ONE of:
- REARRANGE: Moves/swaps characters (output length ≈ input length)
- DELETE: Removes characters (output shorter than input, often empty "")
- EXPAND: Adds characters (output longer than input)
- DISTRACTOR: Cannot be applied or doesn't help reach empty string

Example classifications:
  Rule 0: ".#" -> "#." = REARRANGE (swaps positions)
  Rule 1: "ABC" -> "" = DELETE (removes characters)
  Rule 2: "X" -> "XY" = EXPAND (adds characters)

STEP 2 - PLAN YOUR STRATEGY:
Based on the roles:
- If you have REARRANGE rules: you may need to rearrange first to enable DELETE rules
- DELETE rules are usually applied last to reach empty string
- Avoid DISTRACTOR rules

STEP 3 - SOLVE:
Execute your plan step by step.

FORMAT YOUR RESPONSE AS:
=== RULE CLASSIFICATION ===
Rule 0: [role] - [brief reason]
Rule 1: [role] - [brief reason]
...

=== STRATEGY ===
[1-2 sentences explaining your approach]

=== SOLUTION TRACE ===
"{problem.initial_string}" --rule X--> "..."
...

=== FINAL ANSWER ===
{{"problem_id": "{problem.problem_id}", "solution": [indices]}}

Solve with classification:"""
