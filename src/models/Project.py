from pydantic import BaseModel, Field
from typing import List, Dict
from .Component import Component

class Project(BaseModel):
    """Represents a complete hardware project with all components."""
    name: str
    components: List[Component] = Field(default_factory=list)
    total_power_budget: Dict[str, float] = Field(default_factory=dict)
    compatibility_issues: List[str] = Field(default_factory=list)
    missing_components: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Quadcopter Drone",
                "components": [],
                "total_power_budget": {
                    "total_current_a": 45.2,
                    "estimated_power_w": 542.4
                },
                "compatibility_issues": [
                    "ESC max current (30A) may be insufficient for motor peak draw (40A)"
                ],
                "missing_components": [],
                "warnings": [],
                "recommendations": []
            }
        }

    def add_component(self, component: Component):
        """Add a component to the project."""
        self.components.append(component)

    def get_components_by_type(self, component_type: str) -> List[Component]:
        """Get all components of a specific type."""
        return [c for c in self.components if c.component_type == component_type]

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return self.model_dump()
