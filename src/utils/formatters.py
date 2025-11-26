import csv
from pathlib import Path
from typing import List
import sys
sys.path.append('/Users/anujjain/drone-component-analyzer')
from src.models.Project import Project
from src.models.Component import Component
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BOMFormatter:
    """Format Bill of Materials for export."""

    @staticmethod
    def export_csv(project: Project, output_path: Path):
        """
        Export BOM as CSV file.

        Args:
            project: Project object containing components
            output_path: Path to save CSV file
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    'Component Name',
                    'Type',
                    'Manufacturer',
                    'Part Number',
                    'Voltage Input',
                    'Voltage Output',
                    'Current Rating',
                    'Power Consumption',
                    'Capacity',
                    'UART',
                    'I2C',
                    'SPI',
                    'USB',
                    'Source Document',
                    'Page'
                ])

                # Write component rows
                for comp in project.components:
                    writer.writerow([
                        comp.name,
                        comp.component_type,
                        comp.manufacturer or 'N/A',
                        comp.part_number or 'N/A',
                        comp.power.voltage_input or 'N/A',
                        comp.power.voltage_output or 'N/A',
                        comp.power.current_rating or 'N/A',
                        comp.power.power_consumption or 'N/A',
                        comp.power.capacity or 'N/A',
                        comp.interfaces.uart_count,
                        comp.interfaces.i2c_count,
                        comp.interfaces.spi_count,
                        comp.interfaces.usb_count,
                        comp.source_document,
                        comp.page_number or 'N/A'
                    ])

            logger.info(f"BOM exported to: {output_path}")

        except Exception as e:
            logger.error(f"Error exporting BOM: {str(e)}")
            raise

    @staticmethod
    def format_table(project: Project) -> str:
        """
        Format BOM as a text table for display.

        Args:
            project: Project object containing components

        Returns:
            Formatted table string
        """
        if not project.components:
            return "No components found."

        # Create header
        header = f"{'Component':<30} {'Type':<15} {'Voltage':<10} {'Current':<10} {'Source':<20}"
        separator = '-' * 85

        rows = [header, separator]

        # Add component rows
        for comp in project.components:
            voltage = comp.power.voltage_input or 'N/A'
            current = comp.power.current_rating or 'N/A'
            name = comp.name[:28] + '..' if len(comp.name) > 30 else comp.name
            comp_type = comp.component_type[:13] + '..' if len(comp.component_type) > 15 else comp.component_type
            source = comp.source_document[:18] + '..' if len(comp.source_document) > 20 else comp.source_document

            row = f"{name:<30} {comp_type:<15} {voltage:<10} {current:<10} {source:<20}"
            rows.append(row)

        return '\n'.join(rows)


class ReportFormatter:
    """Format detailed project reports."""

    @staticmethod
    def export_markdown(project: Project, output_path: Path):
        """
        Export full project report as Markdown.

        Args:
            project: Project object to export
            output_path: Path to save markdown file
        """
        try:
            report = ReportFormatter._generate_markdown(project)
            output_path.write_text(report, encoding='utf-8')
            logger.info(f"Report exported to: {output_path}")

        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            raise

    @staticmethod
    def _generate_markdown(project: Project) -> str:
        """Generate markdown report content."""

        # Header
        report = f"""# {project.name} - Component Analysis Report

## Overview
- **Total Components**: {len(project.components)}
- **Component Types**: {len(set(c.component_type for c in project.components))}
"""

        # Power budget
        if project.total_power_budget:
            report += f"""- **Total Current Draw**: {project.total_power_budget.get('total_current_a', 'N/A')}A
- **Estimated Power**: {project.total_power_budget.get('estimated_power_w', 'N/A')}W

"""

        # Bill of Materials Table
        report += """## Bill of Materials

