# Component Specification Extraction System - Implementation Plan

## Project Overview
Build an agentic system that analyzes technical PDFs to extract physical component requirements and specifications for building hardware projects like drones. The system will read PDFs, identify components, extract specifications, and provide concrete requirements and device recommendations.

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│         CLI Interface (Terminal)            │
│     - Folder input                          │
│     - Progress display                      │
│     - Report generation                     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Project Analyzer (Orchestrator)        │
│   - Coordinate PDF processing               │
│   - Aggregate component data                │
│   - Generate BOM & recommendations          │
└──────┬──────────────────────┬────────────┬──┘
       │                      │            │
       ▼                      ▼            ▼
┌──────────────┐    ┌─────────────────┐  ┌────────────────┐
│ PDF Extractor│    │ Claude Agent    │  │ Spec Parser    │
│ - Text       │    │ - Intelligence  │  │ - Power reqs   │
│ - Tables     │    │ - Extraction    │  │ - Interfaces   │
│ - Images     │    │ - Compatibility │  │ - Component ID │
└──────────────┘    └─────────────────┘  └────────────────┘
       │                      │                    │
       └──────────────────────┴────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Output Reports  │
                    │  - BOM (CSV)     │
                    │  - Power budget  │
                    │  - Compatibility │
                    └──────────────────┘
```

---

## Directory Structure

```
drone-component-analyzer/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── PdfExtractor.py          # PDF text/table extraction
│   │   ├── SpecificationParser.py   # Component spec extraction
│   │   ├── ProjectAnalyzer.py       # Main orchestrator
│   │   └── ClaudeAgent.py           # Claude API integration
│   ├── model/
│   │   ├── __init__.py
│   │   ├── Component.py             # Component data models
│   │   ├── Specification.py         # Spec data structures
│   │   └── Project.py               # Project requirements
│   └── utils/
│       ├── __init__.py
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
├── main.py                          # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Component Categories & Specifications

### 1. **Power Components**
**Specifications to Extract:**
- Voltage (input/output): `3.7V`, `5V`, `12V`
- Current rating: `2A`, `500mA`, `10A`
- Capacity (batteries): `2200mAh`, `5000mAh`
- Power consumption: `5W`, `100mW`

**Component Types:**
- Batteries (LiPo, Li-ion)
- Voltage regulators (LDO, buck/boost converters)
- Power distribution boards (PDB)
- Battery management systems (BMS)

### 2. **Processors & Controllers**
**Specifications to Extract:**
- Clock speed: `168MHz`, `2.4GHz`
- RAM/Flash: `256KB RAM`, `1MB Flash`
- Architecture: `ARM Cortex-M4`, `ESP32`
- Communication interfaces count: `3x UART`, `2x I2C`, `1x SPI`

**Component Types:**
- Microcontrollers (Arduino, STM32, ESP32)
- Flight controllers (Pixhawk, Betaflight)
- Single-board computers (Raspberry Pi)

### 3. **Communication Interfaces**
**Specifications to Extract:**
- Protocol: `UART`, `I2C`, `SPI`, `CAN`, `USB`
- Baud rate: `115200`, `9600`
- Voltage levels: `3.3V`, `5V TTL`
- Pin count/channels

### 4. **Sensors**
**Specifications to Extract:**
- Type: `IMU`, `GPS`, `Barometer`, `Magnetometer`
- Range: `±2g`, `±16g` (accelerometer)
- Update rate: `100Hz`, `1kHz`
- Accuracy: `±0.5m` (GPS)
- Interface: `I2C`, `SPI`

### 5. **Motors & Actuators**
**Specifications to Extract:**
- KV rating: `2300KV`, `1000KV`
- Max current: `25A`, `40A`
- Torque: `10Nm`, `5kg-cm`
- Operating voltage: `7.4V-14.8V`
- RPM: `0-5000 RPM`

**Component Types:**
- Brushless motors
- Servo motors
- Stepper motors
- Electronic Speed Controllers (ESC)

