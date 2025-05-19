# -*- coding: utf-8 -*-
"""Treatment Process Optimization Module (Evaluator-Optimizer).

This module demonstrates the evaluator-optimizer pattern applied to water treatment
process optimization, using feedback-driven iterative improvements.
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

# Define a schema for the treatment process evaluation


class ProcessEvaluation(BaseModel):
    """Schema for water treatment process evaluation."""
    performance_score: int = Field(
        description="Score from 1-10 rating overall process performance.",
        ge=1,
        le=10
    )
    water_quality_assessment: str = Field(
        description="Assessment of produced water quality relative to targets.",
    )
    efficiency_assessment: str = Field(
        description="Assessment of resource efficiency (energy, chemicals, etc.).",
    )
    optimization_status: Literal["optimized", "needs_improvement"] = Field(
        description="Whether the process is optimized or needs further improvement.",
    )
    improvement_recommendations: str = Field(
        description="Specific recommendations for process improvements.",
    )


# Define the state type for type checking
class OptimizationState(TypedDict):
    """Type definition for the treatment process optimization state."""
    treatment_parameters: Dict[str,
                               Any]     # Current treatment process parameters
    treatment_goals: Dict[str, Any]          # Target goals for optimization
    # Current process configuration description
    process_configuration: str
    evaluation: ProcessEvaluation            # Current process evaluation
    # History of configurations and evaluations
    optimization_history: list
    iteration_count: int                     # Number of optimization iterations
    max_iterations: int                      # Maximum allowed iterations
    final_configuration: str                 # Final optimized process configuration


class TreatmentOptimizer:
    """
    Implements the evaluator-optimizer pattern for water treatment process optimization.

    This class demonstrates how to iteratively improve a water treatment process
    through repeated cycles of evaluation and optimization, using feedback to
    guide improvements until performance targets are achieved.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the TreatmentOptimizer with specified model.

        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")

        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)
        self.evaluator = self.llm.with_structured_output(ProcessEvaluation)
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Builds the evaluator-optimizer workflow for treatment process optimization.

        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        optimization_workflow = StateGraph(OptimizationState)

        # Add the nodes
        optimization_workflow.add_node("initialize", self.initialize)
        optimization_workflow.add_node(
            "evaluate_process", self.evaluate_process)
        optimization_workflow.add_node(
            "optimize_process", self.optimize_process)
        optimization_workflow.add_node("finalize", self.finalize)

        # Add edges to connect nodes
        optimization_workflow.add_edge(START, "initialize")
        optimization_workflow.add_edge("initialize", "evaluate_process")
        optimization_workflow.add_conditional_edges(
            "evaluate_process",
            self.should_continue_optimization,
            {
                "Continue": "optimize_process",
                "Complete": "finalize",
            },
        )
        optimization_workflow.add_edge("optimize_process", "evaluate_process")
        optimization_workflow.add_edge("finalize", END)

        # Compile the workflow
        return optimization_workflow.compile()

    def initialize(self, state: OptimizationState) -> Dict[str, Any]:
        """
        Initialize the optimization process with a baseline configuration.

        Args:
            state: Current workflow state containing treatment parameters and goals

        Returns:
            Dictionary with initial configuration and history to add to the state
        """
        # Format parameters and goals for the LLM
        parameters_text = "\n".join(
            [f"- {k}: {v}" for k, v in state['treatment_parameters'].items()])
        goals_text = "\n".join(
            [f"- {k}: {v}" for k, v in state['treatment_goals'].items()])

        prompt = f"""You are a water treatment process engineer tasked with developing an initial process configuration.
        
        Based on the following treatment parameters and optimization goals, design an initial water 
        treatment process configuration:
        
        TREATMENT PARAMETERS:
        {parameters_text}
        
        OPTIMIZATION GOALS:
        {goals_text}
        
        Provide a detailed description of a baseline treatment process configuration, including:
        1. Treatment sequence and unit processes
        2. Chemical dosages and application points
        3. Operational setpoints and control parameters
        4. Monitoring points and frequency
        5. Resource usage estimates (energy, chemicals, etc.)
        
        This will serve as the starting point for an iterative optimization process.
        """

        # Generate initial configuration
        response = self.llm.invoke(prompt)

        return {
            "process_configuration": response.content,
            "optimization_history": [],
            "iteration_count": 0
        }

    def evaluate_process(self, state: OptimizationState) -> Dict[str, ProcessEvaluation]:
        """
        Evaluate the current process configuration against optimization goals.

        Args:
            state: Current workflow state containing process configuration and goals

        Returns:
            Dictionary with process evaluation to be added to the state
        """
        # Format parameters and goals for the LLM
        parameters_text = "\n".join(
            [f"- {k}: {v}" for k, v in state['treatment_parameters'].items()])
        goals_text = "\n".join(
            [f"- {k}: {v}" for k, v in state['treatment_goals'].items()])

        # Update optimization history
        current_history = state.get('optimization_history', [])
        if state.get('iteration_count', 0) > 0:  # Don't add the initial state
            current_history.append({
                "iteration": state['iteration_count'],
                "configuration": state['process_configuration'],
                "evaluation": state.get('evaluation')
            })

        # Run the evaluation
        evaluation = self.evaluator.invoke(
            f"""You are a water treatment process evaluation expert. Carefully evaluate the following
            treatment process configuration against the specified optimization goals:
            
            TREATMENT PARAMETERS:
            {parameters_text}
            
            OPTIMIZATION GOALS:
            {goals_text}
            
            CURRENT PROCESS CONFIGURATION:
            {state['process_configuration']}
            
            Provide a detailed evaluation of this process configuration in terms of:
            1. Expected water quality outcomes vs. targets
            2. Resource efficiency (energy, chemicals, labor)
            3. Operational stability and reliability
            4. Areas that need improvement
            
            Be rigorous and demanding in your assessment. Only rate a process as "optimized" if 
            it truly meets or exceeds all optimization goals with no significant weaknesses.
            """
        )

        return {
            "evaluation": evaluation,
            "optimization_history": current_history,
            "iteration_count": state['iteration_count'] + 1
        }

    def optimize_process(self, state: OptimizationState) -> Dict[str, str]:
        """
        Improve the process configuration based on evaluation feedback.

        Args:
            state: Current workflow state containing evaluation and history

        Returns:
            Dictionary with improved configuration to be added to the state
        """
        # Format parameters and goals for the LLM
        parameters_text = "\n".join(
            [f"- {k}: {v}" for k, v in state['treatment_parameters'].items()])
        goals_text = "\n".join(
            [f"- {k}: {v}" for k, v in state['treatment_goals'].items()])

        # Get the current evaluation
        evaluation = state['evaluation']

        prompt = f"""You are a water treatment process optimization engineer. Based on the evaluation 
        feedback, improve the current treatment process configuration:
        
        TREATMENT PARAMETERS:
        {parameters_text}
        
        OPTIMIZATION GOALS:
        {goals_text}
        
        CURRENT PROCESS CONFIGURATION (Iteration {state['iteration_count']}):
        {state['process_configuration']}
        
        EVALUATION RESULTS:
        - Overall Performance Score: {evaluation.performance_score}/10
        - Water Quality Assessment: {evaluation.water_quality_assessment}
        - Efficiency Assessment: {evaluation.efficiency_assessment}
        - Specific Improvement Recommendations: {evaluation.improvement_recommendations}
        
        Revise the process configuration to address these specific improvement recommendations.
        Focus particularly on:
        1. Addressing the weaknesses identified in the evaluation
        2. Improving the aspects with the lowest performance
        3. Maintaining or enhancing the strengths of the current configuration
        4. Making targeted, strategic changes rather than complete redesigns
        
        Provide a detailed description of the improved treatment process configuration.
        """

        # Generate improved configuration
        response = self.llm.invoke(prompt)

        return {"process_configuration": response.content}

    def should_continue_optimization(self, state: OptimizationState) -> str:
        """
        Determine whether to continue the optimization process or finalize.

        Args:
            state: Current workflow state containing evaluation and iteration count

        Returns:
            "Continue" if more optimization is needed, "Complete" if optimization is finished
        """
        # Stop if maximum iterations reached
        if state['iteration_count'] >= state['max_iterations']:
            return "Complete"

        # Stop if process is already optimized
        if state['evaluation'].optimization_status == "optimized":
            return "Complete"

        # Otherwise, continue optimization
        return "Continue"

    def finalize(self, state: OptimizationState) -> Dict[str, str]:
        """
        Generate a final report on the optimization process.

        Args:
            state: Current workflow state containing the optimization results

        Returns:
            Dictionary with final configuration to be added to the state
        """
        prompt = f"""You are a water treatment process engineer creating a final report on an
        optimization process. Summarize the optimization journey and final results:
        
        INITIAL CONFIGURATION:
        {state['optimization_history'][0]['configuration'] if state['optimization_history'] else state['process_configuration']}
        
        OPTIMIZATION ITERATIONS: {state['iteration_count']}
        
        FINAL CONFIGURATION:
        {state['process_configuration']}
        
        FINAL EVALUATION:
        - Overall Performance Score: {state['evaluation'].performance_score}/10
        - Water Quality Assessment: {state['evaluation'].water_quality_assessment}
        - Efficiency Assessment: {state['evaluation'].efficiency_assessment}
        - Optimization Status: {state['evaluation'].optimization_status}
        
        Provide a comprehensive final report that includes:
        1. Executive summary of the optimization process
        2. Key improvements made during optimization
        3. Final performance metrics and their comparison to goals
        4. Implementation recommendations
        5. Expected operational benefits
        6. Long-term monitoring suggestions
        
        Present this report in a professional format suitable for utility management.
        """

        # Generate final report
        response = self.llm.invoke(prompt)

        return {"final_configuration": response.content}

    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.

        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())

    def run(self, treatment_parameters: Dict[str, Any], treatment_goals: Dict[str, Any], max_iterations: int = 5) -> OptimizationState:
        """
        Execute the treatment optimization workflow with the given parameters and goals.

        Args:
            treatment_parameters: Dictionary of water quality and operational parameters
            treatment_goals: Dictionary of optimization targets
            max_iterations: Maximum number of optimization iterations to perform

        Returns:
            The final state containing the optimized configuration and history
        """
        state = self.workflow.invoke({
            "treatment_parameters": treatment_parameters,
            "treatment_goals": treatment_goals,
            "max_iterations": max_iterations
        })
        return state


