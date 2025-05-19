"""Water Quality Analysis Workflow Module (Prompt Chaining).

This module demonstrates the prompt chaining pattern applied to water quality analysis,
sequentially processing water sample data through multiple analysis steps.
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


class WaterQualityState(TypedDict):
    """Type definition for the water quality analysis state."""
    sample_data: Dict[str, float]  # Raw water quality parameters
    initial_analysis: str          # Basic assessment of water quality
    treatment_recommendations: str  # Recommended treatment approaches
    compliance_evaluation: str     # Regulatory compliance assessment
    final_report: str              # Comprehensive water quality report


class WaterQualityWorkflow:
    """
    Implements the prompt chaining pattern for water quality analysis.

    This class demonstrates how to break down complex water quality assessment into
    sequential steps, with each step building on the previous analysis. It includes
    quality gates to ensure proper analysis progression.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the WaterQualityWorkflow with specified model.

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
        Builds the sequential workflow for water quality analysis.

        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        workflow = StateGraph(WaterQualityState)

        # Add nodes for each analysis step
        workflow.add_node("analyze_parameters", self.analyze_parameters)
        workflow.add_node("recommend_treatment", self.recommend_treatment)
        workflow.add_node("evaluate_compliance", self.evaluate_compliance)
        workflow.add_node("generate_report", self.generate_report)

        # Add edges to connect nodes in sequence with quality gates
        workflow.add_edge(START, "analyze_parameters")
        workflow.add_conditional_edges(
            "analyze_parameters",
            self.check_analysis_quality,
            {"Pass": "recommend_treatment", "Fail": END}
        )
        workflow.add_edge("recommend_treatment", "evaluate_compliance")
        workflow.add_edge("evaluate_compliance", "generate_report")
        workflow.add_edge("generate_report", END)

        # Compile the workflow
        return workflow.compile()

    def analyze_parameters(self, state: WaterQualityState) -> Dict[str, str]:
        """
        First analysis step: Assess basic water quality parameters.

        Args:
            state: Current workflow state containing sample data

        Returns:
            Dictionary with initial analysis to be added to the state
        """
        # Format the sample data for the LLM
        parameters_text = "\n".join(
            [f"- {param}: {value}" for param, value in state['sample_data'].items()])

        prompt = f"""Analyze the following water quality parameters and provide an initial assessment:

{parameters_text}

Consider potential contaminants, general water quality, and any immediate concerns.
Provide a detailed analysis of what these parameters indicate about the water sample.
"""

        msg = self.llm.invoke(prompt)
        return {"initial_analysis": msg.content}

    def recommend_treatment(self, state: WaterQualityState) -> Dict[str, str]:
        """
        Second analysis step: Recommend appropriate water treatment methods.

        Args:
            state: Current workflow state containing initial analysis

        Returns:
            Dictionary with treatment recommendations to be added to the state
        """
        prompt = f"""Based on the following water quality analysis, recommend appropriate treatment methods:

WATER QUALITY ANALYSIS:
{state['initial_analysis']}

SAMPLE DATA:
{state['sample_data']}

Provide specific treatment recommendations including:
1. Primary treatment methods
2. Chemical treatments if necessary
3. Filtration requirements
4. Disinfection approaches
5. Any specialized treatments for specific contaminants
"""

        msg = self.llm.invoke(prompt)
        return {"treatment_recommendations": msg.content}

    def evaluate_compliance(self, state: WaterQualityState) -> Dict[str, str]:
        """
        Third analysis step: Evaluate regulatory compliance of the water sample.

        Args:
            state: Current workflow state containing treatment recommendations

        Returns:
            Dictionary with compliance evaluation to be added to the state
        """
        prompt = f"""Evaluate the regulatory compliance of this water sample based on the following information:

WATER QUALITY ANALYSIS:
{state['initial_analysis']}

SAMPLE DATA:
{state['sample_data']}

RECOMMENDED TREATMENTS:
{state['treatment_recommendations']}

Assess compliance with:
1. EPA Safe Drinking Water Act standards
2. State-level water quality regulations
3. Any potential compliance issues
4. Required reporting or monitoring
5. Risk management considerations
"""

        msg = self.llm.invoke(prompt)
        return {"compliance_evaluation": msg.content}

    def generate_report(self, state: WaterQualityState) -> Dict[str, str]:
        """
        Final analysis step: Generate comprehensive water quality report.

        Args:
            state: Current workflow state containing all previous analyses

        Returns:
            Dictionary with final report to be added to the state
        """
        prompt = f"""Create a comprehensive water quality report based on all the following analyses:

SAMPLE DATA:
{state['sample_data']}

INITIAL ANALYSIS:
{state['initial_analysis']}

TREATMENT RECOMMENDATIONS:
{state['treatment_recommendations']}

COMPLIANCE EVALUATION:
{state['compliance_evaluation']}

The report should include:
1. Executive summary
2. Detailed findings
3. Treatment recommendations with rationale
4. Compliance status and any required actions
5. Next steps and monitoring recommendations
"""

        msg = self.llm.invoke(prompt)
        return {"final_report": msg.content}

    def check_analysis_quality(self, state: WaterQualityState) -> str:
        """
        Quality gate to verify if the initial analysis is sufficient.

        Args:
            state: Current workflow state containing the initial analysis

        Returns:
            "Pass" if the analysis meets quality standards, "Fail" otherwise
        """
        # Check if the analysis covers key water quality aspects
        required_topics = ["pH", "turbidity",
                           "dissolved solids", "contaminant"]
        analysis_text = state["initial_analysis"].lower()

        # Count how many required topics are mentioned
        topics_covered = sum(
            1 for topic in required_topics if topic in analysis_text)

        # Pass if at least 3 of the required topics are covered
        if topics_covered >= 3 and len(analysis_text) > 200:
            return "Pass"
        return "Fail"

    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.

        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())

    def run(self, sample_data: Dict[str, float]) -> WaterQualityState:
        """
        Execute the water quality analysis workflow with the given sample data.

        Args:
            sample_data: Dictionary of water quality parameters and their values

        Returns:
            The final state containing all analyses and the final report
        """
        state = self.workflow.invoke({"sample_data": sample_data})
        return state


def example_usage():
    """Demonstrate the usage of WaterQualityWorkflow."""

    # Example water quality parameters
    sample_data = {
        "pH": 7.2,
        "turbidity": 1.8,  # NTU
        "total_dissolved_solids": 280,  # mg/L
        "dissolved_oxygen": 7.5,  # mg/L
        "temperature": 22.3,  # °C
        "chlorine": 0.7,  # mg/L
        "lead": 0.008,  # mg/L
        "nitrates": 3.2,  # mg/L
        "phosphates": 0.15,  # mg/L
        "total_coliform": 2,  # CFU/100mL
        "e_coli": 0,  # CFU/100mL
    }

    # Create the water quality workflow
    water_quality_workflow = WaterQualityWorkflow()

    # Visualize the workflow (useful in notebooks)
    # display(water_quality_workflow.visualize())

    # Run the workflow
    result = water_quality_workflow.run(sample_data)

    # Print final report
    print("WATER QUALITY FINAL REPORT:")
    print("===========================")
    print(result["final_report"])


if __name__ == "__main__":
    example_usage()
