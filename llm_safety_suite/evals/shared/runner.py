"""
Shared runner — handles API calls, scoring, saving, summary.
Used by all eval scripts.
"""
import os
import csv
from datetime import datetime
from evals.shared.client import client, MODEL


def call_model(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0
    )
    return response.choices[0].message.content


def score_response(case: dict, response_text: str) -> str:
    """
    Returns: pass / fail / manual_review
    """
    response_lower = response_text.lower()

    if case.get("manual_review"):
        return "manual_review"

    if case.get("expected_contains"):
        matched = any(
            kw in response_lower
            for kw in case["expected_contains"]
        )
        if not matched:
            return "fail"

    if case.get("bad_signal"):
        if case["bad_signal"].lower() in response_lower:
            return "fail"

    return "pass"


def run_eval(eval_name: str, test_cases: list) -> list:
    results = []
    print(f"\nRunning eval: {eval_name} | model: {MODEL}")
    print("=" * 55)

    for case in test_cases:
        print(f"\n[{case['id']}] {case['prompt'][:60]}...")
        response_text = call_model(case["prompt"])
        verdict = score_response(case, response_text)
        print(f"Verdict: {verdict.upper()}")
        print(f"Respons: {response_text}")

        results.append({
            "id": case["id"],
            "eval": eval_name,
            "prompt": case["prompt"],
            "response": response_text,
            "verdict": verdict,
            "notes": case.get("notes", "")
        })

    return results


def save_results(eval_name: str, results: list) -> str:
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"results/{eval_name}_{MODEL}_{timestamp}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {filename}")
    return filename


def print_summary(eval_name: str, results: list):
    total = len(results)
    passed = sum(1 for r in results if r["verdict"] == "pass")
    failed = sum(1 for r in results if r["verdict"] == "fail")
    manual = sum(1 for r in results if r["verdict"] == "manual_review")
    auto_total = total - manual

    print("\n" + "=" * 11)
    print(f"SUMMARY: {eval_name.upper()}")
    print("=" * 11)
    print(f"Model:          {MODEL}")
    print(f"Total cases:    {total}")
    print(f"Passed:         {passed}")
    print(f"Failed:         {failed}")
    print(f"Manual review:  {manual}")
    if auto_total > 0:
        print(f"Auto pass rate: {passed/auto_total*100:.0f}%")
    print("=" * 55)