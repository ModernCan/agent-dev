# -*- coding: utf-8 -*-
"""Utilities for agent development.

This module provides common utilities and shared functions for agent development.
"""

import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import json

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph

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


class NodeResult(Dict[str, Any]):
    """
    Typed dictionary for node results in workflow graphs.

    This is a convenience wrapper around Dict[str, Any] to provide
    better type hints and documentation.
    """

    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        """
        Create a dictionary with the provided key-value pairs.

        Args:
            **kwargs: Key-value pairs to include in the result

        Returns:
            A dictionary that can be returned from a workflow node
        """
        return dict(**kwargs)


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


@tool
def print_json(obj: Any) -> str:
    """
    Pretty print an object as JSON. Useful for debugging complex objects.

    Args:
        obj: The object to pretty print

    Returns:
        A formatted JSON string representation of the object
    """
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception as e:
        return f"Error converting to JSON: {e}"


def get_system_prompt(prompt_template: str, **kwargs) -> str:
    """
    Format a system prompt template with the provided arguments.

    Args:
        prompt_template: The template string with {placeholders}
        **kwargs: Values to substitute into the template

    Returns:
        The formatted system prompt
    """
    return prompt_template.format(**kwargs)


class CommonSchemas:
    """
    Collection of commonly used Pydantic schemas for structured outputs.
    """

    class ThoughtActionResult(BaseModel):
        """Schema for Thought-Action-Result pattern."""
        thought: str = Field(
            description="The reasoning process behind the decision")
        action: str = Field(description="The action to take")
        action_input: Optional[Dict[str, Any]] = Field(
            default=None, description="The input parameters for the action"
        )

    class PlanSteps(BaseModel):
        """Schema for planning steps."""
        steps: List[str] = Field(
            description="Sequential steps to accomplish the task")
        reasoning: str = Field(description="The reasoning behind this plan")

    class Evaluation(BaseModel):
        """Schema for evaluating outputs."""
        score: int = Field(description="Score from 1-10", ge=1, le=10)
        strengths: List[str] = Field(description="The strengths of the output")
        weaknesses: List[str] = Field(description="Areas for improvement")
        suggestions: List[str] = Field(
            description="Specific suggestions for improvement")
