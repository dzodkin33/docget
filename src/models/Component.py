from pydantic import BaseModel, Field
from typing import Optional, Dict

class PowerSpec(BaseModel):
    """Power-related specifications for a component."""
    voltage_input: Optional[str] = None
    voltage_output: Optional[str] = None
    current_rating: Optional[str] = None
    power_consumption: Optional[str] = None
    capacity: Optional[str] = None  # For batteries (mAh)

    class Config:
        json_schema_extra = {
            "example": {
                "voltage_input": "5V",
                "voltage_output": "3.3V",
                "current_rating": "2A",
                "power_consumption": "10W",
                "capacity": "2200mAh"
            }
        }

class InterfaceSpec(BaseModel):
    """Communication interface specifications."""
    uart_count: int = 0
    i2c_count: int = 0
    spi_count: int = 0
    can_count: int = 0
    usb_count: int = 0
    gpio_count: int = 0
    pwm_count: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "uart_count": 3,
                "i2c_count": 2,
                "spi_count": 1,
                "can_count": 0,
                "usb_count": 1,
                "gpio_count": 20,
                "pwm_count": 6
            }
        }

class Component(BaseModel):
    """Represents a hardware component extracted from specifications."""
    name: str
    component_type: str  # motor, sensor, processor, camera, battery, esc, radio, etc.
    manufacturer: Optional[str] = None
    part_number: Optional[str] = None
    power: PowerSpec = Field(default_factory=PowerSpec)
    interfaces: InterfaceSpec = Field(default_factory=InterfaceSpec)
    specific_specs: Dict[str, str] = Field(default_factory=dict)
    source_document: str
    page_number: Optional[int] = None
    confidence: Optional[float] = None  # AI extraction confidence score

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Pixhawk 4",
                "component_type": "processor",
                "manufacturer": "Holybro",
                "part_number": "PH4-001",
                "power": {
                    "voltage_input": "5V",
                    "current_rating": "500mA"
                },
                "interfaces": {
                    "uart_count": 6,
                    "i2c_count": 3,
                    "spi_count": 2
                },
                "specific_specs": {
                    "processor": "STM32F765",
                    "ram": "512KB",
                    "flash": "2MB"
                },
                "source_document": "pixhawk4_datasheet.pdf",
                "page_number": 3
            }
        }

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return self.model_dump()
