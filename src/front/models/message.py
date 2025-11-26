from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime = field(default_factory=datetime.now)
    conversation_id: Optional[str] = None

    def to_dict(self):
        return {
            'content': self.content,
            'role': self.role,
            'timestamp': self.timestamp.isoformat(),
            'conversation_id': self.conversation_id
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            content=data['content'],
            role=data['role'],
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            conversation_id=data.get('conversation_id')
        )

    def is_user_message(self) -> bool:
        return self.role == 'user'

    def is_assistant_message(self) -> bool:
        return self.role == 'assistant'