### 6. **Cameras**
**Specifications to Extract:**
- Resolution: `1920x1080`, `4K`, `12MP`
- Frame rate: `30fps`, `60fps`, `120fps`
- Interface: `USB 2.0`, `MIPI CSI`, `HDMI`
- FOV: `120°`, `170°`
- Sensor size: `1/2.3"`, `1/4"`

### 7. **Radio & Telemetry**
**Specifications to Extract:**
- Frequency: `2.4GHz`, `900MHz`, `433MHz`
- Channels: `8-channel`, `16-channel`
- Range: `1km`, `10km`
- Protocol: `PPM`, `SBUS`, `IBUS`, `MAVLink`

---

## Implementation Phases

### **Phase 1: Foundation (Days 1-2)**

#### 1.1 Project Setup
**Tasks:**
- [ ] Create directory structure
- [ ] Initialize virtual environment
- [ ] Install dependencies
- [ ] Configure environment variables
- [ ] Create basic README

**Dependencies:**
```txt
# requirements.txt
anthropic>=0.18.0
pdfplumber>=0.10.0
pydantic>=2.5.0
click>=8.1.0
tabulate>=0.9.0
python-dotenv>=1.0.0
pandas>=2.0.0
regex>=2023.0.0
```

#### 1.2 Data Models
**Create Pydantic models:**

```python
# src/models/Component.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class PowerSpec(BaseModel):
    voltage_input: Optional[str] = None
    voltage_output: Optional[str] = None
    current_rating: Optional[str] = None
    power_consumption: Optional[str] = None

class InterfaceSpec(BaseModel):
    uart_count: int = 0
    i2c_count: int = 0
    spi_count: int = 0
    can_count: int = 0
    usb_count: int = 0
    gpio_count: int = 0

class Component(BaseModel):
    name: str
    component_type: str  # motor, sensor, processor, camera, etc.
    manufacturer: Optional[str] = None
    part_number: Optional[str] = None
    power: PowerSpec
    interfaces: InterfaceSpec
    specific_specs: Dict[str, str] = Field(default_factory=dict)
    source_document: str
    page_number: Optional[int] = None

class Project(BaseModel):
    name: str
    components: List[Component]
    total_power_budget: Dict[str, float]
    compatibility_issues: List[str] = Field(default_factory=list)
    missing_components: List[str] = Field(default_factory=list)
```

---

### **Phase 2: PDF Processing (Days 2-3)**

#### 2.1 PDF Extractor Implementation

```python
# src/agent/PdfExtractor.py
import pdfplumber
from typing import Dict, List
from pathlib import Path

class PdfExtractor:
    """Extract text, tables, and metadata from PDF files."""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.document_name = self.pdf_path.stem

    def extract_all(self) -> Dict:
        """Extract all content from PDF."""
        with pdfplumber.open(self.pdf_path) as pdf:
            return {
                'metadata': self.extract_metadata(pdf),
                'text': self.extract_text(pdf),
                'tables': self.extract_tables(pdf),
                'page_count': len(pdf.pages)
            }

    def extract_text(self, pdf) -> List[Dict]:
        """Extract text from each page."""
        pages = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages.append({
                    'page_number': i + 1,
                    'text': text
                })
        return pages

    def extract_tables(self, pdf) -> List[Dict]:
        """Extract tables from PDF (common in spec sheets)."""
        tables = []
        for i, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            for table in page_tables:
                tables.append({
                    'page_number': i + 1,
                    'data': table
                })
        return tables

    def extract_metadata(self, pdf) -> Dict:
        """Extract PDF metadata."""
        return {
            'title': pdf.metadata.get('Title', ''),
            'author': pdf.metadata.get('Author', ''),
            'subject': pdf.metadata.get('Subject', ''),
        }
```

**Features:**
- Text extraction with page tracking
- Table extraction (crucial for spec sheets)
- Metadata extraction
- Error handling for corrupted PDFs

