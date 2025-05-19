# -*- coding: utf-8 -*-
"""Drought Management System Module (Orchestrator-Worker).

This module demonstrates the orchestrator-worker pattern applied to drought response
management, planning coordinated actions across multiple operational areas.
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

# Define schemas for the drought response actions


class DroughtAction(BaseModel):
    """Schema for an individual drought response action."""
    title: str = Field(
        description="Title of the drought response action.",
    )
    description: str = Field(
        description="Detailed description of what the action entails.",
    )
    department: str = Field(
        description="Responsible department (Supply, Operations, Communications, or Conservation).",
    )
    priority: str = Field(
        description="Priority level (High, Medium, Low).",
    )
    timeline: str = Field(
        description="Timeline for implementation.",
    )


class DroughtPlan(BaseModel):
    """Schema for the collection of drought response actions."""
    actions: List[DroughtAction] = Field(
        description="List of drought response actions across all operational areas.",
    )


# Define the state types for type checking
class DroughtResponseState(TypedDict):
    """Type definition for the drought response planning state."""
    drought_data: Dict[str,
                       Any]              # Drought conditions and resource data
    # Master list of all planned actions
    drought_actions: list[DroughtAction]
    # Actions from each department
    completed_actions: Annotated[list, operator.add]
    supply_plan: str                          # Water supply management plan
    operations_plan: str                      # Operational response plan
    communications_plan: str                  # Public communications plan
    conservation_plan: str                    # Water conservation plan
    # Final integrated drought response plan
    integrated_response_plan: str


class WorkerState(TypedDict):
    """Type definition for the worker state."""
    actions: List[DroughtAction]
    completed_actions: Annotated[list, operator.add]


class DroughtManagementSystem:
    """
    Implements the orchestrator-worker pattern for drought response management.

    This class demonstrates how a central orchestrator can plan a comprehensive
    drought response strategy, delegate specific actions to specialized departments,
    and integrate their individual plans into a cohesive response.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the DroughtManagementSystem with specified model.

        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")

        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)
        self.planner = self.llm.with_structured_output(DroughtPlan)
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Builds the orchestrator-worker workflow for drought response.

        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        drought_workflow = StateGraph(DroughtResponseState)

        # Add the nodes
        drought_workflow.add_node("orchestrator", self.orchestrator)
        drought_workflow.add_node("supply_worker", self.supply_worker)
        drought_workflow.add_node("operations_worker", self.operations_worker)
        drought_workflow.add_node(
            "communications_worker", self.communications_worker)
        drought_workflow.add_node(
            "conservation_worker", self.conservation_worker)
        drought_workflow.add_node("integrator", self.integrator)

        # Add edges to connect nodes
        drought_workflow.add_edge(START, "orchestrator")
        drought_workflow.add_conditional_edges(
            "orchestrator", self.assign_workers, [
                "supply_worker",
                "operations_worker",
                "communications_worker",
                "conservation_worker"
            ]
        )
        drought_workflow.add_edge("supply_worker", "integrator")
        drought_workflow.add_edge("operations_worker", "integrator")
        drought_workflow.add_edge("communications_worker", "integrator")
        drought_workflow.add_edge("conservation_worker", "integrator")
        drought_workflow.add_edge("integrator", END)

        # Compile the workflow
        return drought_workflow.compile()

    def orchestrator(self, state: DroughtResponseState) -> Dict[str, List[DroughtAction]]:
        """
        The orchestrator that plans comprehensive drought response actions.

        Args:
            state: Current workflow state containing drought data

        Returns:
            Dictionary with planned actions to be added to the state
        """
        # Format drought data for the LLM
        drought_info = "\n".join(
            [f"- {k}: {v}" for k, v in state['drought_data'].items()])

        # Generate drought response plan
        plan = self.planner.invoke(
            [
                SystemMessage(content="""You are a drought management expert tasked with creating 
                a comprehensive drought response plan. Based on the drought data provided, 
                develop specific actions across the following operational areas:
                
                1. Water Supply Management (Department: Supply)
                2. Utility Operations (Department: Operations)
                3. Public Communications (Department: Communications)
                4. Water Conservation Programs (Department: Conservation)
                
                For each action, include a title, detailed description, responsible department, 
                priority level (High, Medium, Low), and implementation timeline."""),
                HumanMessage(
                    content=f"Here is the current drought information:\n\n{drought_info}"),
            ]
        )

        return {"drought_actions": plan.actions}

    def assign_workers(self, state: DroughtResponseState) -> List[Send]:
        """
        Assign workers to handle actions for their respective departments.

        Args:
            state: Current workflow state containing planned actions

        Returns:
            List of Send objects to trigger department-specific workers
        """
        # Group actions by department
        supply_actions = [a for a in state['drought_actions']
                          if a.department == "Supply"]
        operations_actions = [
            a for a in state['drought_actions'] if a.department == "Operations"]
        communications_actions = [
            a for a in state['drought_actions'] if a.department == "Communications"]
        conservation_actions = [
            a for a in state['drought_actions'] if a.department == "Conservation"]

        # Send actions to appropriate workers
        return [
            Send("supply_worker", {"actions": supply_actions}),
            Send("operations_worker", {"actions": operations_actions}),
            Send("communications_worker", {"actions": communications_actions}),
            Send("conservation_worker", {"actions": conservation_actions})
        ]

    def supply_worker(self, state: WorkerState) -> Dict[str, Any]:
        """
        Worker that creates a water supply management plan.

        Args:
            state: Worker state containing assigned supply actions

        Returns:
            Dictionary with supply plan and completed actions
        """
        # Format actions for the LLM
        actions_text = "\n\n".join([
            f"Action: {a.title}\nDescription: {a.description}\nPriority: {a.priority}\nTimeline: {a.timeline}"
            for a in state['actions']
        ])

        prompt = f"""You are a water supply manager at a water utility responding to drought conditions.
        
        Based on the following drought response actions assigned to the Supply department, 
        develop a detailed water supply management plan:
        
        {actions_text}
        
        Your plan should include:
        1. Specific implementation steps for each action
        2. Required resources and infrastructure
        3. Monitoring and measurement approaches
        4. Coordination with other departments
        5. Contingency plans if conditions worsen
        
        Present a comprehensive, actionable water supply management plan.
        """

        # Generate supply plan
        response = self.llm.invoke(prompt)

        # Add department label to each action for tracking
        for action in state['actions']:
            action.title = f"[SUPPLY] {action.title}"

        return {
            "supply_plan": response.content,
            "completed_actions": state['actions']
        }

    def operations_worker(self, state: WorkerState) -> Dict[str, Any]:
        """
        Worker that creates an operational response plan.

        Args:
            state: Worker state containing assigned operations actions

        Returns:
            Dictionary with operations plan and completed actions
        """
        # Format actions for the LLM
        actions_text = "\n\n".join([
            f"Action: {a.title}\nDescription: {a.description}\nPriority: {a.priority}\nTimeline: {a.timeline}"
            for a in state['actions']
        ])

        prompt = f"""You are an operations manager at a water utility responding to drought conditions.
        
        Based on the following drought response actions assigned to the Operations department, 
        develop a detailed operational response plan:
        
        {actions_text}
        
        Your plan should include:
        1. Personnel assignments and responsibilities
        2. Equipment and infrastructure requirements
        3. Operational adjustments and protocols
        4. Monitoring and control procedures
        5. Coordination with other utility functions
        
        Present a comprehensive, actionable operational response plan.
        """

        # Generate operations plan
        response = self.llm.invoke(prompt)

        # Add department label to each action for tracking
        for action in state['actions']:
            action.title = f"[OPERATIONS] {action.title}"

        return {
            "operations_plan": response.content,
            "completed_actions": state['actions']
        }

    def communications_worker(self, state: WorkerState) -> Dict[str, Any]:
        """
        Worker that creates a public communications plan.

        Args:
            state: Worker state containing assigned communications actions

        Returns:
            Dictionary with communications plan and completed actions
        """
        # Format actions for the LLM
        actions_text = "\n\n".join([
            f"Action: {a.title}\nDescription: {a.description}\nPriority: {a.priority}\nTimeline: {a.timeline}"
            for a in state['actions']
        ])

        prompt = f"""You are a communications director at a water utility responding to drought conditions.
        
        Based on the following drought response actions assigned to the Communications department, 
        develop a detailed public communications plan:
        
        {actions_text}
        
        Your plan should include:
        1. Key messages for different audiences
        2. Communication channels and methods
        3. Timeline for public announcements
        4. Media relations strategy
        5. Customer support resources
        
        Present a comprehensive, actionable public communications plan.
        """

        # Generate communications plan
        response = self.llm.invoke(prompt)

        # Add department label to each action for tracking
        for action in state['actions']:
            action.title = f"[COMMUNICATIONS] {action.title}"

        return {
            "communications_plan": response.content,
            "completed_actions": state['actions']
        }

    def conservation_worker(self, state: WorkerState) -> Dict[str, Any]:
        """
        Worker that creates a water conservation plan.

        Args:
            state: Worker state containing assigned conservation actions

        Returns:
            Dictionary with conservation plan and completed actions
        """
        # Format actions for the LLM
        actions_text = "\n\n".join([
            f"Action: {a.title}\nDescription: {a.description}\nPriority: {a.priority}\nTimeline: {a.timeline}"
            for a in state['actions']
        ])

        prompt = f"""You are a water conservation manager at a water utility responding to drought conditions.
        
        Based on the following drought response actions assigned to the Conservation department, 
        develop a detailed water conservation plan:
        
        {actions_text}
        
        Your plan should include:
        1. Customer conservation programs and incentives
        2. Water use restrictions and enforcement
        3. Conservation targets and metrics
        4. Public education initiatives
        5. Commercial and industrial partnership approaches
        
        Present a comprehensive, actionable water conservation plan.
        """

        # Generate conservation plan
        response = self.llm.invoke(prompt)

        # Add department label to each action for tracking
        for action in state['actions']:
            action.title = f"[CONSERVATION] {action.title}"

        return {
            "conservation_plan": response.content,
            "completed_actions": state['actions']
        }

    def integrator(self, state: DroughtResponseState) -> Dict[str, str]:
        """
        Integrates department plans into a comprehensive drought response plan.

        Args:
            state: Current workflow state containing all department plans

        Returns:
            Dictionary with integrated response plan
        """
        prompt = f"""You are a drought response coordinator tasked with integrating multiple 
        departmental plans into a cohesive, coordinated drought management strategy.
        
        Based on the following department-specific plans, create an integrated drought 
        response plan that ensures coordination, eliminates redundancies, and optimizes resource use:
        
        WATER SUPPLY MANAGEMENT PLAN:
        {state['supply_plan']}
        
        OPERATIONAL RESPONSE PLAN:
        {state['operations_plan']}
        
        PUBLIC COMMUNICATIONS PLAN:
        {state['communications_plan']}
        
        WATER CONSERVATION PLAN:
        {state['conservation_plan']}
        
        Your integrated plan should include:
        1. Executive summary
        2. Coordinated timeline across all departments
        3. Cross-departmental dependencies and coordination points
        4. Resource allocation and prioritization
        5. Unified monitoring and reporting framework
        6. Governance structure for drought response
        7. Adaptive management approach as conditions change
        """

        # Generate integrated plan
        response = self.llm.invoke(prompt)

        return {"integrated_response_plan": response.content}

    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.

        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())

    def run(self, drought_data: Dict[str, Any]) -> DroughtResponseState:
        """
        Execute the drought management workflow with the given drought data.

        Args:
            drought_data: Dictionary of drought conditions and resource information

        Returns:
            The final state containing department plans and integrated response
        """
        state = self.workflow.invoke({"drought_data": drought_data})
        return state


