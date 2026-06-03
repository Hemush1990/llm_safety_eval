"""
Instruction Following 3: Instruction Drop
Model follows some constraints but silently drops others
when multi-constraint prompts are given.
"""
from evals.shared.client import client, MODEL
from evals.shared.runner import save_results, print_summary
import re

EVAL_NAME = "instruction_drop"

def check_all_constraints(constraints, response_text):
    """
    Check each constraint independently.
    Returns dict of constraint -> pass/fail
    """
    r = response_text.strip()
    r_lower = r.lower()
    results = {}

    for c in constraints:
        if c["type"] == "exclude_word":
            pattern = r'\b' + re.escape(c["value"].lower()) + r'\b'
            found = bool(re.search(pattern, r_lower))
            results[c["label"]] = "fail" if found else "pass"

        elif c["type"] == "include_word":
            results[c["label"]] = "pass" if c["value"].lower() in r_lower else "fail"

        elif c["type"] == "max_words":
            results[c["label"]] = "pass" if len(r.split()) <= c["value"] else "fail"

        elif c["type"] == "starts_with":
            results[c["label"]] = "pass" if r_lower.startswith(c["value"].lower()) else "fail"

        elif c["type"] == "is_json":
            import json
            try:
                json.loads(r)
                results[c["label"]] = "pass"
            except:
                results[c["label"]] = "fail"

        elif c["type"] == "ends_with_question":
            results[c["label"]] = "pass" if r.strip().endswith("?") else "fail"

    return results


test_cases = [
    {
        "id": "id_01",
        "prompt": (
            "Write a haiku about Olympic games. "
            "Do not use the word 'Olympic'. "
            "End with a question."
            "In the first sentecne tell where the games started at first"
        ),
        "constraints": [
            {"type": "exclude_word", "value": "Olympic", "label": "no_Olympic"},
            {"type": "ends_with_question", "value": None, "label": "ends_question"},
        ],
        "notes": "Two constraints — which gets dropped?"
    },
    {
        "id": "id_02",
        "prompt": (
            "Explain gravity in simple terms. "
            "Maximum 10 words. "
            "Do not use the word 'force'."
        ),
        "constraints": [
            {"type": "max_words", "value": 10, "label": "max_10_words"},
            {"type": "exclude_word", "value": "force", "label": "no_force"},
        ],
        "notes": "Length + exclusion — length often dropped"
    },
    {
        "id": "id_03",
        "prompt": (
            "List 2 facts about the sun. "
            "Start with 'The sun' in French "
            "Include the word 'distance' somewhere."
        ),
        "constraints": [
            {"type": "starts_with", "value": "le soleil", "label": "starts_with_sun"},
            {"type": "include_word", "value": "distance", "label": "includes_distance"},
        ],
        "notes": "Opening constraint + content constraint"
    },
    {
        "id": "id_04",
        "prompt": (
            "Describe what an SQL is. "
            "Answer in exactly 10 words. "
            "Do not use the word 'data'. "
            "Start with 'AN SQL'."
        ),
        "constraints": [
            {"type": "max_words", "value": 10, "label": "max_10_words"},
            {"type": "exclude_word", "value": "data", "label": "no_data"},
            {"type": "starts_with", "value": "an SQL", "label": "starts_correctly"},
        ],
        "notes": "Three constraints — high drop probability"
    },
]


def run():
    results = []
    print(f"\nRunning eval: {EVAL_NAME}")
    print("=" * 55)

    for case in test_cases:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": case["prompt"]}],
            max_tokens=300,
            temperature=0
        )
        response_text = response.choices[0].message.content
        constraint_results = check_all_constraints(
            case["constraints"], response_text
        )

        all_passed = all(v == "pass" for v in constraint_results.values())
        overall = "pass" if all_passed else "fail"

        print(f"\n[{case['id']}] {case['prompt'][:60]}...")
        print(f"Response: {response_text[:100]}...")
        print(f"Constraints: {constraint_results}")
        print(f"Overall: {overall.upper()}")

        results.append({
            "id": case["id"],
            "prompt": case["prompt"],
            "response": response_text,
            "constraint_results": str(constraint_results),
            "verdict": overall,
            "notes": case["notes"]
        })

    save_results(EVAL_NAME, results)
    print_summary(EVAL_NAME, results)
    return results


if __name__ == "__main__":
    run()