---

### **Phase 3: Specification Parser (Days 3-4)**

#### 3.1 Pattern-Based Extraction

```python
# src/agent/SpecificationParser.py
import re
from typing import Dict, List, Optional
from models.Component import PowerSpec, InterfaceSpec

class SpecificationParser:
    """Parse component specifications from extracted text."""

    # Regex patterns for common specifications
    PATTERNS = {
        'voltage': r'(\d+\.?\d*)\s*V(?:DC|AC)?',
        'current': r'(\d+\.?\d*)\s*(mA|A)',
        'power': r'(\d+\.?\d*)\s*(mW|W)',
        'frequency': r'(\d+\.?\d*)\s*(MHz|GHz|Hz|KHz)',
        'capacity': r'(\d+\.?\d*)\s*mAh',
        'resolution': r'(\d+)\s*[xX×]\s*(\d+)',
        'megapixel': r'(\d+\.?\d*)\s*MP',
        'fps': r'(\d+)\s*fps',
        'kv_rating': r'(\d+)\s*KV',
    }

    INTERFACE_PATTERNS = {
        'uart': r'(\d+)\s*[×xX]?\s*UART',
        'i2c': r'(\d+)\s*[×xX]?\s*I2C',
        'spi': r'(\d+)\s*[×xX]?\s*SPI',
    }

    def parse_power_specs(self, text: str) -> PowerSpec:
        """Extract power-related specifications."""
        voltage = self._extract_pattern(text, 'voltage')
        current = self._extract_pattern(text, 'current')
        power = self._extract_pattern(text, 'power')

        return PowerSpec(
            voltage_input=voltage,
            current_rating=current,
            power_consumption=power
        )

    def parse_interfaces(self, text: str) -> InterfaceSpec:
        """Extract communication interface counts."""
        interfaces = InterfaceSpec()

        for interface, pattern in self.INTERFACE_PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                setattr(interfaces, f"{interface}_count", int(match.group(1)))

        return interfaces

    def identify_component_type(self, text: str) -> Optional[str]:
        """Identify component category from text."""
        keywords = {
            'motor': ['motor', 'brushless', 'servo', 'actuator'],
            'sensor': ['sensor', 'imu', 'gps', 'accelerometer', 'gyro', 'barometer'],
            'camera': ['camera', 'lens', 'megapixel', 'fps', 'resolution'],
            'processor': ['microcontroller', 'mcu', 'processor', 'cpu', 'arm', 'esp32'],
            'battery': ['battery', 'lipo', 'mah', 'cell'],
            'esc': ['esc', 'speed controller'],
            'radio': ['receiver', 'transmitter', 'radio', 'telemetry'],
        }

        text_lower = text.lower()
        for comp_type, kws in keywords.items():
            if any(kw in text_lower for kw in kws):
                return comp_type

        return None

    def _extract_pattern(self, text: str, pattern_name: str) -> Optional[str]:
        """Extract value using regex pattern."""
        pattern = self.PATTERNS.get(pattern_name)
        if not pattern:
            return None

        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else None
```

---

### **Phase 4: Claude Integration (Days 4-5)**

#### 4.1 Claude Agent for Intelligent Extraction

