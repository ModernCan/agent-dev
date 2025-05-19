# -*- coding: utf-8 -*-
"""
Water Utility Customer Service Module (Routing).

This module demonstrates the routing pattern applied to a water utility customer
service system, classifying inquiries and directing them to specialized handlers.
"""

import os
from typing import TypedDict, Dict, Any, Optional, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from IPython.display import Image

# Load environment variables
load_dotenv()

# Define a schema for the routing decision


class InquiryRoute(BaseModel):
    """Schema for the customer inquiry routing decision."""
    category: Literal[
        "billing", "service_disruption", "water_quality",
        "conservation", "new_service", "general"
    ] = Field(
        description="The category of the customer inquiry"
    )
    priority: Literal["low", "medium", "high", "emergency"] = Field(
        description="The priority level of the inquiry"
    )


# Define the state type for type checking
class CustomerServiceState(TypedDict):
    """Type definition for the customer service state."""
    inquiry: str              # The original customer inquiry
    category: str             # Classified inquiry category
    priority: str             # Priority level
    response: str             # The final response to the customer


class CustomerServiceSystem:
    """
    Implements the routing pattern for a water utility customer service system.

    This class demonstrates how to classify customer inquiries by category and priority,
    then route them to specialized handlers for appropriate responses.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the CustomerServiceSystem with specified model.

        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")

        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)
        self.router = self.llm.with_structured_output(InquiryRoute)
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Builds the routing workflow for customer service inquiries.

        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        cs_workflow = StateGraph(CustomerServiceState)

        # Add nodes for the router and specialized handlers
        cs_workflow.add_node("classify_inquiry", self.classify_inquiry)
        cs_workflow.add_node("handle_billing", self.handle_billing)
        cs_workflow.add_node("handle_service_disruption",
                             self.handle_service_disruption)
        cs_workflow.add_node("handle_water_quality", self.handle_water_quality)
        cs_workflow.add_node("handle_conservation", self.handle_conservation)
        cs_workflow.add_node("handle_new_service", self.handle_new_service)
        cs_workflow.add_node("handle_general", self.handle_general)

        # Add edges to connect nodes
        cs_workflow.add_edge(START, "classify_inquiry")
        cs_workflow.add_conditional_edges(
            "classify_inquiry",
            self.route_inquiry,
            {
                "billing": "handle_billing",
                "service_disruption": "handle_service_disruption",
                "water_quality": "handle_water_quality",
                "conservation": "handle_conservation",
                "new_service": "handle_new_service",
                "general": "handle_general",
            },
        )
        cs_workflow.add_edge("handle_billing", END)
        cs_workflow.add_edge("handle_service_disruption", END)
        cs_workflow.add_edge("handle_water_quality", END)
        cs_workflow.add_edge("handle_conservation", END)
        cs_workflow.add_edge("handle_new_service", END)
        cs_workflow.add_edge("handle_general", END)

        # Compile workflow
        return cs_workflow.compile()

    def classify_inquiry(self, state: CustomerServiceState) -> Dict[str, str]:
        """
        Classifies a customer inquiry by category and priority.

        Args:
            state: Current workflow state containing the customer inquiry

        Returns:
            Dictionary with classification results to be added to the state
        """
        # Run the router LLM to classify the inquiry
        classification = self.router.invoke(
            [
                SystemMessage(
                    content="""You are a water utility customer service classifier. 
                    Analyze customer inquiries and classify them by category and priority.
                    
                    Categories:
                    - billing: Questions about bills, payments, rates, or account status
                    - service_disruption: Reports of service outages, low pressure, or leaks
                    - water_quality: Concerns about water taste, odor, color, or safety
                    - conservation: Questions about water efficiency, restrictions, or conservation programs
                    - new_service: Requests for new connections or service changes
                    - general: General information requests that don't fit other categories
                    
                    Priority levels:
                    - low: General information requests with no time sensitivity
                    - medium: Issues that should be addressed in the next 1-2 business days
                    - high: Urgent issues requiring same-day attention
                    - emergency: Critical issues requiring immediate response (major leaks, contamination)
                    """
                ),
                HumanMessage(content=state["inquiry"]),
            ]
        )

        return {
            "category": classification.category,
            "priority": classification.priority
        }

    def route_inquiry(self, state: CustomerServiceState) -> str:
        """
        Routes the inquiry to the appropriate specialized handler.

        Args:
            state: Current workflow state containing the classification

        Returns:
            The name of the handler node to process the inquiry
        """
        return f"handle_{state['category']}"

    def handle_billing(self, state: CustomerServiceState) -> Dict[str, str]:
        """
        Specialized handler for billing inquiries.

        Args:
            state: Current workflow state containing the inquiry and classification

        Returns:
            Dictionary with the response to be added to the state
        """
        prompt = f"""You are a water utility billing specialist. Provide a helpful response to the following customer inquiry:

Customer inquiry: {state['inquiry']}

This has been classified as a {state['priority']} priority billing inquiry.

Address the inquiry with:
1. A greeting that acknowledges their billing concern
2. Specific information about water utility billing processes
3. Clear next steps for the customer
4. Any relevant information about payment options, bill structure, or account management
5. A professional closing with offer of further assistance if needed
"""

        msg = self.llm.invoke(prompt)
        return {"response": msg.content}

    def handle_service_disruption(self, state: CustomerServiceState) -> Dict[str, str]:
        """
        Specialized handler for service disruption inquiries.

        Args:
            state: Current workflow state containing the inquiry and classification

        Returns:
            Dictionary with the response to be added to the state
        """
        # Emergency priorities get a special response
        if state['priority'] == "emergency":
            emergency_prompt = f"""You are a water utility emergency response specialist. Provide an urgent response to this emergency service disruption:

