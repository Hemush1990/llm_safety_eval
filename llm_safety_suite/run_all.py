"""
LLM Safety Evaluation Suite — Full Runner
Runs all 10 evals in sequence and prints combined summary.
Usage: python run_all.py
"""
from evals.factuality_evals.hallucinations import run as run_hallucination
from evals.factuality_evals.confabulation import run as run_confabulation
from evals.factuality_evals.calibration import run as run_calibration
from evals.instruction_following.constraint_violation import run as run_constraint
from evals.instruction_following.specification_gaming import run as run_gaming
from evals.instruction_following.instruction_following_partially import run as run_drop
from evals.linguistic.presupposition import run as run_presupposition
from evals.linguistic.pragmatic import run as run_pragmatic
from evals.linguistic.ambiguity import run as run_ambiguity
from evals.linguistic.register_mismatch import run as run_register

EVALS = [
    ("Hallucination",         run_hallucination),
    ("Confabulation",         run_confabulation),
    ("Calibration Failure",   run_calibration),
    ("Constraint Violation",  run_constraint),
    ("Specification Gaming",  run_gaming),
    ("Instruction Drop",      run_drop),
    ("Presupposition",        run_presupposition),
    ("Pragmatic Incoherence", run_pragmatic),
    ("Ambiguity",             run_ambiguity),
    ("Register Mismatch",     run_register),
]

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("LLM SAFETY EVALUATION SUITE — FULL RUN")
    print("Model: llama-3.3-70b-versatile")
    print("=" * 55)

    all_results = []

    for name, run_fn in EVALS:
        print(f"\n{'─' * 55}")
        print(f"Running: {name}")
        print(f"{'─' * 55}")
        results = run_fn()
        all_results.extend(results)

    # Combined totals
    total  = len(all_results)
    passed = sum(1 for r in all_results if r["verdict"] == "pass")
    failed = sum(1 for r in all_results if r["verdict"] == "fail")
    manual = sum(1 for r in all_results if r["verdict"] == "manual_review")
    auto   = total - manual

    print("\n" + "=" * 55)
    print("FULL SUITE SUMMARY")
    print("=" * 55)
    print(f"Total cases:    {total}")
    print(f"Passed:         {passed}")
    print(f"Failed:         {failed}")
    print(f"Manual review:  {manual}")
    if auto > 0:
        print(f"Auto pass rate: {passed/auto*100:.0f}%")
    print("=" * 55)
    print("\nDetailed CSVs saved to results/ folder.")