```python
# src/agent/ClaudeAgent.py
from anthropic import Anthropic
from typing import Dict, List
import json
from pathlib import Path

class ClaudeAgent:
    """Use Claude for intelligent component specification extraction."""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.prompts = self._load_prompts()

    def extract_component_specs(self, text: str, table_data: List = None) -> Dict:
        """Extract component specifications using Claude."""
        prompt = self.prompts['component_extraction'].format(
            text=text,
            tables=self._format_tables(table_data) if table_data else "No tables"
        )

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return self._parse_response(response.content[0].text)

    def analyze_compatibility(self, components: List[Dict]) -> Dict:
        """Check compatibility between components."""
        prompt = self.prompts['compatibility_check'].format(
            components=json.dumps(components, indent=2)
        )

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return self._parse_response(response.content[0].text)

    def suggest_alternatives(self, component: Dict, issue: str) -> List[Dict]:
        """Suggest alternative components."""
        prompt = self.prompts['recommendation'].format(
            component=json.dumps(component, indent=2),
            issue=issue
        )

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return self._parse_response(response.content[0].text)

    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates from files."""
        prompts = {}
        prompt_dir = Path(__file__).parent.parent.parent / 'prompts'

        for prompt_file in prompt_dir.glob('*.txt'):
            prompts[prompt_file.stem] = prompt_file.read_text()

        return prompts

    def _format_tables(self, tables: List) -> str:
        """Format table data for Claude."""
        formatted = []
        for i, table in enumerate(tables):
            formatted.append(f"Table {i+1}:\n{self._table_to_markdown(table)}")
        return "\n\n".join(formatted)

    def _table_to_markdown(self, table: List[List]) -> str:
        """Convert table to markdown format."""
        if not table:
            return ""

        rows = [" | ".join(str(cell) for cell in row) for row in table]
        header_separator = " | ".join(['---'] * len(table[0]))
        return f"{rows[0]}\n{header_separator}\n" + "\n".join(rows[1:])

    def _parse_response(self, response: str) -> Dict:
        """Parse Claude's JSON response."""
        try:
            # Extract JSON from response (Claude might wrap in markdown)
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()

            return json.loads(response)
        except json.JSONDecodeError:
            return {'raw_response': response}
```

---

### **Phase 5: Project Orchestrator (Days 5-6)**

#### 5.1 Main Orchestration Logic

```python
# src/agent/ProjectAnalyzer.py
from pathlib import Path
from typing import List, Dict
from .PdfExtractor import PdfExtractor
from .SpecificationParser import SpecificationParser
from .ClaudeAgent import ClaudeAgent
from models.Component import Component, Project
from utils.formatters import BOMFormatter, ReportFormatter

class ProjectAnalyzer:
    """Main orchestrator for component analysis."""

    def __init__(self, pdf_folder: str, api_key: str):
        self.pdf_folder = Path(pdf_folder)
        self.pdf_extractor = PdfExtractor
        self.spec_parser = SpecificationParser()
        self.claude_agent = ClaudeAgent(api_key)
        self.components = []

    def analyze_project(self, project_name: str) -> Project:
        """Analyze all PDFs and generate project report."""
        print(f"🔍 Analyzing project: {project_name}")

        # Step 1: Process all PDFs
        pdf_files = list(self.pdf_folder.glob('*.pdf'))
        print(f"📄 Found {len(pdf_files)} PDF files")

        for pdf_file in pdf_files:
            self._process_pdf(pdf_file)

        # Step 2: Analyze compatibility
        compatibility = self.claude_agent.analyze_compatibility(
            [comp.model_dump() for comp in self.components]
        )

        # Step 3: Calculate power budget
        power_budget = self._calculate_power_budget()

        # Step 4: Identify missing components
        missing = self._identify_missing_components()

        return Project(
            name=project_name,
            components=self.components,
            total_power_budget=power_budget,
            compatibility_issues=compatibility.get('issues', []),
            missing_components=missing
        )

    def _process_pdf(self, pdf_path: Path):
        """Process a single PDF file."""
        print(f"  Processing: {pdf_path.name}")

        extractor = self.pdf_extractor(str(pdf_path))
        content = extractor.extract_all()

        # Combine all text
        full_text = "\n".join([p['text'] for p in content['text']])

        # Use Claude for intelligent extraction
        component_data = self.claude_agent.extract_component_specs(
            full_text,
            content['tables']
        )

        # Create Component objects
        if isinstance(component_data, list):
            for comp in component_data:
                self.components.append(self._create_component(comp, pdf_path.name))
        elif isinstance(component_data, dict):
            self.components.append(self._create_component(component_data, pdf_path.name))

    def _create_component(self, data: Dict, source_doc: str) -> Component:
        """Create Component object from extracted data."""
        # Use spec parser for standardization
        power_spec = self.spec_parser.parse_power_specs(str(data))
        interface_spec = self.spec_parser.parse_interfaces(str(data))

        return Component(
            name=data.get('name', 'Unknown'),
            component_type=data.get('type', 'unknown'),
            manufacturer=data.get('manufacturer'),
            part_number=data.get('part_number'),
            power=power_spec,
            interfaces=interface_spec,
            specific_specs=data.get('specs', {}),
            source_document=source_doc
        )

    def _calculate_power_budget(self) -> Dict[str, float]:
        """Calculate total power requirements."""
        total_current = 0.0
        total_power = 0.0

        for comp in self.components:
            # Extract numeric values and sum
            if comp.power.current_rating:
                # Parse "2.5A" -> 2.5
                current_str = comp.power.current_rating.replace('A', '').replace('mA', '')
                try:
                    current = float(current_str)
                    if 'mA' in comp.power.current_rating:
                        current /= 1000
                    total_current += current
                except ValueError:
                    pass

        return {
            'total_current_a': round(total_current, 2),
            'estimated_power_w': round(total_current * 12, 2)  # Assume 12V nominal
        }

    def _identify_missing_components(self) -> List[str]:
        """Identify potentially missing components."""
        missing = []
        component_types = [c.component_type for c in self.components]

        # Check for essential drone components
        essentials = {
            'processor': 'Flight controller or microcontroller',
            'motor': 'Motors for propulsion',
            'esc': 'Electronic speed controllers',
            'battery': 'Power source',
            'radio': 'Remote control receiver'
        }

        for comp_type, description in essentials.items():
            if comp_type not in component_types:
                missing.append(f"{description} ({comp_type})")

        return missing
```

