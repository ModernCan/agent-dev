# -*- coding: utf-8 -*-
"""Prompt Chaining Module.

This module demonstrates the prompt chaining pattern where tasks are
decomposed into sequential LLM calls, with each step building on the output
of the previous one.
"""

import os
from typing import TypedDict, Dict, Any, Optional, Callable
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from IPython.display import Image

# Load environment variables
load_dotenv()

# Define the state type for type checking


class JokeState(TypedDict):
    """Type definition for the joke generation state."""
    topic: str
    joke: str
    improved_joke: str
    final_joke: str


class PromptChain:
    """
    Implements the prompt chaining pattern where multiple LLM calls are chained
    sequentially, with each step building on the previous one.

    This class demonstrates how to break down a complex task (joke creation and refinement)
    into a sequence of simpler LLM calls with quality checks between steps.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the PromptChain with specified model.

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
        Builds the sequential workflow for joke creation and refinement.

        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        workflow = StateGraph(JokeState)

        # Add nodes
        workflow.add_node("generate_joke", self.generate_joke)
        workflow.add_node("improve_joke", self.improve_joke)
        workflow.add_node("polish_joke", self.polish_joke)

        # Add edges to connect nodes in sequence with quality check
        workflow.add_edge(START, "generate_joke")
        workflow.add_conditional_edges(
            "generate_joke",
            self.check_punchline,
            {"Pass": "improve_joke", "Fail": END}
        )
        workflow.add_edge("improve_joke", "polish_joke")
        workflow.add_edge("polish_joke", END)

        # Compile the workflow
        return workflow.compile()

    def generate_joke(self, state: JokeState) -> Dict[str, str]:
        """
        First LLM call to generate an initial joke.

        Args:
            state: The current workflow state containing the topic

        Returns:
            Dictionary with the generated joke to be added to the state
        """
        msg = self.llm.invoke(f"Write a short joke about {state['topic']}")
        return {"joke": msg.content}

    def improve_joke(self, state: JokeState) -> Dict[str, str]:
        """
        Second LLM call to improve the joke with wordplay.

        Args:
            state: The current workflow state containing the initial joke

        Returns:
            Dictionary with the improved joke to be added to the state
        """
        msg = self.llm.invoke(
            f"Make this joke funnier by adding wordplay: {state['joke']}")
        return {"improved_joke": msg.content}

    def polish_joke(self, state: JokeState) -> Dict[str, str]:
        """
        Third LLM call to add a final twist to the joke.

        Args:
            state: The current workflow state containing the improved joke

        Returns:
            Dictionary with the final polished joke to be added to the state
        """
        msg = self.llm.invoke(
            f"Add a surprising twist to this joke: {state['improved_joke']}")
        return {"final_joke": msg.content}

    def check_punchline(self, state: JokeState) -> str:
        """
        Quality check to verify if the joke has a punchline.

        This gate function determines whether the workflow should proceed
        to joke improvement or terminate if the joke isn't good enough.

        Args:
            state: The current workflow state containing the joke to check

        Returns:
            "Pass" if the joke has a punchline, "Fail" otherwise
        """
        # Simple check - does the joke contain "?" or "!"
        if "?" in state["joke"] or "!" in state["joke"]:
            return "Pass"
        return "Fail"

    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.

        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())

    def run(self, topic: str) -> JokeState:
        """
        Execute the prompt chain workflow with the given topic.

        Args:
            topic: The subject for joke creation

        Returns:
            The final state containing all intermediate and final outputs
        """
        state = self.workflow.invoke({"topic": topic})
        return state


def example_usage():
    """Demonstrate the usage of PromptChain."""

    # Create the prompt chain
    joke_chain = PromptChain()

    # Visualize the workflow (useful in notebooks)
    # display(joke_chain.visualize())

    # Run the workflow
    result = joke_chain.run("cats")

    # Print results
    print("Initial joke:")
    print(result["joke"])
    print("\n--- --- ---\n")

    if "improved_joke" in result:
        print("Improved joke:")
        print(result["improved_joke"])
        print("\n--- --- ---\n")

        print("Final joke:")
        print(result["final_joke"])
    else:
        print("Joke failed quality gate - no punchline detected!")


if __name__ == "__main__":
    example_usage()
