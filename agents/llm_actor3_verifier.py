from __future__ import annotations

import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def _extract_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return None


class LLMActor3Verifier:
    def __init__(self, model="GPT OSS 120B"):
        self.client = OpenAI(
            base_url="https://api.clod.io/v1",
            api_key=os.environ["CLOD_API_KEY"],
        )
        self.model = model

    def evaluate(self, topic: str, user_input: str, history: list[dict]):
        transcript = "\n".join(
            f"{m['role']}: {m['content']}"
            for m in history[-6:]
        )

        prompt = f"""Topic: "{topic}"

Student said:
"{user_input}"

Conversation:
{transcript}

Return ONLY:

{{
"verdict":"correct|partial|incorrect",
"score":0-100,
"feedback":"short feedback"
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": "Evaluate accuracy. Return only JSON."},
                {"role": "user", "content": prompt},
            ],
        )

        parsed = _extract_json(response.choices[0].message.content)

        if not isinstance(parsed, dict):
            return {
                "verdict": "partial",
                "score": 50,
                "feedback": "Could not evaluate."
            }

        return parsed
