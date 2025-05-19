# -*- coding: utf-8 -*-
"""Augmented LLM Module.

This module demonstrates how to enhance LLMs with structured output capabilities and tools,
creating a foundation for more complex agent patterns.
"""

import os
from typing import Optional, List, Dict, Any, Callable
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()


class AugmentedLLM:
    """
    Enhances LLMs with structured output capabilities and tool-binding.

    This class serves as the fundamental building block for agent systems,
    allowing LLMs to produce structured outputs and use tools.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the AugmentedLLM with specified model.

        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")

        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)

    def with_structured_output(self, output_schema: BaseModel) -> "StructuredOutputLLM":
        """
        Augment the LLM with schema for structured output.

        Args:
            output_schema: A Pydantic model defining the expected output structure

        Returns:
            An LLM that will return structured output according to the schema
        """
        return StructuredOutputLLM(self.llm, output_schema)

    def with_tools(self, tools: List[Callable]) -> "ToolAugmentedLLM":
        """
        Augment the LLM with tools.

        Args:
            tools: A list of tool functions to make available to the LLM

        Returns:
            An LLM that can use the provided tools
        """
        return ToolAugmentedLLM(self.llm, tools)

    def invoke(self, prompt: str) -> str:
        """
        Invoke the LLM with a prompt.

        Args:
            prompt: The text prompt to send to the LLM

        Returns:
            The LLM's response text
        """
        response = self.llm.invoke(prompt)
        return response.content


class StructuredOutputLLM:
    """
    LLM that produces output conforming to a specified Pydantic schema.
    """

    def __init__(self, llm: ChatAnthropic, output_schema: BaseModel):
        """
        Initialize the structured output LLM.

        Args:
            llm: The base LLM to use
            output_schema: A Pydantic model defining the expected output structure
        """
        self.llm = llm
        self.output_schema = output_schema
        self.structured_llm = llm.with_structured_output(output_schema)

    def invoke(self, prompt: str | List) -> BaseModel:
        """
        Invoke the LLM to generate structured output.

        Args:
            prompt: A string or list of messages to send to the LLM

        Returns:
            An instance of the Pydantic model with the LLM's structured response
        """
        return self.structured_llm.invoke(prompt)


class ToolAugmentedLLM:
    """
    LLM augmented with tools that it can use to perform actions.
    """

    def __init__(self, llm: ChatAnthropic, tools: List[Callable]):
        """
        Initialize the tool-augmented LLM.

        Args:
            llm: The base LLM to use
            tools: A list of tools the LLM can call
        """
        self.llm = llm
        self.tools = tools
        self.llm_with_tools = llm.bind_tools(tools)

    def invoke(self, prompt: str | List) -> Any:
        """
        Invoke the LLM, allowing it to use tools if necessary.

        Args:
            prompt: A string or list of messages to send to the LLM

        Returns:
            The LLM's response, potentially after using tools
        """
        return self.llm_with_tools.invoke(prompt)


# Example Pydantic model for structured output
class SearchQuery(BaseModel):
    """A schema for search query generation."""
    search_query: str = Field(
        None, description="Query that is optimized for web search.")
    justification: str = Field(
        None, description="Why this query is relevant to the user's request."
    )


# Example tool function
@tool
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers.

    Args:
        a: The first number
        b: The second number

    Returns:
        The product of a and b
    """
    return a * b


def example_usage():
    """Demonstrate the usage of AugmentedLLM."""

    # Create the augmented LLM
    augmented_llm = AugmentedLLM()

    # 1. Example of structured output
    structured_llm = augmented_llm.with_structured_output(SearchQuery)
    output = structured_llm.invoke(
        "How does Calcium CT score relate to high cholesterol?")
    print(f"Generated search query: {output.search_query}")
    print(f"Justification: {output.justification}")

    # 2. Example of tool use
    llm_with_tools = augmented_llm.with_tools([multiply])
    response = llm_with_tools.invoke("What is 2 times 3?")
    print(f"Tool response: {response.content}")

    # If there are tool calls
    if hasattr(response, "tool_calls") and response.tool_calls:
        for call in response.tool_calls:
            print(f"Tool called: {call['name']} with args: {call['args']}")


if __name__ == "__main__":
    example_usage()
