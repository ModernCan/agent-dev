"""Water Quality Analysis Workflow Module (Prompt Chaining).

This module demonstrates the prompt chaining pattern applied to water quality analysis,
sequentially processing water sample data through multiple analysis steps.
"""

import os
from typing import TypedDict, Dict, Any, Optional, List
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display

# Import utility functions
from water_industry.utils import (
    initialize_llm,
    visualize_workflow,
    format_parameters,
    save_report_as_pdf,
    generate_report_chart
)

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
        api_key: Optional[str] = None,
        debug_mode: bool = False
    ):
        """
        Initialize the WaterQualityWorkflow with specified model.

        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
            debug_mode: Enable detailed logging for debugging
        """
        # Use the utility function to initialize the LLM
        self.llm = initialize_llm(model_name, api_key)
        self.debug_mode = debug_mode
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
        # Use the utility function to format parameters
        parameters_text = format_parameters(state['sample_data'])

        prompt = f"""Analyze the following water quality parameters and provide an initial assessment:

{parameters_text}

Provide a detailed analysis that must include specific assessments of:
1. pH levels and what they indicate about the water
2. Turbidity measurements and their implications
3. Total dissolved solids (TDS) concentration and significance
4. Potential contaminants indicated by these parameters, including any concerning levels

Also consider other parameters like dissolved oxygen, temperature, and any specific substances like chlorine, 
nitrates, phosphates, lead, or microbial indicators. 

Your analysis should be comprehensive, technically precise, and include specific references to each key parameter.
"""

        msg = self.llm.invoke(prompt)
        analysis = msg.content

        if self.debug_mode:
            print("INITIAL ANALYSIS COMPLETED:")
            print(f"Character count: {len(analysis)}")
            print("First 100 characters: " + analysis[:100] + "...")

        return {"initial_analysis": analysis}

    def recommend_treatment(self, state: WaterQualityState) -> Dict[str, str]:
        """
        Second analysis step: Recommend appropriate water treatment methods.

        Args:
            state: Current workflow state containing initial analysis

        Returns:
            Dictionary with treatment recommendations to be added to the state
        """
        # Format parameters using the utility function
        parameters_text = format_parameters(state['sample_data'])

        prompt = f"""Based on the following water quality analysis, recommend appropriate treatment methods:

WATER QUALITY ANALYSIS:
{state['initial_analysis']}

SAMPLE DATA:
{parameters_text}

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
        # Format parameters using the utility function
        parameters_text = format_parameters(state['sample_data'])

        prompt = f"""Evaluate the regulatory compliance of this water sample based on the following information:

WATER QUALITY ANALYSIS:
{state['initial_analysis']}