def example_usage():
    """Demonstrate the usage of DroughtManagementSystem."""

    # Example drought data
    drought_data = {
        "drought_severity": "Severe (Stage 3)",
        "current_reservoir_level": "37% of capacity (historically low)",
        "groundwater_levels": "Declining, 15% below seasonal average",
        "precipitation_forecast": "Below normal precipitation expected for next 3 months",
        "current_water_demand": "22% above sustainable levels",
        "water_supply_forecast": "Expected 30% reduction in available supply if conditions persist",
        "regulatory_requirements": "State-mandated 25% reduction in water usage",
        "regional_conditions": "Neighboring utilities also implementing restrictions",
        "critical_customer_needs": "Hospital, fire services, and food production prioritized",
        "available_emergency_sources": "Limited emergency interconnections with neighboring systems",
        "current_restriction_level": "Stage 2 (moderate) restrictions currently in place",
        "conservation_program_status": "Existing programs reaching 15% of customers",
        "infrastructure_constraints": "Treatment capacity reduced due to lower reservoir levels",
        "public_awareness_level": "Moderate awareness, 40% recognition of drought conditions"
    }

    # Create the drought management system
    drought_system = DroughtManagementSystem()

    # Visualize the workflow (useful in notebooks)
    # display(drought_system.visualize())

    # Run the workflow
    result = drought_system.run(drought_data)

    # Print the integrated response plan
    print("INTEGRATED DROUGHT RESPONSE PLAN:")
    print("=================================")
    print(result["integrated_response_plan"])

    # For Jupyter notebooks
    # display(Markdown(result["integrated_response_plan"]))

    # To see individual department plans
    # print("\nWATER SUPPLY MANAGEMENT PLAN:")
    # print(result["supply_plan"])


if __name__ == "__main__":
    example_usage()
