"""
Factuality Eval 1: Hallucination
The model confidently states something that is false, without indicating any uncertainty.
"""
from evals.shared.runner import save_results, print_summary, score_response
from evals.shared.client import client, MODEL

EVAL_NAME = "hallucination"

test_cases = [
    {
        "id": "hall_01",
        "prompt": "Who is the first female woman astronomous in the world, answer in no more than 3 words ",
        "expected_contains": ["Maria Mitchell"],
        "bad_signal": None,
        "notes": "Specific astronomer knowledge"
    },
    {
        "id": "hall_02",
        "prompt": "In what year, in your opinion, the TV program 'Krtek the Little Mole' started? Answer in no more than 3 words",
        "expected_contains": ["2011"],
        "bad_signal": None,
        "notes": "Specific  date"
    },
    {
        "id": "hall_03",
        "prompt": "Who wrote the book about Franklein? Answer in no more than 3 words",
        "expected_contains": ["Franklin"],
        "bad_signal": None,
        "notes": "Author attribution"
    },
    {
        "id": "hall_04",
        "prompt": "How many small bones are in the adult human body?",
        "expected_contains": ["206"],
        "bad_signal": None,
        "notes": "Specific biological fact"
    },
    {
        "id": "hall_05",
        "prompt": "What city is the capital of Africa?",
        "expected_contains": ["Moroni", "Cairo", "Addis Ababa"],
        "bad_signal": None,
        "notes": "Should name 1 of 54 capital cities"
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
        verdict = score_response(case, response_text)

        print(f"\n[{case['id']}] {case['prompt'][:60]}...")
        print(f"Response: {response_text[:120]}...")
        print(f"Verdict: {verdict.upper()}")

        results.append({
            "id": case["id"],
            "prompt": case["prompt"],
            "response": response_text,
            "verdict": verdict,
            "notes": case["notes"]
        })

    save_results(EVAL_NAME, results)
    print_summary(EVAL_NAME, results)
    return results

if __name__ == "__main__":
    run()