SAMPLE DATA:
{parameters_text}

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
        # Format parameters using the utility function
        parameters_text = format_parameters(state['sample_data'])

        prompt = f"""Create a comprehensive water quality report based on all the following analyses:

SAMPLE DATA:
{parameters_text}

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
        # Define topics with multiple terms that could be used to describe them
        required_topics = {
            "pH": ["ph", "acidity", "alkalinity", "acidic", "alkaline"],
            "turbidity": ["turbid", "clarity", "clear", "cloudy", "cloudiness", "ntu"],
            "dissolved solids": ["tds", "dissolved solid", "solids", "mineral content", "conductivity", "ppm"],
            "contaminant": ["contaminant", "pollutant", "impurity", "contamination",
                            "lead", "nitrate", "phosphate", "coliform", "e. coli",
                            "bacteria", "microbial", "toxin", "pathogen"]
        }

        analysis_text = state["initial_analysis"].lower()

        # Count how many required topics are mentioned
        topics_covered = 0
        found_topics = []

        for topic, variations in required_topics.items():
            if any(var in analysis_text for var in variations):
                topics_covered += 1
                found_topics.append(topic)

        min_required_topics = 3
        min_required_length = 200

        # Check if requirements are met
        length_ok = len(analysis_text) >= min_required_length
        topics_ok = topics_covered >= min_required_topics

        if self.debug_mode:
            print(f"\nQUALITY CHECK RESULTS:")
            print(
                f"Topics found ({topics_covered}/{len(required_topics)}): {', '.join(found_topics)}")
            print(
                f"Length check: {len(analysis_text)} characters (minimum: {min_required_length})")
            print(
                f"Topics check: {topics_covered} topics (minimum: {min_required_topics})")
            print(
                f"Overall result: {'Pass' if (length_ok and topics_ok) else 'Fail'}")

            if not length_ok:
                print(
                    f"REASON FOR FAILURE: Analysis too short ({len(analysis_text)} < {min_required_length})")
            if not topics_ok:
                print(
                    f"REASON FOR FAILURE: Too few topics covered ({topics_covered} < {min_required_topics})")
                print(
                    f"Missing topics: {', '.join(set(required_topics.keys()) - set(found_topics))}")

        # Pass if minimum topics are covered and length requirement is met
        if topics_ok and length_ok:
            return "Pass"
        return "Fail"

    def visualize(self) -> None:
        """
        Generate and display a visualization of the workflow graph.
        Uses the utility function to display the graph.
        """
        # Use the utility function to visualize the workflow
        visualize_workflow(self.workflow)

    def _build_direct_workflow(self) -> StateGraph:
        """
        Builds a version of the workflow that bypasses the quality check.
        This is used for testing or demonstration purposes.

        Returns:
            A compiled StateGraph that skips the quality check
        """
        # Build a new workflow
        workflow = StateGraph(WaterQualityState)

        # Add nodes for each analysis step
        workflow.add_node("analyze_parameters", self.analyze_parameters)
        workflow.add_node("recommend_treatment", self.recommend_treatment)
        workflow.add_node("evaluate_compliance", self.evaluate_compliance)
        workflow.add_node("generate_report", self.generate_report)

        # Add edges to connect nodes in sequence WITHOUT quality gates
        workflow.add_edge(START, "analyze_parameters")
        # Direct connection that bypasses quality check
        workflow.add_edge("analyze_parameters", "recommend_treatment")
        workflow.add_edge("recommend_treatment", "evaluate_compliance")
        workflow.add_edge("evaluate_compliance", "generate_report")
        workflow.add_edge("generate_report", END)

        # Compile the workflow
        return workflow.compile()

    def run(self, sample_data: Dict[str, float], bypass_quality_check: bool = False, save_pdf: bool = False, generate_chart: bool = True) -> WaterQualityState:
        """
        Execute the water quality analysis workflow with the given sample data.

        Args:
            sample_data: Dictionary of water quality parameters and their values
            bypass_quality_check: If True, skip the quality check for testing purposes
            save_pdf: If True, save the final report as a PDF
            generate_chart: If True, generate a chart of key parameters (in debug mode)

        Returns:
            The final state containing all analyses and the final report
        """
        if bypass_quality_check:
            if self.debug_mode:
                print(
                    "WARNING: Quality check bypass enabled. This should only be used for testing.")

            # Create a direct workflow that completely bypasses the quality check
            direct_workflow = self._build_direct_workflow()

            # Use the direct workflow
            state = direct_workflow.invoke({"sample_data": sample_data})
        else:
            # Use the normal workflow
            state = self.workflow.invoke({"sample_data": sample_data})

        if self.debug_mode:
            print("\nWORKFLOW COMPLETED")
            print(f"State keys: {list(state.keys())}")
            if 'final_report' not in state:
                print(
                    "NOTE: Final report was not generated. Workflow may have stopped early.")
                if 'initial_analysis' in state:
                    print(
                        "Check the quality gate requirements or use bypass_quality_check=True.")

        # Generate and save a PDF if requested and the report was generated
        if save_pdf and 'final_report' in state:
            try:
                pdf_path = save_report_as_pdf(
                    state['final_report'],
                    f"water_quality_report_{int(state['sample_data'].get('pH', 0) * 10)}.pdf"
                )
                print(f"Report saved as PDF: {pdf_path}")
            except Exception as e:
                print(f"Error saving PDF: {e}")

        # Create a chart for visualization if the final report was generated
        if 'final_report' in state and self.debug_mode and generate_chart:
            try:
                chart = generate_report_chart(
                    {k: v for k, v in sample_data.items()
                     if k in ['pH', 'turbidity', 'total_dissolved_solids', 'chlorine', 'dissolved_oxygen']},
                    chart_type="bar",
                    title="Key Water Quality Parameters"
                )
                display(chart)
                print("Chart generated for key parameters.")
            except Exception as e:
                print(f"Error generating chart: {e}")

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

    # Create the water quality workflow with debug mode enabled
    water_quality_workflow = WaterQualityWorkflow(debug_mode=True)

    print("Workflow visualization:")
    # Uses utility function to display the workflow
    water_quality_workflow.visualize()

    # Run the workflow
    result = water_quality_workflow.run(sample_data)

    # If the workflow stopped early, try again with bypass_quality_check
    if 'final_report' not in result:
        print("\nRetrying with quality check bypass...\n")
        # Don't generate a chart on the first try, only on the retry
        result = water_quality_workflow.run(
            sample_data, bypass_quality_check=True, generate_chart=True)
    else:
        # Only generate a chart if we succeeded on the first try
        if 'final_report' in result:
            try:
                chart = generate_report_chart(
                    {k: v for k, v in sample_data.items()
                     if k in ['pH', 'turbidity', 'total_dissolved_solids', 'chlorine', 'dissolved_oxygen']},
                    chart_type="bar",
                    title="Key Water Quality Parameters"
                )
                display(chart)
                print("Chart generated for key parameters.")
            except Exception as e:
                print(f"Error generating chart: {e}")

    # Print final report
    if 'final_report' in result:
        print("\nWATER QUALITY FINAL REPORT:")
        print("===========================")
        print(result["final_report"])

        # Optionally save as PDF
        # uncomment to save PDF
        # water_quality_workflow.run(sample_data, bypass_quality_check=True, save_pdf=True)


if __name__ == "__main__":
    example_usage()
