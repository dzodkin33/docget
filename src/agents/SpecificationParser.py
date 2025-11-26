import re
from typing import Dict, List, Optional, Tuple
import logging
import sys
sys.path.append('/Users/anujjain/drone-component-analyzer')
from src.models.Component import PowerSpec, InterfaceSpec

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpecificationParser:
    """Parse component specifications from extracted text using regex patterns."""

    # Regex patterns for common specifications
    PATTERNS = {
        'voltage': r'(\d+\.?\d*)\s*V(?:DC|AC)?(?!\w)',  # e.g., "5V", "3.3VDC"
        'current': r'(\d+\.?\d*)\s*(mA|A)(?!\w)',  # e.g., "2A", "500mA"
        'power': r'(\d+\.?\d*)\s*(mW|W)(?!\w)',  # e.g., "10W", "500mW"
        'frequency': r'(\d+\.?\d*)\s*(MHz|GHz|Hz|KHz)',  # e.g., "2.4GHz", "100MHz"
        'capacity': r'(\d+\.?\d*)\s*mAh',  # e.g., "2200mAh"
        'resolution': r'(\d+)\s*[xX×]\s*(\d+)',  # e.g., "1920x1080"
        'megapixel': r'(\d+\.?\d*)\s*MP',  # e.g., "12MP"
        'fps': r'(\d+)\s*fps',  # e.g., "60fps"
        'kv_rating': r'(\d+)\s*KV',  # e.g., "2300KV"
        'clock_speed': r'(\d+\.?\d*)\s*(MHz|GHz)',  # e.g., "168MHz"
        'memory': r'(\d+\.?\d*)\s*(KB|MB|GB)',  # e.g., "256KB", "1MB"
        'temperature': r'(-?\d+\.?\d*)\s*°?C',  # e.g., "-40°C", "85C"
        'weight': r'(\d+\.?\d*)\s*(g|kg|oz|lb)',  # e.g., "50g", "2.5kg"
        'rpm': r'(\d+)\s*RPM',  # e.g., "5000 RPM"
        'channels': r'(\d+)\s*[-\s]?(?:ch|channel)',  # e.g., "8-channel"
    }

    INTERFACE_PATTERNS = {
        'uart': r'(\d+)\s*[×xX]?\s*UART',  # e.g., "3x UART", "3 UART"
        'i2c': r'(\d+)\s*[×xX]?\s*I2C',  # e.g., "2x I2C"
        'spi': r'(\d+)\s*[×xX]?\s*SPI',  # e.g., "1x SPI"
        'can': r'(\d+)\s*[×xX]?\s*CAN',  # e.g., "1x CAN"
        'usb': r'(\d+)\s*[×xX]?\s*USB',  # e.g., "1x USB"
        'gpio': r'(\d+)\s*[×xX]?\s*GPIO',  # e.g., "20x GPIO"
        'pwm': r'(\d+)\s*[×xX]?\s*PWM',  # e.g., "6x PWM"
    }

    COMPONENT_TYPE_KEYWORDS = {
        'motor': ['motor', 'brushless', 'servo', 'actuator', 'bldc'],
        'sensor': ['sensor', 'imu', 'gps', 'accelerometer', 'gyro', 'gyroscope',
                   'barometer', 'magnetometer', 'compass', 'lidar', 'ultrasonic'],
        'camera': ['camera', 'lens', 'megapixel', 'fps', 'resolution', 'cmos', 'ccd'],
        'processor': ['microcontroller', 'mcu', 'processor', 'cpu', 'arm', 'esp32',
                      'stm32', 'arduino', 'cortex', 'flight controller'],
        'battery': ['battery', 'lipo', 'li-po', 'li-ion', 'lithium', 'mah', 'cell'],
        'esc': ['esc', 'speed controller', 'electronic speed'],
        'radio': ['receiver', 'transmitter', 'radio', 'telemetry', 'rc', 'remote control'],
        'power': ['regulator', 'voltage regulator', 'buck', 'boost', 'ldo', 'pdb',
                  'power distribution'],
    }

    def __init__(self):
        """Initialize the specification parser."""
        logger.info("SpecificationParser initialized")

    def parse_power_specs(self, text: str) -> PowerSpec:
        """
        Extract power-related specifications from text.

        Args:
            text: Text to parse

        Returns:
            PowerSpec object with extracted power specifications
        """
        # Extract voltage (look for input/output context)
        voltage_input = self._extract_contextual_voltage(text, ['input', 'supply', 'vin'])
        voltage_output = self._extract_contextual_voltage(text, ['output', 'vout'])

        # If no contextual voltage found, get the first voltage mention
        if not voltage_input and not voltage_output:
            voltage = self._extract_pattern(text, 'voltage')
            voltage_input = voltage

        current = self._extract_pattern(text, 'current')
        power = self._extract_pattern(text, 'power')
        capacity = self._extract_pattern(text, 'capacity')

        return PowerSpec(
            voltage_input=voltage_input,
            voltage_output=voltage_output,
            current_rating=current,
            power_consumption=power,
            capacity=capacity
        )

    def parse_interfaces(self, text: str) -> InterfaceSpec:
        """
        Extract communication interface counts from text.

        Args:
            text: Text to parse

        Returns:
            InterfaceSpec object with interface counts
        """
        interfaces = InterfaceSpec()

        for interface, pattern in self.INTERFACE_PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                setattr(interfaces, f"{interface}_count", count)
                logger.debug(f"Found {count} {interface.upper()} interfaces")

        return interfaces

    def identify_component_type(self, text: str) -> Optional[str]:
        """
        Identify component category from text using keyword matching.

        Args:
            text: Text to analyze

        Returns:
            Component type string or None if not identified
        """
        text_lower = text.lower()

        # Count matches for each component type
        type_scores = {}
        for comp_type, keywords in self.COMPONENT_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                type_scores[comp_type] = score

        # Return type with highest score
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            logger.debug(f"Identified component type: {best_type[0]} (score: {best_type[1]})")
            return best_type[0]

        return None

    def extract_all_specs(self, text: str) -> Dict[str, str]:
        """
        Extract all specifications from text.

        Args:
            text: Text to parse

        Returns:
            Dictionary of all extracted specifications
        """
        specs = {}

        for spec_name, pattern in self.PATTERNS.items():
            value = self._extract_pattern(text, spec_name)
            if value:
                specs[spec_name] = value

        return specs

    def extract_component_name(self, text: str) -> Optional[str]:
        """
        Attempt to extract component name from text.

        Args:
            text: Text to parse

        Returns:
            Component name if found
        """
        # Look for model numbers (common patterns)
        model_patterns = [
            r'Model[:\s]+([A-Z0-9\-]+)',
            r'Part\s*(?:Number|No\.?)[:\s]+([A-Z0-9\-]+)',
            r'P/N[:\s]+([A-Z0-9\-]+)',
        ]

        for pattern in model_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def extract_manufacturer(self, text: str) -> Optional[str]:
        """
        Attempt to extract manufacturer name from text.

        Args:
            text: Text to parse

        Returns:
            Manufacturer name if found
        """
        # Look for manufacturer mentions
        manufacturer_patterns = [
            r'Manufacturer[:\s]+([A-Za-z\s&]+?)(?:\n|$)',
            r'Made by[:\s]+([A-Za-z\s&]+?)(?:\n|$)',
            r'(?:©|Copyright)[:\s]+\d{4}\s+([A-Za-z\s&]+?)(?:\n|$)',
        ]

        for pattern in manufacturer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_pattern(self, text: str, pattern_name: str) -> Optional[str]:
        """
        Extract value using regex pattern.

        Args:
            text: Text to search
            pattern_name: Name of pattern from PATTERNS dict

        Returns:
            Matched string or None
        """
        pattern = self.PATTERNS.get(pattern_name)
        if not pattern:
            return None

        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0).strip() if match else None

    def _extract_contextual_voltage(self, text: str, context_keywords: List[str]) -> Optional[str]:
        """
        Extract voltage with context (e.g., "input voltage: 5V").

        Args:
            text: Text to search
            context_keywords: Keywords to look for near voltage values

        Returns:
            Voltage string if found in context
        """
        for keyword in context_keywords:
            # Look for keyword followed by voltage within 20 characters
            pattern = f'{keyword}[\\s\\w:]*?({self.PATTERNS["voltage"]})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract just the voltage part
                voltage_match = re.search(self.PATTERNS['voltage'], match.group(0))
                if voltage_match:
                    return voltage_match.group(0).strip()

        return None

    def parse_table_specs(self, table: List[List[str]]) -> Dict[str, str]:
        """
        Extract specifications from a table structure.

        Args:
            table: 2D list representing table data

        Returns:
            Dictionary of extracted specifications
        """
        specs = {}

        if not table or len(table) < 2:
            return specs

        # Try to identify if first row is header
        headers = [cell.lower().strip() for cell in table[0]]

        # Common patterns for spec tables
        spec_indicators = ['specification', 'parameter', 'description', 'feature']
        value_indicators = ['value', 'rating', 'typical', 'min', 'max']

        spec_col_idx = None
        value_col_idx = None

        # Find specification and value columns
        for idx, header in enumerate(headers):
            if any(ind in header for ind in spec_indicators):
                spec_col_idx = idx
            elif any(ind in header for ind in value_indicators):
                value_col_idx = idx

        # Extract specs from identified columns
        if spec_col_idx is not None and value_col_idx is not None:
            for row in table[1:]:
                if len(row) > max(spec_col_idx, value_col_idx):
                    spec_name = row[spec_col_idx].strip()
                    spec_value = row[value_col_idx].strip()
                    if spec_name and spec_value:
                        specs[spec_name] = spec_value

        # Also extract using patterns from all cells
        table_text = ' '.join([' '.join(row) for row in table])
        pattern_specs = self.extract_all_specs(table_text)
        specs.update(pattern_specs)

        return specs

    def calculate_confidence(self, extracted_data: Dict) -> float:
        """
        Calculate confidence score for extracted data.

        Args:
            extracted_data: Dictionary of extracted specifications

        Returns:
            Confidence score between 0 and 1
        """
        # Simple confidence calculation based on number of fields extracted
        total_fields = 0
        filled_fields = 0

        for value in extracted_data.values():
            total_fields += 1
            if value:
                filled_fields += 1

        return filled_fields / total_fields if total_fields > 0 else 0.0
