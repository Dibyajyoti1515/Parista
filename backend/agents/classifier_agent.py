"""Classifier Agent for the Parista backend.

Tags the incoming situation: domain (romantic / family / workplace),
conflict type, emotional tone, and age bracket where inferable. Produces
no advice itself — output is structured tags consumed by the Retrieval
Agent to condition search.
"""

from backend.agents.base import BaseAgent

# Deterministic domain keywords (used as a fast pre-screen; the LLM
# classifier refines these on the full text).
DOMAIN_KEYWORDS = {
    "romantic": ("boyfriend", "girlfriend", "partner", "husband", "wife", "spouse", "dating", "ex", "breakup", "break up", "marriage"),
    "family": ("mom", "dad", "mother", "father", "parent", "sister", "brother", "family", "in-law", "in laws", "daughter", "son"),
    "workplace": ("boss", "manager", "coworker", "colleague", "work", "office", "hr", "job", "team lead", "supervisor", "client"),
}

CONFLICT_TYPES = ("communication", "trust", "boundaries", "expectations", "values", "power", "other")

TONE_OPTIONS = ("upset", "anxious", "angry", "confused", "hurt", "neutral", "other")


class ClassifierAgent(BaseAgent):
    """Classifies the domain, conflict type, and emotional tone of a situation."""

    def __init__(self) -> None:
        super().__init__(
            name="classifier_agent",
            instruction=(
                "You are the Classifier Agent for Parista. Given a user's "
                "description of an interpersonal conflict, classify it into a "
                "structured set of tags: domain (romantic/family/workplace/"
                "general), conflict type, emotional tone, and age bracket where "
                "inferable. Output ONLY structured tags — never produce advice "
                "or a reply."
            ),
        )

    def classify(self, text: str) -> dict:
        """Classify the situation into structured tags.

        Returns a dict with ``domain``, ``conflict_type``, ``emotional_tone``,
        and ``age_bracket`` (if inferable).
        """
        lowered = text.lower()

        # Domain detection — highest-scoring keyword group wins.
        scores = {domain: 0 for domain in DOMAIN_KEYWORDS}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lowered:
                    scores[domain] += 1

        domain = max(scores, key=scores.get) if max(scores.values()) > 0 else "general"

        # Conflict type and tone are refined by the LLM in later steps; here we
        # provide a deterministic default that the Reasoning step can override.
        classification = {
            "domain": domain,
            "conflict_type": "other",
            "emotional_tone": "neutral",
            "age_bracket": None,
        }
        self.log("classified", **classification)
        return classification