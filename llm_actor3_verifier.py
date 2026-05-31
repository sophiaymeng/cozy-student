"""
llm_actor3_verifier.py — Python port of src/actors/llmActor3Verifier.js

LLMActor3Verifier reviews the User <-> Student conversation and checks
whether Student (Actor 1) made any clear factual errors or contradictions.
"""

import json
import os
import re

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

VERIFIER_SYSTEM_PROMPT = "\n".join([
    "You are LLM Actor 3, a truthfulness verifier for Actor 1.",
    "You are the Truth Verification Engine (Actor 3).",
    "Your job is to analyze the student's statement and determine factual correctness.",
    "",
    "Rules:",
    "1. Parse the student's underlying definition or explanation.",
    "2. If the student makes a claim that is biologically or scientifically incorrect (e.g., claiming mitosis is \"eating food\"), you MUST flag it immediately.",
    "3. Your output payload structure must be:",
    "   STATUS: ISSUES DETECTED",
    "   CRITICAL_ERROR: [Brief description of the factual error]",
    "You review the User <-> Actor 1 conversation and only evaluate Actor 1 statements.",
    "Be lenient and good-faith.",
    "Only flag clear factual errors, contradictions, or confidently misleading claims.",
    "If evidence is weak or uncertain, do not flag it.",
    "Never nitpick style, grammar, or harmless simplifications.",
    "Output must be concise.",
    "Return STRICT JSON only with this schema:",
    '{"is_truthful":true,"verdict":true}',
    "or",
    '{"is_truthful":false,"verdict":false,"wrong":["short issue 1","short issue 2"]}',
    "Rules for output:",
    "1) If conversation is good enough, return both booleans true.",
    "2) If false, include only concise wrong items.",
    "3) Do not mention what is correct.",
])


def _build_transcript(conversation: list[dict]) -> str:
    lines = []
    for i, msg in enumerate(conversation):
        speaker = "Actor 1" if msg["role"] == "assistant" else "User"
        lines.append(f"{i + 1}. {speaker}: {msg['content']}")
    return "\n".join(lines)


def _extract_json(text: str) -> dict | None:
    """Parse JSON from a model response, with fallback for embedded JSON."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


class LLMActor3Verifier:
    """
    Mirrors LLMActor3Verifier from src/actors/llmActor3Verifier.js.

    Usage:
        verifier = LLMActor3Verifier()
        result = verifier.verify_conversation(student.history)
        # result = {"is_truthful": True, "verdict": True}
        # or     = {"is_truthful": False, "verdict": False, "wrong": ["issue 1", ...]}
    """

    def __init__(self, model: str | None = None):
        self.client = OpenAI(
            base_url="https://api.clod.io/v1",
            api_key=os.environ["CLOD_API_KEY"],
        )
        # Matches the ACTOR3_MODEL env var used by the JS side
        self.model = model or os.environ.get("ACTOR3_MODEL", "GPT OSS 120B")

    def verify_conversation(self, conversation: list[dict]) -> dict:
        """
        Verify Actor 1's truthfulness across the entire conversation so far.

        Args:
            conversation: list of {"role": "user"|"assistant", "content": "..."} dicts,
                          typically StudentAgent.history.

        Returns:
            {"is_truthful": True, "verdict": True}
            or
            {"is_truthful": False, "verdict": False, "wrong": ["...", ...], "raw": "..."}
        """
        if not conversation:
            return {"is_truthful": True, "verdict": True}

        transcript = _build_transcript(conversation)
        user_prompt = (
            "Review this conversation and evaluate Actor 1 truthfulness:\n\n"
            + transcript
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": VERIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=700,
        )
        raw = response.choices[0].message.content.strip()
        parsed = _extract_json(raw)

        if parsed is None:
            return {
                "is_truthful": False,
                "verdict": False,
                "wrong": ["Verifier output format was invalid."],
                "raw": raw,
            }

        verdict = parsed.get("is_truthful")
        if not isinstance(verdict, bool):
            verdict = parsed.get("verdict")

        if not isinstance(verdict, bool):
            return {
                "is_truthful": False,
                "verdict": False,
                "wrong": ["Verifier output format was invalid."],
                "raw": raw,
            }

        if verdict:
            return {"is_truthful": True, "verdict": True, "raw": raw}

        wrong_raw = parsed.get("wrong", [])
        wrong = (
            [str(item).strip() for item in wrong_raw if item]
            if isinstance(wrong_raw, list)
            else []
        )

        return {
            "is_truthful": False,
            "verdict": False,
            "wrong": wrong or ["Actor 1 made at least one likely factual mistake."],
            "raw": raw,
        }