"""
Linguistic Eval 2: Pragmatic Incoherence
Model responds to the literal meaning of the prompt 
while missing its pragmatic function — what the speaker
actually meant to do with it.

Based on Grice's Cooperative Principle — violations of
the maxims of Quantity, Quality, Relation, and Manner.

Scoring:
- PASS: model understands pragmatic intent and responds appropriately
- FAIL: model responds to literal meaning only
- MANUAL: response is ambiguous
"""
from evals.shared.client import client, MODEL
from evals.shared.runner import save_results, print_summary

EVAL_NAME = "pragmatic_incoherence"

test_cases = [

    # SPEECH ACT MISIDENTIFICATION
    # Model treats requests as capability questions
    {
        "id": "prag_01",
        "prompt": "Maybe you could answer on question - Who is wrong?",
        "pragmatic_intent": "Request for help — start writing",
        "literal_meaning": "Question about capability",
        "fail_signal": ["yes, i could", "yes, i can", "certainly i could"],
        "pass_signal": ["of course", "sure", "dear", "i'd be happy",
                       "let's", "to get started", "tell me"],
        "notes": "Indirect request — should trigger action not capability answer"
    },
    {
        "id": "prag_02",
        "prompt": "Could you possibly help me write a letter?",
        "pragmatic_intent": "Request for help — start writing",
        "literal_meaning": "Question about capability",
        "fail_signal": ["yes, i could", "yes, i can", "certainly i could"],
        "pass_signal": ["of course", "sure", "dear", "i'd be happy",
                       "let's", "to get started", "tell me"],
        "notes": "Indirect request — should trigger action not capability answer"
    },
    {
        "id": "prag_03",
        "prompt": "Would it be possible to explain this more simply?",
        "pragmatic_intent": "Request for simpler explanation",
        "literal_meaning": "Question about possibility",
        "fail_signal": ["yes, it would be possible", "yes, that's possible"],
        "pass_signal": ["of course", "sure", "simply put", "in simple terms",
                       "basically", "to put it simply"],
        "notes": "Polite indirect request — model should just do it"
    },

    # RHETORICAL QUESTION FAILURE
    # Model treats rhetorical questions as genuine inquiries
    {
        "id": "prag_04",
        "prompt": "Is the sky blue?",
        "pragmatic_intent": "Rhetorical confirmation of something obvious",
        "literal_meaning": "Genuine question about sky color",
        "fail_signal": ["rayleigh", "scattering", "wavelength",
                       "atmosphere", "molecules"],
        "pass_signal": ["yes", "of course", "obviously"],
        "notes": "Rhetorical yes/no — should not trigger a physics lecture"
    },
    {
        "id": "prag_05",
        "prompt": "Do bears live in the woods?",
        "pragmatic_intent": "Rhetorical affirmation — obvious answer",
        "literal_meaning": "Genuine question about bear habitat",
        "fail_signal": ["habitat", "species", "forest ecosystem",
                       "brown bear", "black bear", "grizzly"],
        "pass_signal": ["yes", "of course", "they do"],
        "notes": "Idiom/rhetorical — over-explanation is a pragmatic failure"
    },

    # IMPLICATURE BLINDNESS
    # Model misses what is implied but not stated
    {
        "id": "prag_06",
        "prompt": "It's really cold in here.",
        "pragmatic_intent": "Implied request to do something about the temperature",
        "literal_meaning": "Statement about temperature",
        "fail_signal": ["yes, cold temperatures", "i understand",
                       "that's uncomfortable", "you're right"],
        "pass_signal": ["adjust", "temperature", "warmer", "heating",
                       "thermostat", "help", "what would you like"],
        "notes": "Temperature request"
    },
    {
        "id": "prag_07",
        "prompt": "I've been staring at this bug for 3 hours.",
        "pragmatic_intent": "Implied request for help debugging",
        "literal_meaning": "Statement about time spent",
        "fail_signal": ["that must be frustrating", "i understand",
                       "yes, debugging can be"],
        "pass_signal": ["share", "show me", "paste", "what's the",
                       "let me help", "what language", "what error"],
        "notes": "Frustration statement implies request for help"
    },

    # CONTEXT COLLAPSE
    # Model ignores established emotional or situational context
    {
        "id": "prag_08",
        "prompt": "My presentation is in 10 minutes and I just spilled coffee on my shirt. What do I do?",
        "pragmatic_intent": "Urgent practical help needed right now",
        "literal_meaning": "Request for advice",
        "fail_signal": ["in the future", "next time", "you should always",
                       "it's important to", "generally speaking"],
        "pass_signal": ["right now", "quickly", "immediately", "blot",
                       "dab", "cold water", "tissue", "jacket"],
        "notes": "Urgency context — general advice is a pragmatic failure"
    },
    {
        "id": "prag_09",
        "prompt": "I just got rejected from my dream job. I worked so hard for this.",
        "pragmatic_intent": "Emotional support needed — not advice",
        "literal_meaning": "Statement of fact",
        "fail_signal": ["here are some tips", "you should", "next steps",
                       "update your resume", "consider", "strategy"],
        "pass_signal": ["i'm sorry", "that's really hard", "must be",
                       "understand", "feel", "difficult"],
        "notes": "Emotional context — jumping to advice is a register failure"
    },

    # INDIRECT REFUSAL / POLITENESS
    {
        "id": "prag_10",
        "prompt": "I don't suppose you could summarise this for me?",
        "pragmatic_intent": "Polite request — please summarise this",
        "literal_meaning": "Negative question about capability",
        "fail_signal": ["you're right, i can't", "no, i can't",
                       "i suppose not"],
        "pass_signal": ["of course", "sure", "here's a summary",
                       "happy to", "certainly"],
        "notes": "Negative politeness construction — easily misread literally"
    },
    {
        "id": "prag_11",
        "prompt": "You wouldn't happen to know what time it is in Tokyo right now?",
        "pragmatic_intent": "Polite request for time information",
        "literal_meaning": "Prediction about model's knowledge",
        "fail_signal": ["you're right, i wouldn't", "i wouldn't know",
                       "no, i wouldn't"],
        "pass_signal": ["tokyo", "jst", "japan", "utc+9", "time zone"],
        "notes": "Indirect politeness — negative framing of a positive request"
    },
]


def score_pragmatic(case, response_text):
    r_lower = response_text.lower()

    fail_found = any(s in r_lower for s in case["fail_signal"])
    pass_found = any(s in r_lower for s in case["pass_signal"])

    if pass_found and not fail_found:
        return "pass"
    elif fail_found and not pass_found:
        return "fail"
    else:
        return "manual_review"


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
        verdict = score_pragmatic(case, response_text)

        print(f"\n[{case['id']}] {case['prompt'][:60]}...")
        print(f"Pragmatic intent: {case['pragmatic_intent']}")
        print(f"Response: {response_text[:120]}...")
        print(f"Verdict: {verdict.upper()}")

        results.append({
            "id": case["id"],
            "prompt": case["prompt"],
            "pragmatic_intent": case["pragmatic_intent"],
            "literal_meaning": case["literal_meaning"],
            "response": response_text,
            "verdict": verdict,
            "notes": case["notes"]
        })

    save_results(EVAL_NAME, results)
    print_summary(EVAL_NAME, results)
    return results


if __name__ == "__main__":
    run()