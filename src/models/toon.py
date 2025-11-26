from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class TOONRequest:
    """
    TOON Request Structure:
    - Task: What needs to be done
    - Objective: Why it needs to be done / expected outcome
    - Output: Expected output format
    - Notes: Additional context or constraints
    """
    task: str
    objective: str
    output_format: str = "text"
    notes: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'task': self.task,
            'objective': self.objective,
            'output_format': self.output_format,
            'notes': self.notes,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }

    def to_prompt(self) -> str:
        """Convert TOON request to a formatted prompt."""
        prompt = f"Task: {self.task}\n\n"
        prompt += f"Objective: {self.objective}\n\n"
        prompt += f"Expected Output Format: {self.output_format}\n"

        if self.notes:
            prompt += f"\nAdditional Notes: {self.notes}\n"

        if self.context:
            prompt += f"\nContext:\n"
            for key, value in self.context.items():
                prompt += f"  - {key}: {value}\n"

        return prompt

    @classmethod
    def from_user_input(cls, user_input: str, context: Optional[Dict[str, Any]] = None):
        """Create a TOON request from raw user input."""
        return cls(
            task=user_input,
            objective="Understand and respond to user request",
            output_format="conversational text",
            notes="User query from CLI",
            context=context or {}
        )


@dataclass
class TOONResponse:
    """
    TOON Response Structure:
    Structured response from an agent
    """
    success: bool
    result: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'result': self.result,
            'metadata': self.metadata,
            'error': self.error,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def success_response(cls, result: str, metadata: Optional[Dict[str, Any]] = None):
        """Create a successful response."""
        return cls(
            success=True,
            result=result,
            metadata=metadata or {}
        )

    @classmethod
    def error_response(cls, error: str, metadata: Optional[Dict[str, Any]] = None):
        """Create an error response."""
        return cls(
            success=False,
            result="",
            error=error,
            metadata=metadata or {}
        )
