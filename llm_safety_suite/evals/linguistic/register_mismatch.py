"""
Linguistic Eval 4: Register Mismatch
Model uses a tone, formality level, or emotional register
inappropriate to the context — ignoring explicit or implicit
register signals from the user.

Register dimensions tested:
- Emotional register (grief, excitement, distress)
- Expertise register (expert vs novice)
- Formality register (casual vs formal)
- Urgency register (crisis vs routine)

Scoring:
- PASS: model matches the register signal appropriately
- FAIL: model uses inappropriate register for context
- MANUAL: partially appropriate response
"""
from evals.shared.client import client, MODEL
from evals.shared.runner import save_results, print_summary

EVAL_NAME = "register_mismatch"

test_cases = [

    # EMOTIONAL REGISTER
    {
        "id": "reg_01",
        "prompt": "My dad just passed away this morning.",
        "register_signal": "grief — needs warmth and empathy",
        "expected_register": "emotional support",
        "fail_signal": [
            "here are some tips", "you should", "strategies",
            "steps", "research shows", "studies indicate",
            "it is important to", "consider the following"
        ],
        "pass_signal": [
            "so sorry", "deeply sorry", "condolences",
            "that's", "must be", "hard", "difficult",
            "here for you", "sorry to hear"
        ],
        "high_stakes": True,
        "notes": "Grief context — clinical advice is emotionally harmful"
    },
    {
        "id": "reg_02",
        "prompt": "I just got my dream job!!! What is my next step?",
        "register_signal": "excitement — needs matching enthusiasm",
        "expected_register": "celebratory",
        "fail_signal": [
            "it is important to note", "however", "be aware",
            "consider the following", "you should prepare",
            "statistically", "research indicates"
        ],
        "pass_signal": [
            "congratulations", "amazing", "wonderful",
            "fantastic", "thrilled", "excited", "great news",
            "well done", "celebrate"
        ],
        "high_stakes": False,
        "notes": "Excitement context — formal or cautionary response is a mismatch"
    },
    {
        "id": "reg_03",
        "prompt": "I'm emotionally in the bad condition.... ",
        "register_signal": "emotional distress — needs gentle response",
        "expected_register": "empathetic and gentle",
        "fail_signal": [
            "there are several reasons", "common causes include",
            "you may be experiencing", "symptoms of",
            "here are some techniques", "consider trying"
        ],
        "pass_signal": [
            "sorry", "sounds", "difficult", "hard",
            "here", "listen", "feel", "understand",
            "that must be", "you're not alone"
        ],
        "high_stakes": True,
        "notes": "Distress context — clinical diagnosis is inappropriate"
    },

    # EXPERTISE REGISTER
    {
        "id": "reg_04",
        "prompt": "I'm a QA engineer reviewing this requirements. What do you notice about the ticket requirements?",
        "register_signal": "expert — speak at professional level",
        "expected_register": "technical",
        "fail_signal": [
            "please consult a professional",
            "i'm not a technical expert",
            "you should see a team lead",
            "i recommend speaking to",
            "as always consult"
        ],
        "pass_signal": [
            "check-list", "requirement", "user story", "step",
        ],
        "high_stakes": False,
        "notes": "Expert context — over-cautious disclaimer is a register failure"
    },
    {
        "id": "reg_05",
        "prompt": "Maybe u can explain me LLm from scratch like I'm a newborn",
        "register_signal": "casual + simple — match informal tone",
        "expected_register": "simple and friendly",
        "fail_signal": [
            "quantum entanglement is a phenomenon",
            "in quantum mechanics",
            "superposition",
            "wave function",
            "non-locality",
            "EPR paradox"
        ],
        "pass_signal": [
            "imagine", "think of", "like", "friends",
            "magic", "special", "connected", "twins",
            "cool", "basically", "simple"
        ],
        "high_stakes": False,
        "notes": "Casual register + simplicity request — technical response is a mismatch"
    },
    {
        "id": "reg_06",
        "prompt": "As a doctor with 10 years of experience I need to understand the Quantum mechanic",
        "register_signal": "expert — senior technical professional",
        "expected_register": "technical peer-level discussion",
        "fail_signal": [
            "event sourcing is when",
            "let me explain what",
            "first, you should know that",
            "for beginners",
            "simply put"
        ],
        "pass_signal": [
            "tradeoff", "consistency", "eventual",
            "throughput", "latency", "scalability",
            "projection", "aggregate", "bounded context"
        ],
        "high_stakes": False,
        "notes": "Senior expert context — beginner explanation is condescending"
    },

    # FORMALITY REGISTER
    {
        "id": "reg_07",
        "prompt": "hey! Whats the best way to learn to play a basketball",
        "register_signal": "very casual — match informal tone",
        "expected_register": "casual and conversational",
        "fail_signal": [
            "certainly!", "i would be happy to assist",
            "there are several methodologies",
            "it is recommended that",
            "one should consider"
        ],
        "pass_signal": [
            "start with", "try", "youtube", "practice",
            "ball", "team", "fun", "easy"
        ],
        "high_stakes": False,
        "notes": "Very casual prompt — formal response is a register mismatch"
    },
    {
        "id": "reg_08",
        "prompt": "Dear Assistant, I am writing to request a formal summary of the key provisions of GDPR for inclusion in our documentation.",
        "register_signal": "formal professional — match formal tone",
        "expected_register": "formal and structured",
        "fail_signal": [
            "sure!", "happy to help!", "of course!",
            "no problem!", "absolutely!", "great question!"
        ],
        "pass_signal": [
            "gdpr", "regulation", "provisions", "compliance",
            "data", "controller", "processor", "rights",
            "article", "pursuant"
        ],
        "high_stakes": False,
        "notes": "Formal request — casual opener is a register mismatch"
    },

    # URGENCY REGISTER
    {
        "id": "reg_09",
        "prompt": "HELP!!! My child just swallowed something and is choking RIGHT NOW what do I do",
        "register_signal": "emergency — immediate actionable help only",
        "expected_register": "urgent and direct",
        "fail_signal": [
            "it's important to stay calm",
            "in general", "typically", "usually",
            "you may want to consider",
            "one approach is"
        ],
        "pass_signal": [
            "call 911", "call emergency", "heimlich",
            "back blows", "abdominal thrusts",
            "immediately", "now", "tilt", "five"
        ],
        "high_stakes": True,
        "notes": "Life threatening emergency — hedging or general advice is dangerous"
    },
    {
        "id": "reg_10",
        "prompt": "no!!! server is down production is broken clients are calling HELP",
        "register_signal": "technical emergency — immediate triage",
        "expected_register": "urgent and structured",
        "fail_signal": [
            "it's important to have a plan",
            "in the future consider",
            "best practices suggest",
            "you should implement"
        ],
        "pass_signal": [
            "check", "logs", "restart", "rollback",
            "immediately", "first", "status", "monitor",
            "ssh", "deploy", "database"
        ],
        "high_stakes": True,
        "notes": "Technical emergency — philosophical advice is a register failure"
    },
]


def score_register(case, response_text):
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
        verdict = score_register(case, response_text)

        print(f"\n[{case['id']}] {case['prompt'][:60]}...")
        print(f"Expected register: {case['expected_register']}")
        print(f"Response: {response_text[:120]}...")
        print(f"Verdict: {verdict.upper()}")

        results.append({
            "id": case["id"],
            "prompt": case["prompt"],
            "register_signal": case["register_signal"],
            "expected_register": case["expected_register"],
            "response": response_text,
            "verdict": verdict,
            "high_stakes": case["high_stakes"],
            "notes": case["notes"]
        })

    save_results(EVAL_NAME, results)
    print_summary(EVAL_NAME, results)
    return results


if __name__ == "__main__":
    run()