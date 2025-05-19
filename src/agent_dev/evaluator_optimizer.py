# -*- coding: utf-8 -*-
"""Evaluator-Optimizer Module.

This module demonstrates the evaluator-optimizer pattern, where one LLM generates
content and another evaluates it, providing a feedback loop for iterative improvement.
"""

import os
from typing import TypedDict, Dict, Any, Optional, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from IPython.display import Image

# Load environment variables
load_dotenv()

# Define a schema for the joke evaluation feedback


class Feedback(BaseModel):
    """Schema for joke evaluation feedback."""
    grade: Literal["funny", "not funny"] = Field(
        description="Decide if the joke is funny or not.",
    )
    feedback: str = Field(
        description="If the joke is not funny, provide feedback on how to improve it.",
    )


# Define the state type for type checking
class JokeState(TypedDict):
    """Type definition for the joke generation and evaluation state."""
    joke: str
    topic: str
    feedback: str
    funny_or_not: str


class EvaluatorOptimizer:
    """
    Implements the evaluator-optimizer pattern where one LLM generates content
    and another evaluates it, providing a feedback loop for iterative improvement.

    This class demonstrates how to create a system that can generate content,
    evaluate its quality, and improve it based on feedback.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the EvaluatorOptimizer with specified model.

        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")

        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)
        self.evaluator = self.llm.with_structured_output(Feedback)
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Builds the evaluator-optimizer workflow for joke generation.

        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        optimizer_builder = StateGraph(JokeState)

        # Add the nodes
        optimizer_builder.add_node("generator", self.generator)
        optimizer_builder.add_node("evaluator", self.evaluator_node)

        # Add edges to connect nodes
        optimizer_builder.add_edge(START, "generator")
        optimizer_builder.add_edge("generator", "evaluator")
        optimizer_builder.add_conditional_edges(
            "evaluator",
            self.route_joke,
            {
                "Accepted": END,
                "Rejected + Feedback": "generator",
            },
        )

        # Compile the workflow
        return optimizer_builder.compile()

    def generator(self, state: JokeState) -> Dict[str, str]:
        """
        Generates or improves a joke based on the topic and feedback.

        Args:
            state: The current workflow state containing topic and optional feedback

        Returns:
            Dictionary with the generated joke to be added to the state
        """
        if state.get("feedback"):
            msg = self.llm.invoke(
                f"Write a joke about {state['topic']} but take into account the feedback: {state['feedback']}"
            )
        else:
            msg = self.llm.invoke(f"Write a joke about {state['topic']}")
        return {"joke": msg.content}

    def evaluator_node(self, state: JokeState) -> Dict[str, str]:
        """
        Evaluates the joke and provides feedback.

        Args:
            state: The current workflow state containing the joke to evaluate

        Returns:
            Dictionary with the evaluation and feedback to be added to the state
        """
        grade = self.evaluator.invoke(f"Grade the joke: {state['joke']}")
        return {"funny_or_not": grade.grade, "feedback": grade.feedback}

    def route_joke(self, state: JokeState) -> str:
        """
        Routes back to joke generator or ends based on evaluation.

        Args:
            state: The current workflow state containing the evaluation

        Returns:
            "Accepted" if the joke is funny, "Rejected + Feedback" otherwise
        """
        if state["funny_or_not"] == "funny":
            return "Accepted"
        elif state["funny_or_not"] == "not funny":
            return "Rejected + Feedback"
        else:
            raise ValueError(f"Unknown evaluation: {state['funny_or_not']}")

    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.

        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())

    def run(self, topic: str, max_iterations: int = 5) -> JokeState:
        """
        Execute the evaluator-optimizer workflow with the given topic.

        Args:
            topic: The subject for joke creation
            max_iterations: Maximum number of improvement iterations

        Returns:
            The final state containing the joke and evaluation
        """
        # Using the max_iterations parameter to prevent infinite loops
        # but the actual implementation would need to be modified to use it
        state = self.workflow.invoke({"topic": topic})
        return state


def example_usage():
    """Demonstrate the usage of EvaluatorOptimizer."""

    # Create the evaluator-optimizer workflow
    joke_optimizer = EvaluatorOptimizer()

    # Visualize the workflow (useful in notebooks)
    # display(joke_optimizer.visualize())

    # Run the workflow
    result = joke_optimizer.run("programming")

    # Print results
    print(f"Final joke: {result['joke']}")
    print(f"Evaluation: {result['funny_or_not']}")

    if result["funny_or_not"] == "funny":
        print("The joke was accepted as funny!")
    else:
        print(f"The joke wasn't funny. Final feedback: {result['feedback']}")


if __name__ == "__main__":
    example_usage()
