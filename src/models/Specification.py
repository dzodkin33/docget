from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Specification(BaseModel):
    """Represents extracted specification data from a document."""
    document_name: str
    page_number: int
    raw_text: str
    tables: List[List[List[str]]] = Field(default_factory=list)
    extracted_values: Dict[str, str] = Field(default_factory=dict)
    component_mentions: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "document_name": "motor_datasheet.pdf",
                "page_number": 1,
                "raw_text": "Brushless Motor 2300KV...",
                "tables": [[["Voltage", "Current"], ["11.1V", "25A"]]],
                "extracted_values": {
                    "kv_rating": "2300KV",
                    "max_current": "25A"
                },
                "component_mentions": ["motor", "brushless"]
            }
        }