Customer inquiry: {state['inquiry']}

This has been classified as an EMERGENCY priority service disruption.

Provide:
1. Acknowledgment of the emergency situation
2. Immediate safety instructions if relevant
3. Confirmation that an emergency crew will be dispatched immediately
4. Request for specific location details if not provided
5. Emergency contact phone number (555-123-4567)
6. Instructions to call 911 if there is any safety risk to people
"""
            msg = self.llm.invoke(emergency_prompt)
            return {"response": msg.content}

        # Non-emergency service disruptions
        prompt = f"""You are a water utility service specialist. Provide a helpful response to the following customer inquiry:

Customer inquiry: {state['inquiry']}

This has been classified as a {state['priority']} priority service disruption inquiry.

Address the inquiry with:
1. Acknowledgment of the service issue
2. Information about how service disruptions are handled
3. Expected timeline for resolution based on priority ({state['priority']})
4. Any troubleshooting steps the customer can take
5. How the customer will be updated on progress
6. A professional closing with appropriate urgency
"""

        msg = self.llm.invoke(prompt)
        return {"response": msg.content}

    def handle_water_quality(self, state: CustomerServiceState) -> Dict[str, str]:
        """
        Specialized handler for water quality inquiries.

        Args:
            state: Current workflow state containing the inquiry and classification

        Returns:
            Dictionary with the response to be added to the state
        """
        prompt = f"""You are a water quality specialist at a water utility. Provide a helpful response to the following customer inquiry:

Customer inquiry: {state['inquiry']}

This has been classified as a {state['priority']} priority water quality inquiry.

Address the inquiry with:
1. Acknowledgment of their water quality concern
2. Factual information about water quality standards and testing procedures
3. Common causes for water quality issues like taste, odor, or appearance
4. Any immediate actions the customer should take
5. Information about how water quality complaints are investigated
6. A professional closing that emphasizes the utility's commitment to safe water
"""

        msg = self.llm.invoke(prompt)
        return {"response": msg.content}

    def handle_conservation(self, state: CustomerServiceState) -> Dict[str, str]:
        """
        Specialized handler for water conservation inquiries.

        Args:
            state: Current workflow state containing the inquiry and classification

        Returns:
            Dictionary with the response to be added to the state
        """
        prompt = f"""You are a water conservation specialist at a water utility. Provide a helpful response to the following customer inquiry:

Customer inquiry: {state['inquiry']}

This has been classified as a {state['priority']} priority water conservation inquiry.

Address the inquiry with:
1. Acknowledgment of their interest in water conservation
2. Specific information about water efficiency and conservation practices
3. Details about any current water restrictions or conservation programs
4. Available rebates or incentives for water-saving devices
5. Resources for additional water conservation information
6. A professional closing that emphasizes the importance of water stewardship
"""

        msg = self.llm.invoke(prompt)
        return {"response": msg.content}

    def handle_new_service(self, state: CustomerServiceState) -> Dict[str, str]:
        """
        Specialized handler for new service inquiries.

        Args:
            state: Current workflow state containing the inquiry and classification

        Returns:
            Dictionary with the response to be added to the state
        """
        prompt = f"""You are a new service connection specialist at a water utility. Provide a helpful response to the following customer inquiry:

Customer inquiry: {state['inquiry']}

This has been classified as a {state['priority']} priority new service inquiry.

Address the inquiry with:
1. Acknowledgment of their interest in new service
2. Overview of the service connection process
3. Required documentation and fees
4. Typical timeline for new service installation
5. Next steps in the application process
6. A professional closing with contact information for the new connections department
"""

        msg = self.llm.invoke(prompt)
        return {"response": msg.content}

    def handle_general(self, state: CustomerServiceState) -> Dict[str, str]:
        """
        Specialized handler for general inquiries.

        Args:
            state: Current workflow state containing the inquiry and classification

        Returns:
            Dictionary with the response to be added to the state
        """
        prompt = f"""You are a customer service representative at a water utility. Provide a helpful response to the following general customer inquiry:

Customer inquiry: {state['inquiry']}

This has been classified as a {state['priority']} priority general inquiry.

Address the inquiry with:
1. A friendly greeting
2. Clear and concise information addressing their question
3. Any relevant general information about the water utility's services
4. Direction to specific departments if more specialized information is needed
5. A professional closing with offer of further assistance
"""

        msg = self.llm.invoke(prompt)
        return {"response": msg.content}

    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.

        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())

    def run(self, inquiry: str) -> CustomerServiceState:
        """
        Process a customer inquiry through the routing workflow.

        Args:
            inquiry: The customer's question or request

        Returns:
            The final state containing the classified inquiry and response
        """
        state = self.workflow.invoke({"inquiry": inquiry})
        return state


def example_usage():
    """Demonstrate the usage of CustomerServiceSystem."""

    # Create the customer service system
    cs_system = CustomerServiceSystem()

    # Visualize the workflow (useful in notebooks)
    # display(cs_system.visualize())

    # Example inquiries from different categories
    inquiries = [
        "I think my water bill is too high this month. Can you explain the charges?",
        "There's water gushing out of a pipe on Main Street near Oak Avenue!",
        "My water has a strange chlorine smell and tastes funny.",
        "What rebates do you offer for installing water-efficient toilets?",
        "I'm building a new house and need to set up water service.",
        "What are your office hours?"
    ]

    # Process each inquiry
    for inquiry in inquiries:
        print("\n" + "="*80)
        print(f"CUSTOMER INQUIRY: {inquiry}")
        print("="*80)

        result = cs_system.run(inquiry)

        print(f"Category: {result['category']}")
        print(f"Priority: {result['priority']}")
        print("\nRESPONSE:")
        print(result['response'])


if __name__ == "__main__":
    example_usage()
