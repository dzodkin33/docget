from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid


@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_message(self, message):
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_messages(self):
        return self.messages

    def get_message_count(self) -> int:
        return len(self.messages)

    def to_dict(self):
        return {
            'id': self.id,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict):
        from .message import Message
        return cls(
            id=data['id'],
            messages=[Message.from_dict(msg) for msg in data.get('messages', [])],
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        )

    def clear_messages(self):
        self.messages = []
        self.updated_at = datetime.now()
