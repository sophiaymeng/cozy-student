from __future__ import annotations

import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OUTCOMES_SYSTEM_PROMPT = """You are a precise educational evaluator. You only respond with valid JSON. Never add explanation or markdown."""


def _extract_json(text: str):
    """Parse JSON from a model response, with regex fallback for embedded JSON."""
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"[\[{][\s\S]*[\]}]", cleaned)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
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

    # ── Called once at session start ──────────────────────────────────────
    def generate_outcomes(self, topic: str) -> list[str]:
        self.topic = topic
        prompt = f"""Generate 5-7 specific, testable learning outcomes for: "{topic}"

Return ONLY a JSON array of short strings (max 8 words each).
Example: ["Explain what X is", "Describe how Y works", "Distinguish A from B"]"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": OUTCOMES_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        raw = response.choices[0].message.content
        parsed = _extract_json(raw)
        if not isinstance(parsed, list):
            self.outcomes = []
            self.coverage["missing"] = []
            return self.outcomes
        self.outcomes = [str(o) for o in parsed if o]
        self.coverage["missing"] = list(self.outcomes)
        return self.outcomes

    # ── Called after every user message ──────────────────────────────────
    def evaluate_coverage(self, full_explanation: str) -> dict:
        if not self.outcomes:
            return self.coverage

        prompt = f"""Topic: "{self.topic}"

Learning outcomes:
{chr(10).join(f"{i+1}. {o}" for i, o in enumerate(self.outcomes))}

Everything the student has explained so far:
"{full_explanation}"

For each outcome, decide: covered, partial, or missing.
Return ONLY this JSON (use exact outcome strings from the list):
{{"covered": [...], "partial": [...], "missing": [...]}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": OUTCOMES_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        raw = response.choices[0].message.content
        parsed = _extract_json(raw)
        if not isinstance(parsed, dict):
            return self.coverage
        self.coverage = {
            "covered": list(parsed.get("covered", [])),
            "partial": list(parsed.get("partial", [])),
            "missing": list(parsed.get("missing", [])),
        }
        return self.coverage

    # ── Helpers ───────────────────────────────────────────────────────────
    def next_gap(self) -> str | None:
        """Returns the highest-priority uncovered outcome, or None if all done."""
        return (self.coverage.get("missing") or self.coverage.get("partial") or [None])[0]

    def mastery_score(self) -> int:
        total = len(self.outcomes)
        if not total:
            return 0
        covered = len(self.coverage.get("covered", []))
        partial = len(self.coverage.get("partial", []))
        return round(((covered + partial * 0.5) / total) * 100)

    def reset(self):
        self.topic = None
        self.outcomes = []
        self.coverage = {"covered": [], "partial": [], "missing": []}