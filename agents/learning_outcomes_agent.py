from __future__ import annotations

import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = "You are a precise educational evaluator. Return only valid JSON."


def _extract_json(text: str):
    text = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"[\[{][\s\S]*[\]}]", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return None


class LearningOutcomesAgent:
    def __init__(self, model="GPT OSS 120B"):
        self.client = OpenAI(
            base_url="https://api.clod.io/v1",
            api_key=os.environ["CLOD_API_KEY"],
        )
        self.model = model
        self.topic = None
        self.outcomes = []
        self.coverage = {"covered": [], "partial": [], "missing": []}

    def generate_outcomes(self, topic: str):
        self.topic = topic

        prompt = f"""Generate 5-7 specific, testable learning outcomes for:
"{topic}"

Return ONLY a JSON array of short strings."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        parsed = _extract_json(response.choices[0].message.content)

        self.outcomes = parsed if isinstance(parsed, list) else []
        self.coverage["missing"] = list(self.outcomes)
        return self.outcomes

    def evaluate_coverage(self, full_explanation: str):
        if not self.outcomes:
            return self.coverage

        prompt = f"""Topic: "{self.topic}"

Learning outcomes:
{chr(10).join(f"- {o}" for o in self.outcomes)}

Student explanation:
"{full_explanation}"

Return ONLY:

{{"covered":[],"partial":[],"missing":[]}}

Use exact outcome strings.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        parsed = _extract_json(response.choices[0].message.content)

        if isinstance(parsed, dict):
            self.coverage = {
                "covered": parsed.get("covered", []),
                "partial": parsed.get("partial", []),
                "missing": parsed.get("missing", []),
            }

        return self.coverage

    def mastery_score(self):
        total = len(self.outcomes)
        if total == 0:
            return 0

        covered = len(self.coverage["covered"])
        partial = len(self.coverage["partial"])

        return round(((covered + partial * 0.5) / total) * 100)

    def next_gap(self):
        return (self.coverage["missing"] or self.coverage["partial"] or [None])[0]

    def reset(self):
        self.topic = None
        self.outcomes = []
        self.coverage = {"covered": [], "partial": [], "missing": []}