---

### **Phase 6: CLI Interface (Days 6-7)**

#### 6.1 Command-Line Interface

```python
# main.py
import click
from pathlib import Path
from dotenv import load_dotenv
import os
from src.agent.ProjectAnalyzer import ProjectAnalyzer
from src.utils.formatters import BOMFormatter, ReportFormatter

load_dotenv()

@click.command()
@click.option(
    '--pdf-folder',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help='Path to folder containing PDF specification files'
)
@click.option(
    '--project-name',
    type=str,
    default='Drone Project',
    help='Name of the project'
)
@click.option(
    '--output',
    type=click.Path(file_okay=False, dir_okay=True),
    default='./output',
    help='Output directory for reports'
)
@click.option(
    '--format',
    type=click.Choice(['all', 'bom', 'report', 'power']),
    default='all',
    help='Output format'
)
def analyze(pdf_folder, project_name, output, format):
    """Analyze component specifications from PDF datasheets."""

    # Get API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        click.echo("❌ Error: ANTHROPIC_API_KEY not found in environment", err=True)
        return 1

    click.echo(f"\n🚁 Component Specification Analyzer")
    click.echo(f"{'='*50}\n")

    # Create analyzer
    analyzer = ProjectAnalyzer(pdf_folder, api_key)

    # Analyze project
    try:
        project = analyzer.analyze_project(project_name)

        # Create output directory
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate reports
        if format in ['all', 'bom']:
            bom_path = output_path / 'bill_of_materials.csv'
            BOMFormatter.export_csv(project, bom_path)
            click.echo(f"✅ BOM saved to: {bom_path}")

        if format in ['all', 'report']:
            report_path = output_path / 'project_report.md'
            ReportFormatter.export_markdown(project, report_path)
            click.echo(f"✅ Report saved to: {report_path}")

        if format in ['all', 'power']:
            click.echo(f"\n⚡ Power Budget Summary:")
            click.echo(f"  Total Current: {project.total_power_budget['total_current_a']}A")
            click.echo(f"  Estimated Power: {project.total_power_budget['estimated_power_w']}W")

        # Display summary
        click.echo(f"\n📊 Analysis Summary:")
        click.echo(f"  Components Found: {len(project.components)}")
        click.echo(f"  Compatibility Issues: {len(project.compatibility_issues)}")
        click.echo(f"  Missing Components: {len(project.missing_components)}")

        if project.compatibility_issues:
            click.echo(f"\n⚠️  Compatibility Warnings:")
            for issue in project.compatibility_issues:
                click.echo(f"  - {issue}")

        if project.missing_components:
            click.echo(f"\n❓ Potentially Missing:")
            for missing in project.missing_components:
                click.echo(f"  - {missing}")

        click.echo(f"\n✨ Analysis complete!\n")

    except Exception as e:
        click.echo(f"❌ Error during analysis: {str(e)}", err=True)
        return 1

if __name__ == '__main__':
    analyze()
```

