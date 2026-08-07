"""Style Agent for the Parista backend.

Rewrites the Reasoning Agent's verified output into a natural, age-calibrated
reply, drawing on cached tone examples in the ``style_examples`` table. Only
adjusts phrasing/tone — must not alter the underlying psychological substance
(enforced by the constitution's Cultural Calibration principle).
"""

import json
import re

from backend.agents.base import BaseAgent, LIGHT_MODEL
from backend.modules.chat.logging import get_logger
from backend.modules.llm import generate_text

logger = get_logger("style")


class StyleAgent(BaseAgent):
    """Rewrites a verified analysis into a tone-calibrated reply."""

    def __init__(self) -> None:
        super().__init__(
            name="style_agent",
            instruction=(
                "You are the Style Agent for Parista. Given a verified "
                "psychological analysis, rewrite it into a natural, "
                "age-calibrated reply. You may adjust tone (formal/casual, "
                "Hinglish/English) based on context signals the user provides, "
                "but you MUST NOT alter the underlying psychological substance, "
                "the identified pattern, or the source citation."
            ),
            model=LIGHT_MODEL,
        )

    def style(self, analysis: dict, tone: str = "casual") -> dict:
        """Produce a tone-calibrated suggested reply for the user.

        The psychological substance (pattern, explanation, source) is passed
        through as-is; only the suggested reply text is rewritten for tone.
        """
        pattern = analysis.get("psychological_pattern", {})
        prompt = (
            f"Verify-preserved analysis:\n"
            f"- Pattern: {pattern.get('pattern', '')}\n"
            f"- Explanation: {pattern.get('explanation', '')}\n\n"
            f"Rewrite this into a natural suggested reply the user can send in "
            f"their real conversation. Tone: {tone}. Keep the reply concise "
            "(2-4 sentences) and relatable. Return JSON with key "
            '"text" (the suggested reply). Do not mention the source or '
            "framework in the reply itself."
        )
        raw = generate_text(prompt, model_name=LIGHT_MODEL)
        parsed = self._parse_response(raw)

        suggested_reply = {"text": parsed.get("text", "") or pattern.get("explanation", ""), "tone": tone}
        self.log("styled", tone=tone)
        return suggested_reply

    @staticmethod
    def _parse_response(raw: str) -> dict:
        """Extract JSON from the model response, with fallbacks."""
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
        return {}