def example_usage():
    """Demonstrate the usage of TreatmentOptimizer."""

    # Example treatment parameters
    treatment_parameters = {
        "source_water_turbidity": "12-18 NTU, seasonal variation",
        "source_water_pH": "7.2-7.8",
        "total_organic_carbon": "3.2-4.5 mg/L",
        "alkalinity": "110 mg/L as CaCO3",
        "hardness": "160 mg/L as CaCO3",
        "manganese": "0.08 mg/L",
        "iron": "0.15 mg/L",
        "temperature_range": "8-22°C seasonal variation",
        "plant_capacity": "15 MGD design, 10 MGD average",
        "existing_processes": "Conventional: coagulation, flocculation, sedimentation, filtration, disinfection",
        "available_chemicals": "Alum, polymer, chlorine, caustic soda, PAC, permanganate",
        "discharge_constraints": "Backwash water recovery required, limited discharge permit",
        "space_constraints": "Limited footprint for new processes"
    }

    # Example optimization goals
    treatment_goals = {
        "finished_water_turbidity": "<0.1 NTU 95% of time, never >0.3 NTU",
        "disinfection_byproducts": "THMs <40 μg/L, HAA5 <30 μg/L",
        "chemical_consumption": "Reduce coagulant usage by 15% without compromising quality",
        "energy_efficiency": "Reduce energy consumption by 10%",
        "water_loss": "Improve filter run times by 20%, reduce backwash water to <2% of production",
        "operational_stability": "Maintain stable operation across seasonal water quality variations",
        "capital_constraints": "Optimize existing infrastructure, minimal new construction"
    }

    # Create the optimization workflow
    optimizer = TreatmentOptimizer()

    # Visualize the workflow (useful in notebooks)
    # display(optimizer.visualize())

    # Run the workflow with maximum 3 iterations
    result = optimizer.run(treatment_parameters,
                           treatment_goals, max_iterations=3)

    # Print final optimized configuration
    print("TREATMENT PROCESS OPTIMIZATION REPORT:")
    print("======================================")
    print(result["final_configuration"])

    # Print optimization history (iterations)
    print("\nOPTIMIZATION HISTORY:")
    print("====================")
    for i, entry in enumerate(result["optimization_history"]):
        print(f"\nITERATION {i+1}:")
        print(f"Performance Score: {entry['evaluation'].performance_score}/10")
        print(f"Status: {entry['evaluation'].optimization_status}")


if __name__ == "__main__":
    example_usage()
