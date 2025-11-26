from dataclasses import dataclass
from typing import Any

@dataclass 
class ExtractionResult:
    raw_response: str
    structured_data: dict | None
    tokens_used: int