---

### **Phase 7: Output Formatters (Day 7)**

#### 7.1 Report Generation

```python
# src/utils/formatters.py
import csv
from pathlib import Path
from typing import List
from models.Project import Project
import pandas as pd

class BOMFormatter:
    """Format Bill of Materials."""

    @staticmethod
    def export_csv(project: Project, output_path: Path):
        """Export BOM as CSV."""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Component Name',
                'Type',
                'Manufacturer',
                'Part Number',
                'Voltage',
                'Current',
                'Power',
                'Source Document'
            ])

            for comp in project.components:
                writer.writerow([
                    comp.name,
                    comp.component_type,
                    comp.manufacturer or 'N/A',
                    comp.part_number or 'N/A',
                    comp.power.voltage_input or 'N/A',
                    comp.power.current_rating or 'N/A',
                    comp.power.power_consumption or 'N/A',
                    comp.source_document
                ])

class ReportFormatter:
    """Format detailed project reports."""

    @staticmethod
    def export_markdown(project: Project, output_path: Path):
        """Export full project report as Markdown."""
        report = f"""# {project.name} - Component Analysis Report

## Overview
- **Total Components**: {len(project.components)}
- **Total Current Draw**: {project.total_power_budget['total_current_a']}A
- **Estimated Power**: {project.total_power_budget['estimated_power_w']}W

## Bill of Materials

| Component | Type | Voltage | Current | Power | Source |
|-----------|------|---------|---------|-------|--------|
"""

        for comp in project.components:
            report += f"| {comp.name} | {comp.component_type} | "
            report += f"{comp.power.voltage_input or 'N/A'} | "
            report += f"{comp.power.current_rating or 'N/A'} | "
            report += f"{comp.power.power_consumption or 'N/A'} | "
            report += f"{comp.source_document} |\n"

        # Component breakdown by type
        report += "\n## Components by Type\n\n"
        types = {}
        for comp in project.components:
            types.setdefault(comp.component_type, []).append(comp.name)

        for comp_type, names in types.items():
            report += f"### {comp_type.title()}\n"
            for name in names:
                report += f"- {name}\n"
            report += "\n"

        # Compatibility issues
        if project.compatibility_issues:
            report += "## ⚠️ Compatibility Issues\n\n"
            for issue in project.compatibility_issues:
                report += f"- {issue}\n"
            report += "\n"

        # Missing components
        if project.missing_components:
            report += "## ❓ Potentially Missing Components\n\n"
            for missing in project.missing_components:
                report += f"- {missing}\n"
            report += "\n"

        # Power analysis
        report += f"""## Power Budget Analysis

**Total Current Draw**: {project.total_power_budget['total_current_a']}A
**Estimated Power Consumption**: {project.total_power_budget['estimated_power_w']}W

### Recommended Battery
- LiPo 3S (11.1V) or 4S (14.8V)
- Minimum capacity: {int(project.total_power_budget['total_current_a'] * 1000 * 0.2)}mAh (for 12min flight)
- Recommended: {int(project.total_power_budget['total_current_a'] * 1000 * 0.5)}mAh (for 30min flight)

---
*Generated by Component Specification Analyzer*
"""

        output_path.write_text(report)
```

