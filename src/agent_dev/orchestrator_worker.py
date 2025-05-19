# -*- coding: utf-8 -*-
"""Orchestrator-Worker Module.

This module demonstrates the orchestrator-worker pattern, where a central LLM
plans and delegates tasks to worker LLMs, then synthesizes their results.
"""

import os
import operator
from typing import TypedDict, Dict, Any, Optional, List, Annotated
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from IPython.display import Image, Markdown

# Load environment variables
load_dotenv()

# Define schemas for the report sections


class Section(BaseModel):
    """Schema for an individual report section."""
    name: str = Field(
        description="Name for this section of the report.",
    )
    description: str = Field(
        description="Brief overview of the main topics and concepts to be covered in this section.",
    )


class Sections(BaseModel):
    """Schema for the collection of report sections."""
    sections: List[Section] = Field(
        description="Sections of the report.",
    )


# Define the state types for type checking
class ReportState(TypedDict):
    """Type definition for the report generation state."""
    topic: str  # Report topic
    sections: list[Section]  # List of report sections
    # All workers write to this key in parallel
    completed_sections: Annotated[list, operator.add]
    final_report: str  # Final report


class WorkerState(TypedDict):
    """Type definition for the worker state."""
    section: Section
    completed_sections: Annotated[list, operator.add]


class OrchestratorWorker:
    """
    Implements the orchestrator-worker pattern where a central LLM plans and
    delegates tasks to worker LLMs, then synthesizes their results.

    This class demonstrates how to break down a complex task (report creation),
    delegate sections to workers, and combine their outputs.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the OrchestratorWorker with specified model.

        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")

        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)
        self.planner = self.llm.with_structured_output(Sections)
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Builds the orchestrator-worker workflow.

        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        orchestrator_worker_builder = StateGraph(ReportState)

        # Add the nodes
        orchestrator_worker_builder.add_node("orchestrator", self.orchestrator)
        orchestrator_worker_builder.add_node("worker", self.worker)
        orchestrator_worker_builder.add_node("synthesizer", self.synthesizer)

        # Add edges to connect nodes
        orchestrator_worker_builder.add_edge(START, "orchestrator")
        orchestrator_worker_builder.add_conditional_edges(
            "orchestrator", self.assign_workers, ["worker"]
        )
        orchestrator_worker_builder.add_edge("worker", "synthesizer")
        orchestrator_worker_builder.add_edge("synthesizer", END)

        # Compile the workflow
        return orchestrator_worker_builder.compile()

    def orchestrator(self, state: ReportState) -> Dict[str, List[Section]]:
        """
        The orchestrator that plans the report sections.

        Args:
            state: The current workflow state containing the report topic

        Returns:
            Dictionary with the report sections to be added to the state
        """
        # Generate queries
        report_sections = self.planner.invoke(
            [
                SystemMessage(content="Generate a plan for the report."),
                HumanMessage(
                    content=f"Here is the report topic: {state['topic']}"),
            ]
        )

        return {"sections": report_sections.sections}

    def assign_workers(self, state: ReportState) -> List[Send]:
        """
        Assign workers to each section in the report plan.

        Args:
            state: The current workflow state containing the sections

        Returns:
            List of Send objects to trigger worker tasks
        """
        # Kick off section writing in parallel via Send() API
        return [Send("worker", {"section": s}) for s in state["sections"]]

    def worker(self, state: WorkerState) -> Dict[str, List[str]]:
        """
        A worker that writes a section of the report.

        Args:
            state: The worker state containing the section to write

        Returns:
            Dictionary with the completed section to be added to the state
        """
        # Generate section
        section = self.llm.invoke(
            [
                SystemMessage(content="Write a report section."),
                HumanMessage(
                    content=f"Here is the section name: {state['section'].name} and description: {state['section'].description}"
                ),
            ]
        )

        # Write the updated section to completed sections
        return {"completed_sections": [section.content]}

    def synthesizer(self, state: ReportState) -> Dict[str, str]:
        """
        Synthesize the full report from the completed sections.

        Args:
            state: The current workflow state containing all completed sections

        Returns:
            Dictionary with the final report to be added to the state
        """
        # List of completed sections
        completed_sections = state["completed_sections"]

        # Format completed section to str to use as context for final sections
        completed_report_sections = "\n\n---\n\n".join(completed_sections)

        return {"final_report": completed_report_sections}

    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.

        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())

    def run(self, topic: str) -> ReportState:
        """
        Execute the orchestrator-worker workflow with the given topic.

        Args:
            topic: The report topic

        Returns:
            The final state containing the completed report
        """
        state = self.workflow.invoke({"topic": topic})
        return state


def example_usage():
    """Demonstrate the usage of OrchestratorWorker."""

    # Create the orchestrator-worker workflow
    report_workflow = OrchestratorWorker()

    # Visualize the workflow (useful in notebooks)
    # display(report_workflow.visualize())

    # Run the workflow
    result = report_workflow.run("Create a report on LLM scaling laws")

    # Display the final report
    print("Final Report:\n")
    print(result["final_report"])

    # For Jupyter notebooks
    # display(Markdown(result["final_report"]))


if __name__ == "__main__":
    example_usage()
