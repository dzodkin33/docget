# Component Specification Analyzer

An intelligent agentic system that analyzes technical PDF datasheets to extract hardware component specifications for building projects like drones, robots, and electronics prototypes.

## Features

- **PDF Extraction**: Automatically extract text, tables, and metadata from PDF datasheets
- **Specification Parsing**: Intelligent pattern-based extraction of component specifications
- **Component Identification**: Automatically identify component types (motors, sensors, cameras, etc.)
- **Power Budget Analysis**: Calculate total power requirements and battery recommendations
- **Compatibility Checking**: Identify potential compatibility issues between components
- **BOM Generation**: Export bill of materials as CSV
- **Detailed Reports**: Generate comprehensive project reports in Markdown

## Project Structure

```
drone-component-analyzer/
├── src/
│   ├── agent/
│   │   ├── PdfExtractor.py          # PDF text/table extraction
│   │   └── SpecificationParser.py   # Component spec extraction
│   ├── models/
│   │   ├── Component.py             # Component data models
│   │   ├── Specification.py         # Spec data structures
│   │   └── Project.py               # Project requirements
│   └── utils/
│       ├── config.py                # Configuration management
│       ├── formatters.py            # Output formatting (CSV, MD)
│       └── validators.py            # Data validation
├── data/
│   ├── pdfs/                        # Input PDF folder
│   └── output/                      # Generated reports
├── prompts/
│   ├── component_extraction.txt     # Claude prompts
│   ├── compatibility_check.txt
│   ├── power_analysis.txt
│   └── recommendation.txt
├── tests/
│   ├── test_pdf_extractor.py
│   ├── test_spec_parser.py
│   └── test_integration.py
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### 1. Clone or navigate to the project directory

```bash
cd /Users/anujjain/drone-component-analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Usage

### Quick Start

1. Place your PDF datasheets in the `data/pdfs/` directory

2. Run the analyzer:
```bash
python main.py --pdf-folder ./data/pdfs --project-name "My Drone Project"
```

### Using the PDF Extractor

```python
from src.agent.PdfExtractor import PdfExtractor

# Extract from a PDF
extractor = PdfExtractor('path/to/datasheet.pdf')
content = extractor.extract_all()

# Access extracted data
text = content['text']
tables = content['tables']
metadata = content['metadata']
```

### Using the Specification Parser

```python
from src.agent.SpecificationParser import SpecificationParser

parser = SpecificationParser()

# Extract power specifications
text = "Operating voltage: 5V, current draw: 2A"
power_spec = parser.parse_power_specs(text)
print(power_spec.voltage_input)  # "5V"
print(power_spec.current_rating)  # "2A"

# Extract communication interfaces
text = "Features: 3x UART, 2x I2C, 1x SPI"
interfaces = parser.parse_interfaces(text)
print(interfaces.uart_count)  # 3

# Identify component type
text = "Brushless motor with 2300KV rating"
comp_type = parser.identify_component_type(text)
print(comp_type)  # "motor"
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_spec_parser.py

# Run with coverage
python -m pytest --cov=src tests/
```

## Component Categories Supported

### Power Components
- Batteries (LiPo, Li-ion)
- Voltage regulators
- Power distribution boards (PDB)
- Battery management systems (BMS)

### Processors & Controllers
- Microcontrollers (Arduino, STM32, ESP32)
- Flight controllers (Pixhawk, Betaflight)
- Single-board computers (Raspberry Pi)

### Sensors
- IMU (accelerometer, gyroscope)
- GPS modules
- Barometers, magnetometers
- Distance sensors (LIDAR, ultrasonic)

### Motors & Actuators
- Brushless motors
- Servo motors
- Electronic Speed Controllers (ESC)

### Cameras
- FPV cameras
- HD recording cameras

### Radio & Telemetry
- RC receivers
- Telemetry modules

## Extracted Specifications

The system extracts:

- **Power Specs**: Voltage, current, power consumption, battery capacity
- **Interfaces**: UART, I2C, SPI, CAN, USB, PWM counts
- **Motor Specs**: KV rating, RPM, torque
- **Camera Specs**: Resolution, FPS, FOV
- **Processor Specs**: Clock speed, RAM, Flash, architecture
- **Physical**: Weight, dimensions, temperature range
- **And more...**