---

## Prompt Templates

### Component Extraction Prompt

```txt
# prompts/component_extraction.txt

You are analyzing technical specification documents for hardware components used in projects like drones, robots, or electronics prototypes.

Extract ALL component specifications from the following text and tables. Focus on:

**1. Component Identification:**
- Name and model number
- Manufacturer
- Component type (motor, sensor, camera, processor, battery, ESC, etc.)

**2. Power Specifications:**
- Voltage (input/output ranges)
- Current rating or consumption
- Power consumption in Watts/milliwatts

**3. Communication Interfaces:**
- Count of UART, I2C, SPI, CAN, USB ports
- Protocol support
- Voltage levels (3.3V, 5V)

**4. Component-Specific Specs:**
- **Motors**: KV rating, max current, operating voltage
- **Cameras**: Resolution, FPS, interface type, FOV
- **Processors**: Clock speed, RAM, Flash, architecture
- **Sensors**: Type (IMU, GPS, etc.), range, accuracy, update rate
- **Batteries**: Voltage, capacity (mAh), cell count, chemistry
- **ESCs**: Current rating, supported protocols
- **Radio**: Frequency, channel count, range

**Text:**
{text}

**Tables:**
{tables}

Return a JSON array of components in this format:
```json
[
  {{
    "name": "Component Name",
    "type": "motor|sensor|camera|processor|battery|esc|radio|other",
    "manufacturer": "Manufacturer name",
    "part_number": "Part/model number",
    "power": {{
      "voltage_input": "5V",
      "current_rating": "2A",
      "power_consumption": "10W"
    }},
    "interfaces": {{
      "uart": 3,
      "i2c": 2,
      "spi": 1
    }},
    "specs": {{
      "key": "value",
      "resolution": "1920x1080",
      "kv_rating": "2300KV"
    }}
  }}
]
```

Be thorough - extract EVERY component mentioned. If multiple components are described, return multiple objects.
```

### Compatibility Check Prompt

```txt
# prompts/compatibility_check.txt

Analyze the following components for a hardware project (likely a drone or robot) and identify compatibility issues:

**Components:**
{components}

Check for:

1. **Power Compatibility**
   - Do voltage levels match?
   - Is total current draw reasonable for a single battery?
   - Are there components with conflicting voltage requirements?

2. **Interface Conflicts**
   - Does the processor have enough UART/I2C/SPI ports for all peripherals?
   - Are there duplicate device addresses on I2C?
   - Protocol mismatches?

3. **Physical Constraints**
   - Motor KV rating appropriate for voltage?
   - ESC current rating sufficient for motors?
   - Battery capacity adequate for power draw?

4. **Missing Critical Components**
   - Power regulation (if needed)?
   - Level shifters (3.3V ↔ 5V)?
   - Connectors and wiring?

Return JSON:
```json
{{
  "issues": [
    "Description of compatibility issue",
    "Another issue..."
  ],
  "warnings": [
    "Potential concern...",
  ],
  "recommendations": [
    "Suggested fix or addition..."
  ]
}}
```
```

### Recommendation Prompt

```txt
# prompts/recommendation.txt

Given this component and an identified issue, suggest suitable alternatives:

**Component:**
{component}

**Issue:**
{issue}

Provide 2-3 alternative components that would resolve the issue. For each alternative:
- Name and model
- Why it's better
- Key specifications
- Approximate price range (if known)

Return JSON:
```json
{{
  "alternatives": [
    {{
      "name": "Alternative component name",
      "reason": "Why this solves the issue",
      "specs": {{}},
      "price_range": "$10-20"
    }}
  ]
}}
```
```

---

## Usage Examples

### Basic Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# Run analysis
python main.py --pdf-folder ./data/pdfs --project-name "Quadcopter Drone" --output ./output

