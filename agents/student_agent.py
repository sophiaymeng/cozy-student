from __future__ import annotations

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class StudentAgent:

    def __init__(self, model="GPT OSS 20B"):
        self.client = OpenAI(
            base_url="https://api.clod.io/v1",
            api_key=os.environ["CLOD_API_KEY"],
        )
        self.model = model
        self.topic = ""
        self.history = []

    def set_topic(self, topic: str):
        self.topic = topic

    def respond(self, user_input, correctness, next_gap):

        system_prompt = f"""
You are Cozy, a curious student.

You are learning:
{self.topic}

Rules:
- Never teach.
- Never give definitions.
- Ask questions.
- Be conversational.
- Maximum 3 sentences.
"""

        user_prompt = f'The teacher said:\n"{user_input}"\n'

        verdict = correctness.get("verdict")

        if verdict == "incorrect":
            user_prompt += """
Their explanation may contain an error.

Do NOT correct them.

Ask a question that probes the questionable area.
"""
        elif verdict == "partial":
            user_prompt += """
React positively.

Ask about what is still missing.
"""
        else:
            user_prompt += """
React as if you understood.
Go deeper.
"""

        if next_gap:
            user_prompt += f'\nSteer naturally toward: "{next_gap}"'

        if not next_gap:
            user_prompt += """
Everything seems covered.
Ask one final deep why/what-if question.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                *self.history[-6:],
                {"role": "user", "content": user_prompt},
            ],
        )

        text = response.choices[0].message.content.strip()

        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": text})

        return text

    def reset(self):
        self.history = []
        self.topic = ""
