"""Reasoning Agent for the Parista backend.

Takes the retrieved framework/chunk plus the user's situation and produces
a structured psychological analysis: pattern identified, explanation, and
source citation. Constrained by the constitution to only make claims
traceable to the retrieved content — the source citation is taken directly
from the retrieved chunk, never invented by the model.
"""

import json
import re

from backend.agents.base import BaseAgent, QUALITY_MODEL
from backend.modules.chat.logging import get_logger
from backend.modules.llm import generate_text
from backend.tools.vector_search_tool import VectorSearchResult

logger = get_logger("reasoning")


class ReasoningAgent(BaseAgent):
    """Produces a grounded psychological analysis from a retrieved chunk."""

    def __init__(self) -> None:
        super().__init__(
            name="reasoning_agent",
            instruction=(
                "You are the Reasoning Agent for Parista. Given the user's "
                "situation and a retrieved psychological framework chunk, "
                "produce a structured psychological analysis: the pattern "
                "identified, the explanation, and the source citation. You MUST "
                "only make claims that are directly supported by the retrieved "
                "chunk content — never add claims from general knowledge."
            ),
            model=QUALITY_MODEL,
        )

    def reason(self, text: str, chunk: VectorSearchResult) -> dict:
        """Build a structured analysis grounded in the retrieved chunk.

        The ``source`` is populated directly from the retrieved chunk's
        ``source_title`` and ``framework_name`` — never from the model — so
        the citation is always traceable to a real retrieved source.
        """
        prompt = (
            f"User's situation: {text}\n\n"
            f"Retrieved framework chunk:\n"
            f"- Source: {chunk.source_title}\n"
            f"- Framework: {chunk.framework_name or 'N/A'}\n"
            f"- Content: {chunk.content}\n\n"
            "Based ONLY on the retrieved chunk above, identify the psychological "
            "pattern and explain how it applies to the user's situation. Return "
            'JSON with keys: "pattern" (short name) and "explanation" '
            "(2-4 sentences grounded in the chunk content). Do not include any "
            "claims not supported by the chunk."
        )
        raw = generate_text(prompt, model_name=QUALITY_MODEL)
        parsed = self._parse_response(raw)

        analysis = {
            "psychological_pattern": {
                "pattern": parsed.get("pattern") or (chunk.framework_name or "psychological pattern"),
                "explanation": parsed.get("explanation") or chunk.content,
                "source": {
                    "source_title": chunk.source_title,
                    "framework_name": chunk.framework_name,
                },
            }
        }
        self.log("reasoned", source_title=chunk.source_title)
        return analysis

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