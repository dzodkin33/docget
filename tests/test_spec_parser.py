import unittest
import sys

sys.path.append('/Users/anujjain/drone-component-analyzer')
from src.agent.SpecificationParser import SpecificationParser
from src.models.Component import PowerSpec, InterfaceSpec


class TestSpecificationParser(unittest.TestCase):
    """Test cases for specification parsing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = SpecificationParser()

    def test_voltage_extraction(self):
        """Test voltage pattern extraction."""
        test_cases = [
            ("Operating voltage: 5V DC", "5V"),
            ("Input: 12VDC", "12VDC"),
            ("3.3V nominal", "3.3V"),
        ]

        for text, expected in test_cases:
            result = self.parser._extract_pattern(text, 'voltage')
            self.assertIsNotNone(result)
            self.assertIn(expected.split('V')[0], result)

    def test_current_extraction(self):
        """Test current pattern extraction."""
        test_cases = [
            ("Maximum current: 2A", "2A"),
            ("Current draw: 500mA", "500mA"),
            ("Peak: 3.5A", "3.5A"),
        ]

        for text, expected in test_cases:
            result = self.parser._extract_pattern(text, 'current')
            self.assertIsNotNone(result)

    def test_power_extraction(self):
        """Test power consumption extraction."""
        test_cases = [
            ("Power consumption: 10W", "10W"),
            ("Max power: 500mW", "500mW"),
            ("15.5W typical", "15.5W"),
        ]

        for text, expected in test_cases:
            result = self.parser._extract_pattern(text, 'power')
            self.assertIsNotNone(result)

    def test_capacity_extraction(self):
        """Test battery capacity extraction."""
        test_cases = [
            ("Capacity: 2200mAh", "2200mAh"),
            ("5000mAh LiPo", "5000mAh"),
        ]

        for text, expected in test_cases:
            result = self.parser._extract_pattern(text, 'capacity')
            self.assertEqual(result, expected)

    def test_kv_rating_extraction(self):
        """Test motor KV rating extraction."""
        text = "Brushless motor 2300KV rating"
        result = self.parser._extract_pattern(text, 'kv_rating')
        self.assertEqual(result, "2300KV")

    def test_resolution_extraction(self):
        """Test resolution pattern extraction."""
        test_cases = [
            ("1920x1080 resolution", True),
            ("4K 3840×2160", True),
            ("640X480 VGA", True),
        ]

        for text, should_match in test_cases:
            result = self.parser._extract_pattern(text, 'resolution')
            if should_match:
                self.assertIsNotNone(result)

    def test_interface_parsing_uart(self):
        """Test UART interface detection."""
        text = "Features: 3x UART, 2x I2C, 1x SPI"
        interfaces = self.parser.parse_interfaces(text)

        self.assertEqual(interfaces.uart_count, 3)
        self.assertEqual(interfaces.i2c_count, 2)
        self.assertEqual(interfaces.spi_count, 1)

    def test_interface_parsing_multiple_formats(self):
        """Test interface detection with various formats."""
        test_cases = [
            ("6 UART ports", 6, 'uart'),
            ("2×I2C", 2, 'i2c'),
            ("1 x SPI", 1, 'spi'),
        ]

        for text, expected_count, interface_type in test_cases:
            interfaces = self.parser.parse_interfaces(text)
            actual_count = getattr(interfaces, f"{interface_type}_count")
            self.assertEqual(actual_count, expected_count)

    def test_component_type_identification_motor(self):
        """Test motor component identification."""
        text = "This brushless motor operates at 2300KV with maximum current of 25A"
        comp_type = self.parser.identify_component_type(text)
        self.assertEqual(comp_type, 'motor')

    def test_component_type_identification_sensor(self):
        """Test sensor component identification."""
        text = "IMU sensor with accelerometer and gyroscope, 100Hz update rate"
        comp_type = self.parser.identify_component_type(text)
        self.assertEqual(comp_type, 'sensor')

    def test_component_type_identification_camera(self):
        """Test camera component identification."""
        text = "1920x1080 camera with 60fps and 12MP sensor"
        comp_type = self.parser.identify_component_type(text)
        self.assertEqual(comp_type, 'camera')

    def test_component_type_identification_processor(self):
        """Test processor component identification."""
        text = "STM32 microcontroller with ARM Cortex-M4 running at 168MHz"
        comp_type = self.parser.identify_component_type(text)
        self.assertEqual(comp_type, 'processor')

    def test_component_type_identification_battery(self):
        """Test battery component identification."""
        text = "LiPo battery 3S 2200mAh 11.1V"
        comp_type = self.parser.identify_component_type(text)
        self.assertEqual(comp_type, 'battery')

    def test_power_specs_parsing(self):
        """Test complete power specification parsing."""
        text = "Input voltage: 12V, current rating: 2A, power consumption: 24W"
        power_spec = self.parser.parse_power_specs(text)

        self.assertIsInstance(power_spec, PowerSpec)
        self.assertIsNotNone(power_spec.voltage_input)
        self.assertIsNotNone(power_spec.current_rating)
        self.assertIsNotNone(power_spec.power_consumption)

    def test_extract_all_specs(self):
        """Test extraction of all specifications from text."""
        text = """
        Motor Specifications:
        - Voltage: 11.1V
        - Current: 25A
        - Power: 277W
        - KV Rating: 2300KV
        - Weight: 50g
        """
        specs = self.parser.extract_all_specs(text)

        self.assertIsInstance(specs, dict)
        self.assertIn('voltage', specs)
        self.assertIn('current', specs)
        self.assertIn('kv_rating', specs)

    def test_table_specs_parsing(self):
        """Test specification extraction from table data."""
        table = [
            ['Parameter', 'Value'],
            ['Voltage', '5V'],
            ['Current', '2A'],
            ['Weight', '25g']
        ]

        specs = self.parser.parse_table_specs(table)
        self.assertIsInstance(specs, dict)

    def test_empty_text_handling(self):
        """Test parser handles empty text gracefully."""
        result = self.parser.parse_power_specs("")
        self.assertIsInstance(result, PowerSpec)

        result = self.parser.parse_interfaces("")
        self.assertIsInstance(result, InterfaceSpec)

        result = self.parser.identify_component_type("")
        self.assertIsNone(result)

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        # All fields filled
        data_full = {
            'voltage': '5V',
            'current': '2A',
            'power': '10W'
        }
        confidence = self.parser.calculate_confidence(data_full)
        self.assertEqual(confidence, 1.0)

        # Partially filled
        data_partial = {
            'voltage': '5V',
            'current': None,
            'power': None
        }
        confidence = self.parser.calculate_confidence(data_partial)
        self.assertLess(confidence, 1.0)
        self.assertGreater(confidence, 0.0)

        # Empty
        data_empty = {}
        confidence = self.parser.calculate_confidence(data_empty)
        self.assertEqual(confidence, 0.0)


if __name__ == '__main__':
    unittest.main()
