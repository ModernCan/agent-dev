# -*- coding: utf-8 -*-
"""Parallelization Module.

This module demonstrates the parallelization pattern, where independent
LLM tasks are executed concurrently, with results combined at the end.
"""

import os
from typing import TypedDict, Dict, Any, Optional, List
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from IPython.display import Image

# Load environment variables
load_dotenv()

# Define the state type for type checking


class CreativeState(TypedDict):
    """Type definition for the creative generation state."""
    topic: str
    joke: str
    story: str
    poem: str
    combined_output: str


class Parallelization:
    """
    Implements the parallelization pattern where multiple independent LLM tasks
    are executed concurrently, with results combined at the end.

    This class demonstrates how to break down a task into independent subtasks 
    that can be run in parallel, improving efficiency.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the Parallelization with specified model.

        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")

        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Builds the parallel workflow for creative content generation.

        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        parallel_builder = StateGraph(CreativeState)

        # Add nodes
        parallel_builder.add_node("generate_joke", self.generate_joke)
        parallel_builder.add_node("generate_story", self.generate_story)
        parallel_builder.add_node("generate_poem", self.generate_poem)
        parallel_builder.add_node("aggregator", self.aggregator)

        # Add edges to connect nodes with parallelization
        parallel_builder.add_edge(START, "generate_joke")
        parallel_builder.add_edge(START, "generate_story")
        parallel_builder.add_edge(START, "generate_poem")
        parallel_builder.add_edge("generate_joke", "aggregator")
        parallel_builder.add_edge("generate_story", "aggregator")
        parallel_builder.add_edge("generate_poem", "aggregator")
        parallel_builder.add_edge("aggregator", END)

        # Compile workflow
        return parallel_builder.compile()

    def generate_joke(self, state: CreativeState) -> Dict[str, str]:
        """
        First parallel LLM call to generate a joke.

        Args:
            state: The current workflow state containing the topic

        Returns:
            Dictionary with the generated joke to be added to the state
        """
        msg = self.llm.invoke(f"Write a joke about {state['topic']}")
        return {"joke": msg.content}

    def generate_story(self, state: CreativeState) -> Dict[str, str]:
        """
        Second parallel LLM call to generate a story.

        Args:
            state: The current workflow state containing the topic

        Returns:
            Dictionary with the generated story to be added to the state
        """
        msg = self.llm.invoke(f"Write a story about {state['topic']}")
        return {"story": msg.content}

    def generate_poem(self, state: CreativeState) -> Dict[str, str]:
        """
        Third parallel LLM call to generate a poem.

        Args:
            state: The current workflow state containing the topic

        Returns:
            Dictionary with the generated poem to be added to the state
        """
        msg = self.llm.invoke(f"Write a poem about {state['topic']}")
        return {"poem": msg.content}

    def aggregator(self, state: CreativeState) -> Dict[str, str]:
        """
        Combines the results from all parallel tasks.

        Args:
            state: The current workflow state containing all generated content

        Returns:
            Dictionary with the combined output to be added to the state
        """
        combined = f"Here's a story, joke, and poem about {state['topic']}!\n\n"
        combined += f"STORY:\n{state['story']}\n\n"
        combined += f"JOKE:\n{state['joke']}\n\n"
        combined += f"POEM:\n{state['poem']}"
        return {"combined_output": combined}

    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.

        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())

    def run(self, topic: str) -> CreativeState:
        """
        Execute the parallel workflow with the given topic.

        Args:
            topic: The subject for content creation

        Returns:
            The final state containing all outputs
        """
        state = self.workflow.invoke({"topic": topic})
        return state


def example_usage():
    """Demonstrate the usage of Parallelization."""

    # Create the parallel workflow
    parallel_workflow = Parallelization()

    # Visualize the workflow (useful in notebooks)
    # display(parallel_workflow.visualize())

    # Run the workflow
    result = parallel_workflow.run("cats")

    # Print results
    print(result["combined_output"])


if __name__ == "__main__":
    example_usage()
