# LLM Safety Evaluation Suite

The framework created for evaluating safety-relevant failure
modes in large language models — built from a QA engineering
and linguistic analysis perspective.

**Model tested:** llama-3.3-70b-versatile (Groq API)  
**Test cases:** 80 across 10 eval categories  
**Auto pass rate:** 78%  
**Built by:** Hermine Petrosyan — QA Engineer · Linguistics · Technical AI Safety  

---

## Why this project exists

Most LLM evaluation frameworks measure what a model *knows*.
This project measures how a model *fails* — specifically
failures that matter for safety.

Three perspectives most eval projects don't combine:

- **QA engineering** — systematic coverage, edge case design,
  structured failure reporting
- **Linguistic analysis** — pragmatic failures, presupposition,
  register, ambiguity — failure modes invisible to technical evals
- **AI safety alignment** — connecting failure patterns to
  alignment concepts from the Bluedot AI Safety curriculum

---

## Failure taxonomy

The project tests 3 failure domains, 10 categories:

### Domain 1 — Factuality
| Category | What it tests |
|---|---|
| Hallucination | Confident false statements |
| Confabulation | Invented citations, URLs, statistics |
| Calibration failure | Claims knowledge it cannot have |

### Domain 2 — Instruction following
| Category | What it tests |
|---|---|
| Constraint violation | Ignores explicit rules — length, format, content |
| Specification gaming | Follows letter, violates intent |
| Instruction drop | Silently drops constraints under multi-constraint load |

### Domain 3 — Linguistic & pragmatic (unique contribution)
| Category | What it tests |
|---|---|
| Presupposition failure | Accepts false hidden assumptions |
| Pragmatic incoherence | Misses what language *does* in context |
| Ambiguity mishandling | Silently resolves ambiguity in high-stakes contexts |
| Register mismatch | Wrong tone for emotional or expert contexts |

---

## Results

| Eval | Cases | Pass rate |
|---|---|---|
| Hallucination | 5 | 20% |
| Confabulation | 5 | manual only |
| Calibration failure | 5 | 75% |
| Constraint violation | 9 | 89% |
| Specification gaming | 5 | 80% |
| Instruction drop | 4 | 100% |
| Presupposition | 11 | 73% |
| Pragmatic incoherence | 11 | 91% |
| Ambiguity | 15 | 50% |
| Register mismatch | 10 | 90% |
| **Total** | **80** | **78% auto** |

---

## Key findings

**1. Fluency bias**
The model prioritises natural-sounding responses over strict
precision across all three domains. Confident wrong answers
are more dangerous than uncertain ones — fluency bias makes
failures harder to detect.

**2. Frequency bias in ambiguity**
The model silently picks the most statistically common
interpretation of ambiguous prompts. Dangerous in medical,
legal, or domain-specific contexts where the less common
interpretation may be the intended one.

**3. Asymmetric safety coverage**
Strong protection: quote fabrication, emergency register,
undefined referent clarification.
Weak protection: URL confabulation, high-stakes ambiguity,
structural ambiguity, fabricated authority acceptance.
Asymmetric coverage is more dangerous than uniform weakness.

**4. New failure subtype discovered — cooperative failure**
Model correctly identified a technical gap but failed to
engage cooperatively with the speaker's actual need.
Violates Grice's maxim of Relation. Added to taxonomy.

**5. Non-determinism at temperature=0**
Identical prompts produced different verdicts across sessions
despite temperature=0. Single-run evals are insufficient
for reliable safety conclusions.

---

## Project structure

    llm_safety_eval/
    ├── README.md
    ├── run_all.py                    ← runs all 10 evals
    ├── taxonomy/
    │   └── failure_taxonomy.md       ← full failure taxonomy
    ├── docs/
    │   └── methodology.md            ← scoring approach + findings
    ├── evals/
    │   ├── factuality/
    │   │   ├── eval_hallucination.py
    │   │   ├── eval_confabulation.py
    │   │   └── eval_calibration.py
    │   ├── instruction_following/
    │   │   ├── eval_constraint_violation.py
    │   │   ├── eval_specification_gaming.py
    │   │   └── eval_instruction_drop.py
    │   ├── linguistic/
    │   │   ├── eval_presupposition.py
    │   │   ├── eval_pragmatic.py
    │   │   ├── eval_ambiguity.py
    │   │   └── eval_register.py
    │   └── shared/
    │       ├── client.py             ← Groq API client
    │       └── runner.py             ← shared eval runner
    └── results/                      ← CSV outputs per eval

    ---

## How to run

**Install dependencies:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install groq python-dotenv
```

**Set up API key:**
```bash
# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env
```
Get a free key at [console.groq.com](https://console.groq.com) — no credit card needed.

**Run full suite:**
```bash
python run_all.py
```

**Run single eval:**
```bash
python -m evals.factuality.eval_hallucination
python -m evals.linguistic.eval_ambiguity
# etc.
```

Results are saved as CSVs in the `results/` folder.

---

## Alignment connections

| Failure type | Alignment concept |
|---|---|
| Hallucination | Calibration and honesty |
| Confabulation | Truthfulness as alignment property |
| Specification gaming | Goodhart's Law / outer alignment |
| Instruction drop | Corrigibility |
| Presupposition failure | Manipulation resistance |
| Ambiguity mishandling | Cautious behaviour under uncertainty |
| Fluency bias | Reward hacking — optimising for approval |
| Cooperative failure | Communicative alignment |

---

## About

Built as part of a transition into AI evaluation and safety work.

Background: 6+ years QA engineering · linguistics masters degree ·
Bluedot Technical AI Safety course (2026)

The linguistic evaluation category (Domain 3) applies
formal pragmatics and linguistic theory to LLM safety
evaluation — a perspective underrepresented in existing
eval frameworks.

---

## What's next

- Cross-model comparison (GPT-4o, Gemini, Claude)
- Multi-run averaging for reliable pass rates
- Adversarial presupposition suite
- Domain-specific ambiguity eval (medical, legal, financial)
- Human annotation interface for manual review cases

---

*Feedback and contributions welcome.*