## Development

### Code Style

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

### Adding New Patterns

To add new specification patterns, edit `src/agent/SpecificationParser.py`:

```python
PATTERNS = {
    'your_pattern_name': r'regex_pattern_here',
    # e.g., 'torque': r'(\d+\.?\d*)\s*(Nm|kg-cm)'
}
```

## Configuration

Configuration is managed through environment variables (`.env` file):

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required for Claude integration)
- `CLAUDE_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `MAX_TOKENS`: Maximum tokens for API calls (default: 4096)
- `TEMPERATURE`: Temperature for AI generation (default: 0 for deterministic)
- `LOG_LEVEL`: Logging level (default: INFO)

## Troubleshooting

### Common Issues

1. **"ANTHROPIC_API_KEY not found"**
   - Make sure you've created a `.env` file with your API key
   - Check that the `.env` file is in the project root directory

2. **PDF extraction fails**
   - Ensure the PDF is not encrypted or password-protected
   - Some PDFs may have complex layouts that are difficult to parse

3. **Low extraction accuracy**
   - Try different PDF files to see if the issue is file-specific
   - Check if the PDF contains actual text (not scanned images)

## Examples

### Example Output

```
Component Specification Analyzer
==================================================

Components Found: 12
Total Current: 45.2A
Estimated Power: 542.4W

Compatibility Issues: 1
Warnings: 0
Missing Components: 0

⚠️ Compatibility Warnings:
- ESC max current (30A) may be insufficient for motor peak draw (40A)
```

## Contributing

This is a research/educational project. Feel free to:
- Add new component type patterns
- Improve regex patterns for better extraction
- Add support for additional specification formats
- Enhance validation and compatibility checking

## License

MIT License - feel free to use for your projects!

## Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/) for intelligent extraction
- Uses [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF processing
- Uses [Pydantic](https://docs.pydantic.dev/) for data validation

---

**Note**: This project is in active development. More features and improvements coming soon!

Last Updated: 2025-11-25
tically extract text, tables, and metadata from PDF datasheets
- **Specification Parsing**: Intelligent pattern-based extraction of component specifications
- **Component Identification**: Automatically identify component types (motors, sensors, cameras, etc.)
- **Power Budget Analysis**: Calculate total power requirements and battery recommendations
- **Compatibility Checking**: Identify potential compatibility issues between components
- **BOM Generation**: Export bill of materials as CSV
- **Detailed Reports**: Generate comprehensive project reports in Markdown

## Project Structure

```
drone-component-analyzer/
├── src/
│   ├── agent/
│   │   ├── PdfExtractor.py          # PDF text/table extraction
│   │   └── SpecificationParser.py   # Component spec extraction
│   ├── models/
│   │   ├── Component.py             # Component data models
│   │   ├── Specification.py         # Spec data structures
│   │   └── Project.py               # Project requirements
│   └── utils/
│       ├── config.py                # Configuration management
│       ├── formatters.py            # Output formatting (CSV, MD)
│       └── validators.py            # Data validation
├── data/
│   ├── pdfs/                        # Input PDF folder
│   └── output/                      # Generated reports
├── prompts/
│   ├── component_extraction.txt     # Claude prompts
│   ├── compatibility_check.txt
│   ├── power_analysis.txt
│   └── recommendation.txt
├── tests/
│   ├── test_pdf_extractor.py
│   ├── test_spec_parser.py
│   └── test_integration.py
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### 1. Clone or navigate to the project directory

```bash
cd /Users/anujjain/drone-component-analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Usage

### Quick Start

1. Place your PDF datasheets in the `data/pdfs/` directory

2. Run the analyzer:
```bash
python main.py --pdf-folder ./data/pdfs --project-name "My Drone Project"
```

### Using the PDF Extractor

```python
from src.agent.PdfExtractor import PdfExtractor

# Extract from a PDF
extractor = PdfExtractor('path/to/datasheet.pdf')
content = extractor.extract_all()

