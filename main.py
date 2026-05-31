from dotenv import load_dotenv

from agents.learning_outcomes_agent import LearningOutcomesAgent
from agents.llm_actor3_verifier import LLMActor3Verifier
from agents.student_agent import StudentAgent

load_dotenv()


def print_outcomes(outcomes, coverage, score):

    print(f"\nMastery: {score}%\n")

    for outcome in outcomes:

        if outcome in coverage["covered"]:
            icon = "✓"
        elif outcome in coverage["partial"]:
            icon = "~"
        else:
            icon = "○"

        print(f"{icon} {outcome}")

    print()


def main():

    topic = input("What are you teaching today? > ").strip()

    coverage_agent = LearningOutcomesAgent()
    correctness_agent = LLMActor3Verifier()
    student = StudentAgent()

    student.set_topic(topic)

    outcomes = coverage_agent.generate_outcomes(topic)

    all_user_text = []

    print_outcomes(
        outcomes,
        coverage_agent.coverage,
        coverage_agent.mastery_score()
    )

    greeting = f"I want to learn about {topic}. Could you explain what it is?"
    print(f"\nCozy: {greeting}\n")

    while True:

        user = input("You > ").strip()

        if user.lower() in {"exit", "quit"}:
            break

        all_user_text.append(user)

        coverage = coverage_agent.evaluate_coverage(
            " ".join(all_user_text)
        )

        correctness = correctness_agent.evaluate(
            topic,
            user,
            student.history
        )

        score = coverage_agent.mastery_score()
        gap = coverage_agent.next_gap()

        print_outcomes(outcomes, coverage, score)

        print(
            f"[{correctness['verdict'].upper()}] "
            f"{correctness['score']}/100"
        )
        print(correctness["feedback"])
        print()

        reply = student.respond(
            user,
            correctness,
            gap
        )

        print(f"Cozy: {reply}\n")


if __name__ == "__main__":
    main()
