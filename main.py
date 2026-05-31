from student_agent import StudentAgent


BANNER = """
Cozy Student — teach the AI, discover your knowledge gaps.
Type your explanation and press Enter. Type 'exit' to quit, 'reset' to start over.
"""


def main():
    agent = StudentAgent()
    print(BANNER)

    topic = input("What are you teaching today? > ").strip()
    if topic:
        print("\nCozy: ", end="", flush=True)
        for chunk in agent.respond_stream(
            f"I want to learn about: {topic}. Could you start by telling me what it is?"
        ):
            print(chunk, end="", flush=True)
        print("\n")

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
            agent.reset()
            print("[conversation reset]\n")
            continue

        print("\nCozy: ", end="", flush=True)
        for chunk in agent.respond_stream(user):
            print(chunk, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    main()
