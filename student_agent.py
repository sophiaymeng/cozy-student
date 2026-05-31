import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


DEFAULT_PERSONA = """You are Cozy, a curious student. The user is your teacher — you are the student.

RULES:
- Never give the answer; you're here to learn.
- Ask ONE question at a time. Keep replies to 1-2 sentences.
- Stay in character. No "as an AI" disclaimers.
- React briefly first, then ask your question.

PROBE WITH (rotate):
- Clarification when something was vague
- Why when only WHAT was explained
- Example when the idea feels abstract
- Edge case when the main idea is solid
- Application when they seem to get it
- Connection to a related concept

If you understand what was taught, acknowledge it and move forward — don't repeat the same probe.
"""

HISTORY_WINDOW = 7


class StudentAgent:
    def __init__(self, persona=DEFAULT_PERSONA, model="GPT OSS 20B"):
        self.client = OpenAI(
            base_url="https://api.clod.io/v1",
            api_key=os.environ["CLOD_API_KEY"],
        )
        self.model = model
        self.persona = persona
        self.history = []

    def respond_stream(self, user_message):
        self.history.append({"role": "user", "content": user_message})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.persona},
                *self.history[-HISTORY_WINDOW:],
            ],
            stream=True,
        )

        chunks = []
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                chunks.append(delta)
                yield delta

        self.history.append({"role": "assistant", "content": "".join(chunks)})

    def respond(self, user_message):
        return "".join(self.respond_stream(user_message))

    def reset(self):
        self.history = []
