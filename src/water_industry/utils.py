# -*- coding: utf-8 -*-
"""Utility functions for water industry AI patterns.

This module provides common utilities and shared functions for water industry
pattern implementations.
"""

import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import io

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph
from IPython.display import Image

# Load environment variables
load_dotenv()


def initialize_llm(model_name: str = "claude-3-5-sonnet-latest", api_key: Optional[str] = None) -> ChatAnthropic:
    """
    Initialize a Claude model with the specified parameters.

    Args:
        model_name: The name of the Anthropic model to use
        api_key: Optional API key for Anthropic (defaults to env variable)

    Returns:
        Initialized ChatAnthropic instance
    """
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Anthropic API key is required.")

    return ChatAnthropic(model=model_name, api_key=api_key)


def visualize_workflow(graph: StateGraph) -> None:
    """
    Visualize a workflow graph in a Jupyter notebook.

    Args:
        graph: The LangGraph StateGraph to visualize
    """
    try:
        from IPython.display import Image, display
        display(Image(graph.get_graph().draw_mermaid_png()))
    except ImportError:
        print(
            "IPython is required for visualization. Install it with 'pip install ipython'.")
    except Exception as e:
        print(f"Error visualizing graph: {e}")


def format_parameters(parameters: Dict[str, Any]) -> str:
    """
    Format parameter dictionary as a string for use in prompts.

    Args:
        parameters: Dictionary of parameters

    Returns:
        Formatted string representation of parameters
    """
    return "\n".join([f"- {k}: {v}" for k, v in parameters.items()])


def save_report_as_pdf(report: str, filename: str) -> str:
    """
    Save a text report as a PDF file.

    Args:
        report: The report text content
        filename: The output filename

    Returns:
        Path to the saved PDF file
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()

        # Process report text into paragraphs
        paragraphs = []
        for line in report.split('\n'):
            if line.strip():
                if line.startswith('#'):
                    # Handle headers
                    style = styles['Heading1'] if line.startswith('# ') else \
                        styles['Heading2'] if line.startswith('## ') else \
                        styles['Heading3']
                    line = line.lstrip('#').strip()
                    paragraphs.append(Paragraph(line, style))
                    paragraphs.append(Spacer(1, 12))
                else:
                    # Regular paragraph
                    paragraphs.append(Paragraph(line, styles['Normal']))
                    paragraphs.append(Spacer(1, 6))

        # Build the PDF
        doc.build(paragraphs)
        return filename

    except ImportError:
        print("ReportLab is required for PDF generation. Install it with 'pip install reportlab'.")
        # Save as text file instead
        with open(filename.replace('.pdf', '.txt'), 'w') as f:
            f.write(report)
        return filename.replace('.pdf', '.txt')


def load_water_sample_data(filepath: str) -> Dict[str, float]:
    """
    Load water sample data from a CSV or JSON file.

    Args:
        filepath: Path to the data file

    Returns:
        Dictionary of water parameters and values
    """
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
        # Assume first column is parameter name, second is value
        return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

    elif filepath.endswith('.json'):
        with open(filepath, 'r') as f:
            return json.load(f)

    else:
        raise ValueError(f"Unsupported file format: {filepath}")


def generate_report_chart(data: Dict[str, float], chart_type: str = "bar", title: str = "Water Parameters") -> Image:
    """
    Generate a chart for a water industry report.

    Args:
        data: Dictionary of data points
        chart_type: Type of chart ('bar', 'line', or 'pie')
        title: Chart title

    Returns:
        IPython Image object containing the chart
    """
    plt.figure(figsize=(10, 6))

    if chart_type == "bar":
        plt.bar(data.keys(), data.values())
        plt.xticks(rotation=45, ha='right')

    elif chart_type == "line":
        plt.plot(list(data.keys()), list(data.values()), marker='o')
        plt.xticks(rotation=45, ha='right')

    elif chart_type == "pie":
        plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')

    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    plt.title(title)
    plt.tight_layout()

    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Create IPython image
    return Image(data=buf.read())


class WaterIndustryException(Exception):
    """Base exception class for water industry module errors."""
    pass


class DataValidationError(WaterIndustryException):
    """Exception raised for invalid water data."""
    pass


class ModelConfigurationError(WaterIndustryException):
    """Exception raised for model configuration issues."""
    pass


@tool
def water_parameter_lookup(parameter_name: str) -> str:
    """
    Look up information about a water quality parameter.

    Args:
        parameter_name: The name of the water parameter to look up

    Returns:
        Description and regulatory information about the parameter
    """
    parameter_database = {
        "turbidity": {
            "description": "A measure of water clarity and how much light scatters through particles in the water.",
            "units": "NTU (Nephelometric Turbidity Units)",
            "regulatory_limit": "TT (Treatment Technique): 1 NTU maximum, 0.3 NTU 95% of the time for conventional treatment",
            "health_effects": "High turbidity can interfere with disinfection and provide a medium for microbial growth."
        },
        "ph": {
            "description": "A measure of how acidic or basic the water is on a scale of 0-14.",
            "units": "Standard units (SU)",
            "regulatory_limit": "Secondary standard: 6.5-8.5",
            "health_effects": "Extremes can cause irritation, affect treatment efficiency, and potentially dissolve metals from plumbing."
        },
        "chlorine": {
            "description": "A common disinfectant added to water to kill or inactivate harmful organisms.",
            "units": "mg/L",
            "regulatory_limit": "MRDL (Maximum Residual Disinfectant Level): 4.0 mg/L",
            "health_effects": "Higher levels can create taste and odor problems and potentially form disinfection byproducts."
        },
        # Add more parameters as needed
    }

    parameter = parameter_name.lower()
    if parameter in parameter_database:
        info = parameter_database[parameter]
        return f"""
Parameter: {parameter_name.upper()}
Description: {info['description']}
Units: {info['units']}
Regulatory Limit: {info['regulatory_limit']}
Health Effects: {info['health_effects']}
"""
    else:
        return f"Parameter '{parameter_name}' not found in the database."
