import re
from typing import List, Dict, Tuple
import logging
import sys
sys.path.append('/Users/anujjain/drone-component-analyzer')
from src.models.Component import Component
from src.models.Project import Project

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComponentValidator:
    """Validate component data and specifications."""

    VALID_COMPONENT_TYPES = {
        'motor', 'sensor', 'camera', 'processor', 'battery',
        'esc', 'radio', 'power', 'other'
    }

    @staticmethod
    def validate_component(component: Component) -> Tuple[bool, List[str]]:
        """
        Validate a component object.

        Args:
            component: Component to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check required fields
        if not component.name:
            errors.append("Component name is required")

        if not component.component_type:
            errors.append("Component type is required")
        elif component.component_type not in ComponentValidator.VALID_COMPONENT_TYPES:
            logger.warning(f"Unknown component type: {component.component_type}")

        if not component.source_document:
            errors.append("Source document is required")

        # Validate power specs
        power_errors = ComponentValidator._validate_power_spec(component.power)
        errors.extend(power_errors)

        return (len(errors) == 0, errors)

    @staticmethod
    def _validate_power_spec(power_spec) -> List[str]:
        """Validate power specification format."""
        errors = []

        # Voltage pattern: number followed by V
        voltage_pattern = r'^\d+\.?\d*V(DC|AC)?$'

        if power_spec.voltage_input:
            if not re.match(voltage_pattern, power_spec.voltage_input, re.IGNORECASE):
                errors.append(f"Invalid voltage input format: {power_spec.voltage_input}")

        if power_spec.voltage_output:
            if not re.match(voltage_pattern, power_spec.voltage_output, re.IGNORECASE):
                errors.append(f"Invalid voltage output format: {power_spec.voltage_output}")

        # Current pattern: number followed by mA or A
        current_pattern = r'^\d+\.?\d*(mA|A)$'

        if power_spec.current_rating:
            if not re.match(current_pattern, power_spec.current_rating, re.IGNORECASE):
                errors.append(f"Invalid current rating format: {power_spec.current_rating}")

        # Power pattern: number followed by mW or W
        power_pattern = r'^\d+\.?\d*(mW|W)$'

        if power_spec.power_consumption:
            if not re.match(power_pattern, power_spec.power_consumption, re.IGNORECASE):
                errors.append(f"Invalid power consumption format: {power_spec.power_consumption}")

        # Capacity pattern: number followed by mAh
        capacity_pattern = r'^\d+\.?\d*mAh$'

        if power_spec.capacity:
            if not re.match(capacity_pattern, power_spec.capacity, re.IGNORECASE):
                errors.append(f"Invalid capacity format: {power_spec.capacity}")

        return errors

    @staticmethod
    def check_completeness(component: Component) -> float:
        """
        Calculate completeness score for a component.

        Args:
            component: Component to check

        Returns:
            Completeness score between 0 and 1
        """
        total_fields = 0
        filled_fields = 0

        # Core fields
        fields_to_check = [
            component.name,
            component.component_type,
            component.manufacturer,
            component.part_number,
            component.power.voltage_input,
            component.power.current_rating,
        ]

        for field in fields_to_check:
            total_fields += 1
            if field:
                filled_fields += 1

        # Interface counts (if any > 0, count as filled)
        total_fields += 1
        if any([
            component.interfaces.uart_count > 0,
            component.interfaces.i2c_count > 0,
            component.interfaces.spi_count > 0,
            component.interfaces.usb_count > 0
        ]):
            filled_fields += 1

        # Specific specs
        total_fields += 1
        if component.specific_specs:
            filled_fields += 1

        return filled_fields / total_fields if total_fields > 0 else 0.0


class SpecValidator:
    """Validate extracted specifications."""

    @staticmethod
    def validate_project(project: Project) -> Tuple[bool, List[str]]:
        """
        Validate a complete project.

        Args:
            project: Project to validate

        Returns:
            Tuple of (is_valid, list of warnings)
        """
        warnings = []

        # Check if project has components
        if not project.components:
            warnings.append("No components found in project")

        # Validate each component
        for idx, component in enumerate(project.components):
            is_valid, errors = ComponentValidator.validate_component(component)
            if not is_valid:
                warnings.append(f"Component {idx + 1} ({component.name}): {', '.join(errors)}")

        # Check for essential components (for drone projects)
        if 'drone' in project.name.lower() or 'quadcopter' in project.name.lower():
            essential_warnings = SpecValidator._check_essential_drone_components(project)
            warnings.extend(essential_warnings)

        return (len(warnings) == 0, warnings)

    @staticmethod
    def _check_essential_drone_components(project: Project) -> List[str]:
        """Check for essential drone components."""
        warnings = []

        component_types = [c.component_type for c in project.components]

        essentials = {
            'processor': 'Flight controller or microcontroller',
            'motor': 'Motors for propulsion',
            'esc': 'Electronic speed controllers',
            'battery': 'Power source',
            'radio': 'Remote control receiver'
        }

        for comp_type, description in essentials.items():
            if comp_type not in component_types:
                warnings.append(f"Missing essential component: {description}")

        return warnings

    @staticmethod
    def check_power_compatibility(project: Project) -> List[str]:
        """
        Check power compatibility across components.

        Args:
            project: Project to check

        Returns:
            List of compatibility issues
        """
        issues = []

        # Extract all voltage requirements
        voltages = []
        for comp in project.components:
            if comp.power.voltage_input:
                # Extract numeric value
                match = re.search(r'(\d+\.?\d*)', comp.power.voltage_input)
                if match:
                    voltages.append((comp.name, float(match.group(1))))

        # Check for voltage mismatches
        if len(voltages) > 1:
            unique_voltages = set(v for _, v in voltages)
            if len(unique_voltages) > 3:
                issues.append(
                    f"Multiple voltage requirements detected: {unique_voltages}. "
                    "May need voltage regulators."
                )

        # Check current requirements vs battery
        batteries = [c for c in project.components if c.component_type == 'battery']
        if batteries:
            # This is a simplified check - real implementation would be more complex
            total_current = project.total_power_budget.get('total_current_a', 0)
            if total_current > 50:
                issues.append(
                    f"High total current draw ({total_current}A). "
                    "Ensure battery and wiring can handle this load."
                )

        return issues

    @staticmethod
    def check_interface_availability(project: Project) -> List[str]:
        """
        Check if processor has enough interfaces for peripherals.

        Args:
            project: Project to check

        Returns:
            List of interface issues
        """
        issues = []

        # Find processors/controllers
        processors = [c for c in project.components
                      if c.component_type in ['processor', 'controller']]

        if not processors:
            return ["No processor/controller found to connect peripherals"]

        # Get main processor (assume first one)
        main_processor = processors[0]

        # Count required interfaces from peripherals
        required_uart = 0
        required_i2c = 0
        required_spi = 0

        for comp in project.components:
            if comp.component_type in ['sensor', 'radio', 'camera']:
                # Estimate interface needs (simplified)
                if 'uart' in str(comp.specific_specs).lower():
                    required_uart += 1
                if 'i2c' in str(comp.specific_specs).lower():
                    required_i2c += 1
                if 'spi' in str(comp.specific_specs).lower():
                    required_spi += 1

        # Check availability
        if required_uart > main_processor.interfaces.uart_count:
            issues.append(
                f"Insufficient UART ports: need {required_uart}, "
                f"have {main_processor.interfaces.uart_count}"
            )

        if required_i2c > main_processor.interfaces.i2c_count:
            issues.append(
                f"Insufficient I2C ports: need {required_i2c}, "
                f"have {main_processor.interfaces.i2c_count}"
            )

        if required_spi > main_processor.interfaces.spi_count:
            issues.append(
                f"Insufficient SPI ports: need {required_spi}, "
                f"have {main_processor.interfaces.spi_count}"
            )

        return issues
