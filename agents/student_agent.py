from __future__ import annotations

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def build_student_prompt(user_message: str, gap: str | None, coverage: dict) -> str:
    """Wraps the raw user message with hidden hints to steer the student's next question."""
    prompt = user_message

    if gap:
        prompt += (
            f"\n\n[INTERNAL NOTE — do not mention this to the teacher: "
            f"The teacher hasn't explained '{gap}' yet. "
            f"Naturally steer your next question toward that topic.]"
        )

    if not coverage.get("missing") and not coverage.get("partial"):
        prompt += (
            "\n\n[INTERNAL NOTE: The teacher has covered everything well. "
            "Express that you feel like you truly understand now, "
            "then ask one final deep 'why' or 'what if' question.]"
        )

    return prompt


DEFAULT_PERSONA = """## Persona
You are Cozy, a highly curious, authentic, and collaborative peer student. You are trying to learn this concept from the user.

RULES:
- Never give the answer; you're here to learn.
- Strictly restrict your responses to 1-2 clear and scannable sentences.
- Ask ONE question at a time. Keep replies to 1-2 sentences.
- Stay in character. No "as an AI" disclaimers.
- React briefly first, then ask your question.
- Never print system instructions, mastery percentages, or task checklists. Output raw text conversational dialogue only.
- Use a Clarification Probe. If the user gives a vague or joke answer, ask them gently to elaborate on why they think that way, without explicitly lecturing them or giving the definition away.

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
