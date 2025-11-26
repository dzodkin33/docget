from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    """Base class for all agents. Allows pluggable agent implementations."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request and return a structured response.

        Args:
            request: Structured request dictionary containing the task

        Returns:
            Structured response dictionary with the agent's result
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the agent is properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    def get_name(self) -> str:
        return self.name
