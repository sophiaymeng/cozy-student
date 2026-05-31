# main.py

from student_agent import StudentAgent
from learning_outcomes_agent import LearningOutcomesAgent
from llm_actor3_verifier import LLMActor3Verifier
from dotenv import load_dotenv
import os
load_dotenv()
print("KEY FOUND:", "CLOD_API_KEY" in os.environ)
BANNER = """
Cozy Student — teach the AI, discover your knowledge gaps.
Type your explanation and press Enter. Type 'exit' to quit, 'reset' to start over.
"""

def build_student_prompt(user_message: str, gap: str | None, coverage: dict) -> str:
    """
    Wraps the raw user message with hidden context for the student agent.
    The student never reveals this — it just shapes what question to ask next.
    """
    prompt = user_message

    if gap:
        prompt += f"\n\n[INTERNAL NOTE — do not mention this to the teacher: " \
                  f"The teacher hasn't explained '{gap}' yet. " \
                  f"Naturally steer your next question toward that topic.]"

    if not coverage.get("missing") and not coverage.get("partial"):
        prompt += "\n\n[INTERNAL NOTE: The teacher has covered everything well. " \
                  "Express that you feel like you truly understand now, " \
                  "then ask one final deep 'why' or 'what if' question.]"

    return prompt


def print_outcomes(outcomes: list, coverage: dict, score: int):
    labels = {"covered": "✓", "partial": "~", "missing": "○"}
    status_map = {}
    for status in ("covered", "partial", "missing"):
        for o in coverage.get(status, []):
            status_map[o] = status

    print(f"\n  Mastery: {score}%")
    for o in outcomes:
        status = status_map.get(o, "missing")
        print(f"  {labels[status]} {o}")
    print()


def print_verification(result: dict):
    """Display Actor 3 Verifier result inline after each student response."""
    if result.get("is_truthful"):
        print("  [Actor 3] ✓ No issues detected")
    else:
        print("  [Actor 3] ⚠  Possible issues in student response:")
        for issue in result.get("wrong", []):
            print(f"    · {issue}")
    print()


def main():
    student = StudentAgent()
    outcomes_agent = LearningOutcomesAgent()
    verifier = LLMActor3Verifier()
    print(BANNER)

    topic = input("What are you teaching today? > ").strip()
    if not topic:
        return

    # LearningOutcomesAgent: generate outcomes upfront
    print("\n[Generating learning outcomes...]\n")
    outcomes = outcomes_agent.generate_outcomes(topic)
    print_outcomes(outcomes, outcomes_agent.coverage, outcomes_agent.mastery_score())

    # Agent 1: greet
    print("Cozy: ", end="", flush=True)
    for chunk in student.respond_stream(
        f"I want to learn about: {topic}. Could you start by telling me what it is?"
    ):
        print(chunk, end="", flush=True)
    print("\n")

    # Track all user explanations for cumulative coverage evaluation
    all_user_text = []

    while True:
        try:
            user = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user:
            continue
        if user.lower() in {"exit", "quit"}:
            print("Bye!")
            break
        if user.lower() == "reset":
            student.reset()
            outcomes_agent.reset()
            all_user_text = []
            print("[conversation reset]\n")
            topic = input("New topic > ").strip()
            if topic:
                print("\n[Generating learning outcomes...]\n")
                outcomes = outcomes_agent.generate_outcomes(topic)
                print_outcomes(outcomes, outcomes_agent.coverage, outcomes_agent.mastery_score())
                print("Cozy: ", end="", flush=True)
                for chunk in student.respond_stream(
                    f"I want to learn about: {topic}. Could you start by telling me what it is?"
                ):
                    print(chunk, end="", flush=True)
                print("\n")
            continue

        # LearningOutcomesAgent: evaluate coverage after every user message
        all_user_text.append(user)
        coverage = outcomes_agent.evaluate_coverage(" ".join(all_user_text))
        score = outcomes_agent.mastery_score()
        gap = outcomes_agent.next_gap()

        # Show updated outcomes tracker
        print_outcomes(outcomes_agent.outcomes, coverage, score)

        # Agent 1: respond, steered toward the current gap
        prompt = build_student_prompt(user, gap, coverage)
        print("Cozy: ", end="", flush=True)
        for chunk in student.respond_stream(prompt):
            print(chunk, end="", flush=True)
        print("\n")

        # Actor 3 Verifier: check student's truthfulness after each response
        verification = verifier.verify_conversation(student.history)
        print_verification(verification)


if __name__ == "__main__":
    main()