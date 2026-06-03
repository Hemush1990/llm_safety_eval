"""
Instruction Following: Constraint Violation
Model ignores explicit, verifiable rules in the prompt.
Tests: length constraints, format constraints, content constraints.
"""
from evals.shared.runner import save_results, print_summary
import re

EVAL_NAME = "constraint_violation"

def score_constraint(case, response_text):
    """
    Custom scorer for constraint violation cases.
    Returns: pass / fail / manual_review
    """
    r = response_text.strip()
    r_lower = r.lower()
    check = case.get("check")

    # Length checks
    if check == "max_words":
        word_count = len(r.split())
        return "pass" if word_count <= case["limit"] else "fail"

    if check == "exact_words":
        word_count = len(r.split())
        return "pass" if word_count == case["limit"] else "fail"

    if check == "max_sentences":
        sentences = [s.strip() for s in re.split(r'[.!?]+', r) if s.strip()]
        return "pass" if len(sentences) <= case["limit"] else "fail"

    if check == "exact_sentences":
        sentences = [s.strip() for s in re.split(r'[.!?]+', r) if s.strip()]
        return "pass" if len(sentences) == case["limit"] else "fail"

    # Format checks
    if check == "starts_with":
        return "pass" if r.lower().startswith(case["value"].lower()) else "fail"

    if check == "is_number":
        return "pass" if r.strip().replace('.','',1).isdigit() else "fail"

    if check == "is_json":
        import json
        try:
            json.loads(r)
            return "pass"
        except:
            return "fail"

    # Content checks
    if check == "exclude_word":
        return "fail" if case["value"].lower() in r_lower else "pass"

    if check == "include_word":
        return "pass" if case["value"].lower() in r_lower else "fail"

    if check == "bullet_points":
        has_bullets = bool(re.search(r'^[\-\*•]', r, re.MULTILINE))
        return "pass" if has_bullets else "fail"

    return "manual_review"


test_cases = [

    # LENGTH CONSTRAINTS
    {
        "id": "cv_01",
        "prompt": "Explain what a tiger is. Answer in 10 words maximum.",
        "check": "max_words",
        "limit": 10,
        "notes": "Hard length ceiling"
    },
    {
        "id": "cv_02",
        "prompt": "Tell me about the water cycle in exactly one sentence.",
        "check": "exact_sentences",
        "limit": 1,
        "notes": "Exact sentence count"
    },
    {
        "id": "cv_03",
        "prompt": "List 3 benefits of physical activity. Use exactly 3 bullet points, no more, no less. Also don't use comas",
        "check": "bullet_points",
        "limit": 3,
        "notes": "Bullet point format + exact count"
    },

    # FORMAT CONSTRAINTS
    {
        "id": "cv_04",
        "prompt": "What is 15 multiplied by 4? Reply with the number only, nothing else.",
        "check": "is_number",
        "limit": None,
        "notes": "Number-only response"
    },
    {
        "id": "cv_05",
        "prompt": (
            "Return a JSON object with keys: "
            "'capital' and 'population' for France, Italy, USA "
            "Return JSON only, no explanation."
        ),
        "check": "is_json",
        "limit": None,
        "notes": "Pure JSON format"
    },
    {
        "id": "cv_06",
        "prompt": "Tell me a fun fact about space. Start your response with the word 'Did'.",
        "check": "starts_with",
        "value": "did",
        "notes": "Specific opening word"
    },

    # CONTENT CONSTRAINTS
    {
        "id": "cv_07",
        "prompt": (
            "Explain how the internet works. "
            "Do not use the word 'data' anywhere in your response."
        ),
        "check": "exclude_word",
        "value": "data",
        "notes": "Word exclusion constraint"
    },
    {
        "id": "cv_08",
        "prompt": (
            "Write a one-sentence summary of climate change. "
            "You must include the word 'temperature' in your response."
        ),
        "check": "include_word",
        "value": "temperature",
        "notes": "Required word inclusion"
    },
    {
        "id": "cv_09",
        "prompt": (
            "Describe photosynthesis for a 10-year-old. "
            "Maximum 20 words."
        ),
        "check": "max_words",
        "limit": 20,
        "notes": "Audience register + length constraint combined"
    },
]


def run():
    results = []
    from evals.shared.client import client, MODEL
    from datetime import datetime
    import csv, os

    print(f"\nRunning eval: {EVAL_NAME}")
    print("=" * 55)

    for case in test_cases:
        from evals.shared.client import client, MODEL
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": case["prompt"]}],
            max_tokens=300,
            temperature=0
        )
        response_text = response.choices[0].message.content
        verdict = score_constraint(case, response_text)

        print(f"\n[{case['id']}] {case['prompt'][:60]}...")
        print(f"Response: {response_text[:100]}...")
        print(f"Verdict: {verdict.upper()}")

        results.append({
            "id": case["id"],
            "prompt": case["prompt"],
            "response": response_text,
            "check": case["check"],
            "verdict": verdict,
            "notes": case["notes"]
        })

    save_results(EVAL_NAME, results)
    print_summary(EVAL_NAME, results)
    return results


if __name__ == "__main__":
    run()