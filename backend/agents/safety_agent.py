"""Safety Agent for the Parista backend.

Runs on every single turn, before any other agent. Screens for crisis
signals (self-harm, suicidal ideation, abuse indicators). If triggered,
short-circuits the pipeline and returns supportive language plus
resources instead of relationship advice. This is a hard override — no
other agent runs after a crisis flag.
"""

from backend.agents.base import BaseAgent

# Deterministic keyword screen — always runs, never skipped.
CRISIS_SIGNALS = (
    "kill myself",
    "suicide",
    "suicidal",
    "self-harm",
    "self harm",
    "hurt myself",
    "end my life",
    "want to die",
    "don't want to live",
    "better off dead",
    "being abused",
    "abusive",
    "hit me",
    "hurting me",
    "sexual abuse",
    "domestic violence",
)

SUPPORTIVE_RESPONSE = {
    "crisis_override": True,
    "message": (
        "I'm really sorry you're going through this. Your safety matters most, "
        "and I'm not the right resource for this right now. Please reach out to "
        "someone who can help immediately:\n\n"
        "- National Suicide Prevention Lifeline (US): call or text 988\n"
        "- Crisis Text Line: text HOME to 741741\n"
        "- Or contact your local emergency services (e.g., 911 / 112)\n\n"
        "You deserve support, and there are people who care about you."
    ),
}


class SafetyAgent(BaseAgent):
    """Screens every input for crisis signals before any other agent runs."""

    def __init__(self) -> None:
        super().__init__(
            name="safety_agent",
            instruction=(
                "You are the Safety Agent for Parista. Your ONLY job is to screen "
                "incoming user messages for crisis signals: self-harm, suicidal "
                "ideation, or abuse. If you detect a crisis signal, you MUST "
                "short-circuit the pipeline and return supportive language plus "
                "appropriate resources. You must NEVER provide relationship advice "
                "when a crisis signal is present."
            ),
        )

    def check(self, text: str) -> dict:
        """Screen the input text for crisis signals.

        Returns ``{"crisis_override": True, "message": ...}`` when a crisis
        signal is detected, otherwise ``{"crisis_override": False}``.
        """
        lowered = text.lower()
        for signal in CRISIS_SIGNALS:
            if signal in lowered:
                self.log("crisis_signal_detected", signal=signal)
                return dict(SUPPORTIVE_RESPONSE)
        self.log("safety_check_passed")
        return {"crisis_override": False}