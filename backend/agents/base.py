"""Base ADK agent framework for the Parista backend.

Provides a shared base class that wraps Google ADK agents with common
configuration: model routing (Gemini for quality-sensitive steps, a
lighter model for routine rephrasing) and structured logging.
"""

from typing import Any

from google.adk.agents import Agent

from backend.config import settings
from backend.modules.chat.logging import get_logger

# Model routing per the constitution: Gemini for quality-sensitive steps,
# a lighter/faster model for routine rephrasing.
QUALITY_MODEL = "gemini-2.0-flash"
LIGHT_MODEL = "gemini-2.0-flash-lite"


class BaseAgent:
    """Base class for all Parista ADK agents."""

    def __init__(
        self,
        name: str,
        instruction: str,
        model: str | None = None,
        tools: list[Any] | None = None,
    ) -> None:
        self.name = name
        self.logger = get_logger(f"agent.{name}")
        self.model = model or QUALITY_MODEL
        self.instruction = instruction
        self.tools = tools or []
        self._agent = Agent(
            name=name,
            model=self.model,
            instruction=instruction,
            tools=self.tools,
        )

    @property
    def agent(self) -> Agent:
        """Return the underlying ADK Agent instance."""
        return self._agent

    def log(self, event: str, **kwargs: Any) -> None:
        """Emit a structured log entry for this agent."""
        self.logger.info(event, agent=self.name, **kwargs)


def require_api_key() -> None:
    """Raise if the Gemini API key is not configured."""
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY must be configured in the environment "
            "(see backend/.env.example)"
        )