# Access extracted data
text = content['text']
tables = content['tables']
metadata = content['metadata']
```

### Using the Specification Parser

```python
from src.agent.SpecificationParser import SpecificationParser

parser = SpecificationParser()

# Extract power specifications
text = "Operating voltage: 5V, current draw: 2A"
power_spec = parser.parse_power_specs(text)
print(power_spec.voltage_input)  # "5V"
print(power_spec.current_rating)  # "2A"

# Extract communication interfaces
text = "Features: 3x UART, 2x I2C, 1x SPI"
interfaces = parser.parse_interfaces(text)
print(interfaces.uart_count)  # 3

# Identify component type
text = "Brushless motor with 2300KV rating"
comp_type = parser.identify_component_type(text)
print(comp_type)  # "motor"
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_spec_parser.py

# Run with coverage
python -m pytest --cov=src tests/
```

## Component Categories Supported

### Power Components
- Batteries (LiPo, Li-ion)
- Voltage regulators
- Power distribution boards (PDB)
- Battery management systems (BMS)

### Processors & Controllers
- Microcontrollers (Arduino, STM32, ESP32)
- Flight controllers (Pixhawk, Betaflight)
- Single-board computers (Raspberry Pi)

### Sensors
- IMU (accelerometer, gyroscope)
- GPS modules
- Barometers, magnetometers
- Distance sensors (LIDAR, ultrasonic)

### Motors & Actuators
- Brushless motors
- Servo motors
- Electronic Speed Controllers (ESC)

### Cameras
- FPV cameras
- HD recording cameras

### Radio & Telemetry
- RC receivers
- Telemetry modules

## Extracted Specifications

The system extracts:

- **Power Specs**: Voltage, current, power consumption, battery capacity
- **Interfaces**: UART, I2C, SPI, CAN, USB, PWM counts
- **Motor Specs**: KV rating, RPM, torque
- **Camera Specs**: Resolution, FPS, FOV
- **Processor Specs**: Clock speed, RAM, Flash, architecture
- **Physical**: Weight, dimensions, temperature range
- **And more...**

## Development

### Code Style

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

### Adding New Patterns

To add new specification patterns, edit `src/agent/SpecificationParser.py`:

```python
PATTERNS = {
    'your_pattern_name': r'regex_pattern_here',
    # e.g., 'torque': r'(\d+\.?\d*)\s*(Nm|kg-cm)'
}
```

## Configuration

Configuration is managed through environment variables (`.env` file):

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required for Claude integration)
- `CLAUDE_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `MAX_TOKENS`: Maximum tokens for API calls (default: 4096)
- `TEMPERATURE`: Temperature for AI generation (default: 0 for deterministic)
- `LOG_LEVEL`: Logging level (default: INFO)

## Troubleshooting

### Common Issues

1. **"ANTHROPIC_API_KEY not found"**
   - Make sure you've created a `.env` file with your API key
   - Check that the `.env` file is in the project root directory

2. **PDF extraction fails**
   - Ensure the PDF is not encrypted or password-protected
   - Some PDFs may have complex layouts that are difficult to parse

3. **Low extraction accuracy**
   - Try different PDF files to see if the issue is file-specific
   - Check if the PDF contains actual text (not scanned images)

## Examples

### Example Output

```
Component Specification Analyzer
==================================================

Components Found: 12
Total Current: 45.2A
Estimated Power: 542.4W

Compatibility Issues: 1
Warnings: 0
Missing Components: 0

⚠️ Compatibility Warnings:
- ESC max current (30A) may be insufficient for motor peak draw (40A)
```

## Contributing

This is a research/educational project. Feel free to:
- Add new component type patterns
- Improve regex patterns for better extraction
- Add support for additional specification formats
- Enhance validation and compatibility checking

## License

MIT License - feel free to use for your projects!

## Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/) for intelligent extraction
- Uses [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF processing
- Uses [Pydantic](https://docs.pydantic.dev/) for data validation

---

**Note**: This project is in active development. More features and improvements coming soon!

Last Updated: 2025-11-25