| Component | Type | Manufacturer | Voltage | Current | Power | Source |
|-----------|------|--------------|---------|---------|-------|--------|
"""

        for comp in project.components:
            report += f"| {comp.name} | {comp.component_type} | "
            report += f"{comp.manufacturer or 'N/A'} | "
            report += f"{comp.power.voltage_input or 'N/A'} | "
            report += f"{comp.power.current_rating or 'N/A'} | "
            report += f"{comp.power.power_consumption or 'N/A'} | "
            report += f"{comp.source_document} |\n"

        # Component breakdown by type
        report += "\n## Components by Type\n\n"
        types = {}
        for comp in project.components:
            types.setdefault(comp.component_type, []).append(comp)

        for comp_type, components in sorted(types.items()):
            report += f"### {comp_type.title()}\n\n"
            for comp in components:
                report += f"- **{comp.name}**"
                if comp.manufacturer:
                    report += f" ({comp.manufacturer})"
                if comp.part_number:
                    report += f" - Part #: {comp.part_number}"
                report += "\n"

                # Add key specs
                if comp.power.voltage_input:
                    report += f"  - Voltage: {comp.power.voltage_input}\n"
                if comp.power.current_rating:
                    report += f"  - Current: {comp.power.current_rating}\n"

                # Add specific specs
                if comp.specific_specs:
                    for key, value in comp.specific_specs.items():
                        report += f"  - {key.replace('_', ' ').title()}: {value}\n"

                report += "\n"

        # Compatibility issues
        if project.compatibility_issues:
            report += "## ⚠️ Compatibility Issues\n\n"
            for issue in project.compatibility_issues:
                report += f"- {issue}\n"
            report += "\n"

        # Warnings
        if project.warnings:
            report += "## ⚡ Warnings\n\n"
            for warning in project.warnings:
                report += f"- {warning}\n"
            report += "\n"

        # Missing components
        if project.missing_components:
            report += "## ❓ Potentially Missing Components\n\n"
            for missing in project.missing_components:
                report += f"- {missing}\n"
            report += "\n"

        # Recommendations
        if project.recommendations:
            report += "## 💡 Recommendations\n\n"
            for rec in project.recommendations:
                report += f"- {rec}\n"
            report += "\n"

        # Power budget analysis
        if project.total_power_budget:
            report += f"""## Power Budget Analysis

**Total Current Draw**: {project.total_power_budget.get('total_current_a', 'N/A')}A
**Estimated Power Consumption**: {project.total_power_budget.get('estimated_power_w', 'N/A')}W

### Battery Recommendations
"""
            total_current = project.total_power_budget.get('total_current_a', 0)
            if total_current > 0:
                # Calculate battery recommendations
                min_capacity = int(total_current * 1000 * 0.2)  # 12 min flight
                rec_capacity = int(total_current * 1000 * 0.5)  # 30 min flight

                report += f"""
For a drone/robotic project, consider:
- **Battery Type**: LiPo 3S (11.1V) or 4S (14.8V)
- **Minimum Capacity**: {min_capacity}mAh (for ~12 minutes runtime)
- **Recommended Capacity**: {rec_capacity}mAh (for ~30 minutes runtime)
- **C-Rating**: At least 20C for peak current handling

⚠️ **Safety Note**: Always use a proper battery charger and LiPo safety bag.
"""

        # Footer
        report += f"""
---
*Generated by Component Specification Analyzer*
*Project: {project.name}*
"""

        return report

    @staticmethod
    def format_summary(project: Project) -> str:
        """
        Format a brief summary for console output.

        Args:
            project: Project object to summarize

        Returns:
            Formatted summary string
        """
        summary = f"\n{'='*60}\n"
        summary += f"  {project.name} - Analysis Summary\n"
        summary += f"{'='*60}\n\n"
        summary += f"Components Found: {len(project.components)}\n"

        if project.total_power_budget:
            summary += f"Total Current: {project.total_power_budget.get('total_current_a', 'N/A')}A\n"
            summary += f"Estimated Power: {project.total_power_budget.get('estimated_power_w', 'N/A')}W\n"

        summary += f"\nCompatibility Issues: {len(project.compatibility_issues)}\n"
        summary += f"Warnings: {len(project.warnings)}\n"
        summary += f"Missing Components: {len(project.missing_components)}\n"

        return summary
