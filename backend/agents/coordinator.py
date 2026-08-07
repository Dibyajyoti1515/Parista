"""Coordinator Agent for the Parista backend.

Root orchestrator. Receives the incoming user message, runs the Safety
Agent first, then routes sequentially through Classifier → Retrieval →
Reasoning → Style, and returns the final structured response.

Note: Reasoning, Citation Verification, and Style agents are implemented
in later phases (US1 tasks T019-T021, T020). Until then, the coordinator
runs the Safety Agent, Classifier Agent, and Retrieval Agent, and returns
a structured response reflecting the retrieval outcome. If the core KB has
no confident match, the response is marked as needing the Semantic Scholar
fallback (US4, T039) rather than proceeding ungrounded.
"""

from backend.agents.base import BaseAgent
from backend.agents.classifier_agent import ClassifierAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.safety_agent import SafetyAgent


class CoordinatorAgent(BaseAgent):
    """Coordinates the Parista agent pipeline for each user turn."""

    def __init__(self) -> None:
        super().__init__(
            name="coordinator",
            instruction=(
                "You are the Coordinator Agent for Parista. You orchestrate the "
                "pipeline: Safety Agent first (crisis override), then Classifier, "
                "Retrieval, Reasoning, Citation Verification, and Style. You "
                "return the final structured response to the user."
            ),
        )
        self.safety_agent = SafetyAgent()
        self.classifier_agent = ClassifierAgent()
        self.retrieval_agent = RetrievalAgent()
        # Remaining agents are wired in later phases (US1: T019-T021, T020).
        self.reasoning_agent = None
        self.citation_verify_tool = None
        self.style_agent = None

    def process(self, text: str, conversation_context: dict | None = None) -> dict:
        """Process a user turn through the agent pipeline.

        Safety Agent runs first on every turn. If a crisis signal is
        detected, the pipeline short-circuits immediately and returns the
        supportive response — no other agent runs.

        The Classifier Agent tags the situation, then the Retrieval Agent
        queries the core KB using those tags. If the top match is below the
        confidence threshold, the response is marked as needing the Semantic
        Scholar fallback (US4, not yet implemented) rather than proceeding
        ungrounded.
        """
        # Step 1: Safety Agent (hard override, always first).
        safety_result = self.safety_agent.check(text)
        if safety_result["crisis_override"]:
            self.log("crisis_override_triggered")
            return safety_result

        # Step 2: Classifier Agent.
        classification = self.classifier_agent.classify(text)

        # Step 3: Retrieval Agent (conditioned on the classifier's tags).
        retrieved_chunks = self.retrieval_agent.retrieve(text, classification)
        top = self.retrieval_agent.top_match(text, classification)

        if top is None:
            # Below confidence threshold — do NOT proceed ungrounded. The
            # real-time Semantic Scholar fallback (US4, T039) is not yet
            # implemented, so mark the response as needing it.
            self.log(
                "fallback_needed",
                classification=classification,
                retrieved_count=len(retrieved_chunks),
            )
            return {
                "conversation_id": (
                    conversation_context.get("conversation_id") if conversation_context else None
                ),
                "classification": classification,
                "analysis": None,
                "suggested_reply": None,
                "supplementary": False,
                "fallback_needed": True,
                "message": (
                    "No confident match found in the core knowledge base. "
                    "Semantic Scholar fallback not yet implemented (US4)."
                ),
            }

        # Core KB match found (>= 0.75). Reasoning, Citation Verification,
        # and Style (T019-T021, T020) are implemented in later phases.
        response = {
            "conversation_id": (
                conversation_context.get("conversation_id") if conversation_context else None
            ),
            "classification": classification,
            "retrieved_source": top.to_dict(),
            "analysis": None,
            "suggested_reply": None,
            "supplementary": False,
            "fallback_needed": False,
            "message": "Retrieval complete; Reasoning/Style pipeline pending.",
        }
        self.log("pipeline_partial", classification=classification, top_similarity=top.similarity)
        return response