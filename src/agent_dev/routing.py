"""
Routing Module.

This module demonstrates the routing pattern, where input is classified
and directed to specialized handlers based on the classification.
"""

import os
from typing import TypedDict, Dict, Any, Optional, Callable, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from IPython.display import Image

# Load environment variables
load_dotenv()

# Define a schema for the routing decision
class Route(BaseModel):
    """Schema for the routing decision."""
    step: Literal["poem", "story", "joke"] = Field(
        None, description="The next step in the routing process"
    )


# Define the state type for type checking
class RoutingState(TypedDict):
    """Type definition for the routing state."""
    input: str
    decision: str
    output: str


class Routing:
    """
    Implements the routing pattern where input is classified and directed
    to specialized handlers based on the classification.
    
    This class demonstrates how to use an LLM to make routing decisions
    and then direct the flow to specialized LLM calls.
    """
    
    def __init__(
        self, 
        model_name: str = "claude-3-5-sonnet-latest", 
        api_key: Optional[str] = None
    ):
        """
        Initialize the Routing with specified model.
        
        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")
            
        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)
        self.router = self.llm.with_structured_output(Route)
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """
        Builds the routing workflow.
        
        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        router_builder = StateGraph(RoutingState)

        # Add nodes
        router_builder.add_node("write_story", self.write_story)
        router_builder.add_node("write_joke", self.write_joke)
        router_builder.add_node("write_poem", self.write_poem)
        router_builder.add_node("router", self.route_input)

        # Add edges to connect nodes
        router_builder.add_edge(START, "router")
        router_builder.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "write_story": "write_story",
                "write_joke": "write_joke",
                "write_poem": "write_poem",
            },
        )
        router_builder.add_edge("write_story", END)
        router_builder.add_edge("write_joke", END)
        router_builder.add_edge("write_poem", END)

        # Compile workflow
        return router_builder.compile()
    
    def route_input(self, state: RoutingState) -> Dict[str, str]:
        """
        Routes the input to the appropriate node based on classification.
        
        Args:
            state: The current workflow state containing the input
            
        Returns:
            Dictionary with the routing decision to be added to the state
        """
        print("Routing the input...")
        # Run the augmented LLM with structured output to serve as routing logic
        decision = self.router.invoke(
            [
                SystemMessage(
                    content="Route the input to story, joke, or poem based on the user's request."
                ),
                HumanMessage(content=state["input"]),
            ]
        )
        
        return {"decision": decision.step}
    
    def route_decision(self, state: RoutingState) -> str:
        """
        Conditional edge function to determine the next node.
        
        Args:
            state: The current workflow state containing the routing decision
            
        Returns:
            The name of the next node to visit
        """
        # Return the appropriate handler based on the decision
        if state["decision"] == "story":
            return "write_story"
        elif state["decision"] == "joke":
            return "write_joke"
        elif state["decision"] == "poem":
            return "write_poem"
        else:
            raise ValueError(f"Unknown routing decision: {state['decision']}")

    def write_story(self, state: RoutingState) -> Dict[str, str]:
        """
        Handler for story generation.
        
        Args:
            state: The current workflow state containing the input
            
        Returns:
            Dictionary with the generated story to be added to the state
        """
        print("Writing a story...")
        result = self.llm.invoke(
            f"Write a creative short story based on this request: {state['input']}"
        )
        return {"output": result.content}

    def write_joke(self, state: RoutingState) -> Dict[str, str]:
        """
        Handler for joke generation.
        
        Args:
            state: The current workflow state containing the input
            
        Returns:
            Dictionary with the generated joke to be added to the state
        """
        print("Writing a joke...")
        result = self.llm.invoke(
            f"Write a funny joke based on this request: {state['input']}"
        )
        return {"output": result.content}

    def write_poem(self, state: RoutingState) -> Dict[str, str]:
        """
        Handler for poem generation.
        
        Args:
            state: The current workflow state containing the input
            
        Returns:
            Dictionary with the generated poem to be added to the state
        """
        print("Writing a poem...")
        result = self.llm.invoke(
            f"Write a beautiful poem based on this request: {state['input']}"
        )
        return {"output": result.content}
    
    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.
        
        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())
    
    def run(self, input_text: str) -> RoutingState:
        """
        Execute the routing workflow with the given input.
        
        Args:
            input_text: The user request to route and process
            
        Returns:
            The final state containing the output
        """
        state = self.workflow.invoke({"input": input_text})
        return state


def example_usage():
    """Demonstrate the usage of Routing."""
    
    # Create the routing workflow
    routing = Routing()
    
    # Visualize the workflow (useful in notebooks)
    # display(routing.visualize())
    
    # Run the workflow with different inputs
    story_result = routing.run("Tell me a story about a space explorer")
    print("\nStory Output:")
    print(story_result["output"])
    
    joke_result = routing.run("Make me laugh with something about programming")
    print("\nJoke Output:")
    print(joke_result["output"])
    
    poem_result = routing.run("Create a poem about autumn leaves")
    print("\nPoem Output:")
    print(poem_result["output"])


if __name__ == "__main__":
    example_usage()