# Generate only BOM
python main.py --pdf-folder ./data/pdfs --format bom

# Custom project
python main.py --pdf-folder ~/Documents/drone_specs --project-name "Custom FPV Drone" --output ./reports
```

### Expected Output

```
🚁 Component Specification Analyzer
==================================================

🔍 Analyzing project: Quadcopter Drone
📄 Found 8 PDF files
  Processing: motor_spec.pdf
  Processing: flight_controller.pdf
  Processing: camera.pdf
  Processing: esc.pdf
  Processing: battery.pdf
  Processing: gps.pdf
  Processing: radio_receiver.pdf
  Processing: imu_sensor.pdf

✅ BOM saved to: output/bill_of_materials.csv
✅ Report saved to: output/project_report.md

⚡ Power Budget Summary:
  Total Current: 45.2A
  Estimated Power: 542.4W

📊 Analysis Summary:
  Components Found: 12
  Compatibility Issues: 1
  Missing Components: 0

⚠️  Compatibility Warnings:
  - ESC max current (30A) may be insufficient for motor peak draw (40A)

✨ Analysis complete!
```

---

## Development Workflow

### Day-by-Day Plan

**Days 1-2**: Foundation
- Set up project structure
- Create data models
- Install dependencies
- Basic tests

**Days 2-3**: PDF Processing
- Implement PdfExtractor
- Test on sample datasheets
- Handle edge cases

**Days 3-4**: Spec Parsing
- Build regex patterns
- Test on various formats
- Validate extraction accuracy

**Days 4-5**: Claude Integration
- Implement ClaudeAgent
- Create prompt templates
- Test intelligent extraction

**Days 5-6**: Orchestration
- Build ProjectAnalyzer
- Implement analysis logic
- Power budget calculations

**Days 6-7**: CLI & Output
- Create CLI interface
- Build report formatters
- Final testing

---

## Testing Strategy

### Unit Tests

```python
# tests/test_spec_parser.py
def test_voltage_extraction():
    parser = SpecificationParser()
    text = "Operating voltage: 5V DC"
    result = parser._extract_pattern(text, 'voltage')
    assert result == "5V"

def test_component_type_identification():
    parser = SpecificationParser()
    text = "This brushless motor operates at 2300KV"
    comp_type = parser.identify_component_type(text)
    assert comp_type == "motor"
```

### Integration Tests

```python
# tests/test_integration.py
def test_full_pdf_analysis():
    analyzer = ProjectAnalyzer('tests/sample_pdfs', api_key)
    project = analyzer.analyze_project('Test Drone')
    assert len(project.components) > 0
    assert project.total_power_budget['total_current_a'] > 0
```

---

## Optimization Opportunities

### Performance
- Cache Claude API responses
- Batch process multiple PDFs in parallel
- Optimize regex patterns

### Accuracy
- Fine-tune prompts based on results
- Add domain-specific extraction rules
- Implement confidence scoring

### Features
- Web scraping for component prices
- Integration with parts databases (Digi-Key, Mouser)
- Visual circuit diagram generation
- 3D model compatibility checking

---

## Success Metrics

**Accuracy:**
- Component extraction: >90%
- Specification extraction: >85%
- Compatibility detection: >95%

**Performance:**
- Process 10-page PDF: <30 seconds
- Full project analysis: <5 minutes
- API cost: <$0.50 per project

---

## Next Steps

1. **Start with a minimal prototype:**
   - Simple PDF text extraction
   - Basic Claude integration
   - Single component extraction

2. **Validate approach:**
   - Test on 3-5 real datasheets
   - Check extraction accuracy
   - Iterate on prompts

3. **Build incrementally:**
   - Add features one at a time
   - Test each component
   - Maintain working state

4. **Scale up:**
   - Process full project folders
   - Add report generation
   - Polish CLI interface

---

**Ready to start building!** 🚀

*Last Updated: 2025-11-25*
