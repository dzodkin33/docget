import unittest
import sys
from pathlib import Path

sys.path.append('/Users/anujjain/drone-component-analyzer')
from src.agent.PdfExtractor import PdfExtractor
from src.agent.SpecificationParser import SpecificationParser
from src.models.Component import Component, PowerSpec, InterfaceSpec
from src.models.Project import Project


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = SpecificationParser()
        self.project = Project(name="Test Drone Project")

    def test_pdf_to_component_workflow(self):
        """Test complete workflow from PDF to component extraction."""
        # This test requires actual PDF files
        pdf_dir = Path(__file__).parent.parent / 'data' / 'pdfs'
        pdfs = list(pdf_dir.glob('*.pdf'))

        if not pdfs:
            self.skipTest("No sample PDFs available for integration testing")

        # Extract from first PDF
        extractor = PdfExtractor(str(pdfs[0]))
        content = extractor.extract_all()

        # Parse specifications
        full_text = ' '.join([p['text'] for p in content['text']])
        power_spec = self.parser.parse_power_specs(full_text)
        interfaces = self.parser.parse_interfaces(full_text)
        comp_type = self.parser.identify_component_type(full_text)

        # Verify we got some data
        self.assertIsInstance(power_spec, PowerSpec)
        self.assertIsInstance(interfaces, InterfaceSpec)

    def test_project_component_aggregation(self):
        """Test adding multiple components to a project."""
        # Create test components
        comp1 = Component(
            name="Test Motor",
            component_type="motor",
            manufacturer="TestCo",
            source_document="test.pdf",
            power=PowerSpec(voltage_input="11.1V", current_rating="25A")
        )

        comp2 = Component(
            name="Test Controller",
            component_type="processor",
            manufacturer="TestCo",
            source_document="test.pdf",
            power=PowerSpec(voltage_input="5V", current_rating="500mA"),
            interfaces=InterfaceSpec(uart_count=3, i2c_count=2)
        )

        # Add to project
        self.project.add_component(comp1)
        self.project.add_component(comp2)

        # Verify
        self.assertEqual(len(self.project.components), 2)
        motors = self.project.get_components_by_type('motor')
        self.assertEqual(len(motors), 1)
        self.assertEqual(motors[0].name, "Test Motor")

    def test_specification_extraction_from_realistic_text(self):
        """Test extraction from realistic component description."""
        realistic_text = """
        Pixhawk 4 Flight Controller
        Manufacturer: Holybro
        Part Number: PH4-001

        Technical Specifications:
        - Processor: STM32F765
        - Operating Voltage: 5V DC
        - Current Draw: 500mA typical
        - RAM: 512KB
        - Flash: 2MB
        - Interfaces: 6x UART, 3x I2C, 2x SPI, 1x CAN, 1x USB
        - PWM Outputs: 16 channels
        - Weight: 15.5g
        """

        # Extract specifications
        power_spec = self.parser.parse_power_specs(realistic_text)
        interfaces = self.parser.parse_interfaces(realistic_text)
        comp_type = self.parser.identify_component_type(realistic_text)
        all_specs = self.parser.extract_all_specs(realistic_text)

        # Verify power specs
        self.assertIsNotNone(power_spec.voltage_input)
        self.assertIn('5V', power_spec.voltage_input)
        self.assertIsNotNone(power_spec.current_rating)

        # Verify interfaces
        self.assertEqual(interfaces.uart_count, 6)
        self.assertEqual(interfaces.i2c_count, 3)
        self.assertEqual(interfaces.spi_count, 2)

        # Verify component type
        self.assertEqual(comp_type, 'processor')

        # Verify additional specs extracted
        self.assertIn('weight', all_specs)

    def test_motor_specification_extraction(self):
        """Test extraction from motor datasheet text."""
        motor_text = """
        EMAX RS2205 2300KV Brushless Motor

        Specifications:
        - KV Rating: 2300KV
        - Voltage: 7.4V - 14.8V (2S - 4S LiPo)
        - Max Current: 25A
        - Weight: 28g
        - Shaft Diameter: 5mm
        """

        power_spec = self.parser.parse_power_specs(motor_text)
        comp_type = self.parser.identify_component_type(motor_text)
        all_specs = self.parser.extract_all_specs(motor_text)

        # Verify
        self.assertEqual(comp_type, 'motor')
        self.assertIn('kv_rating', all_specs)
        self.assertIn('2300KV', all_specs['kv_rating'])

    def test_battery_specification_extraction(self):
        """Test extraction from battery specification."""
        battery_text = """
        Tattu 2200mAh 3S LiPo Battery

        Specifications:
        - Capacity: 2200mAh
        - Voltage: 11.1V (3S configuration)
        - Discharge Rate: 25C
        - Weight: 185g
        - Chemistry: Lithium Polymer (LiPo)
        """

        power_spec = self.parser.parse_power_specs(battery_text)
        comp_type = self.parser.identify_component_type(battery_text)

        # Verify
        self.assertEqual(comp_type, 'battery')
        self.assertIsNotNone(power_spec.capacity)
        self.assertIn('2200mAh', power_spec.capacity)
        self.assertIsNotNone(power_spec.voltage_input)

    def test_camera_specification_extraction(self):
        """Test extraction from camera specification."""
        camera_text = """
        RunCam Split 3 FPV Camera

        Specifications:
        - Resolution: 1920x1080 @ 60fps
        - Sensor: 12MP CMOS
        - Interface: USB 2.0
        - Operating Voltage: 5V
        - Current Draw: 380mA
        - Weight: 14g
        - Field of View: 165°
        """

        power_spec = self.parser.parse_power_specs(camera_text)
        comp_type = self.parser.identify_component_type(camera_text)
        all_specs = self.parser.extract_all_specs(camera_text)

        # Verify
        self.assertEqual(comp_type, 'camera')
        self.assertIn('resolution', all_specs)
        self.assertIn('fps', all_specs)
        self.assertIn('megapixel', all_specs)


if __name__ == '__main__':
    unittest.main()
