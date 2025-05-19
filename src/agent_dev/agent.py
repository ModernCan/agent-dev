# -*- coding: utf-8 -*-
"""Agent Module.

This module demonstrates a fully autonomous agent that can plan, take actions
via tools, and respond to feedback in a continuous loop.
"""

import os
from typing import Dict, Any, Optional, Callable, Literal, List
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from IPython.display import Image

# Load environment variables
load_dotenv()


class Agent:
    """
    Implements a fully autonomous agent that can plan, take actions via tools,
    and respond to feedback in a continuous loop.

    This class demonstrates how to create a system that can make decisions
    about which tools to use and when to use them to solve tasks.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the Agent with specified model and tools.

        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")

        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)

        # Define tools
        self.tools = self._create_tools()
        self.tools_by_name = {tool.name: tool for tool in self.tools}

        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Build the agent graph
        self.agent = self._build_agent()

    def _create_tools(self) -> List[Callable]:
        """
        Create the tools that the agent can use.

        Returns:
            A list of tool functions available to the agent
        """
        # Define tools
        @tool
        def multiply(a: int, b: int) -> int:
            """Multiply a and b.

            Args:
                a: first int
                b: second int
            """
            return a * b

        @tool
        def add(a: int, b: int) -> int:
            """Adds a and b.

            Args:
                a: first int
                b: second int
            """
            return a + b

        @tool
        def divide(a: int, b: int) -> float:
            """Divide a and b.

            Args:
                a: first int
                b: second int
            """
            return a / b

        return [add, multiply, divide]

    def _build_agent(self) -> StateGraph:
        """
        Builds the agent workflow graph.

        Returns:
            A compiled LangGraph StateGraph representing the agent
        """
        # Build agent
        agent_builder = StateGraph(MessagesState)

        # Add nodes
        agent_builder.add_node("llm_call", self.llm_call)
        agent_builder.add_node("tool_executor", self.tool_executor)

        # Add edges to connect nodes
        agent_builder.add_edge(START, "llm_call")
        agent_builder.add_conditional_edges(
            "llm_call",
            self.should_continue,
            {
                "Action": "tool_executor",
                END: END,
            },
        )
        agent_builder.add_edge("tool_executor", "llm_call")

        # Compile the agent
        return agent_builder.compile()

    def llm_call(self, state: MessagesState) -> Dict[str, List]:
        """
        LLM decides whether to call a tool or not.

        Args:
            state: The current message state

        Returns:
            Dictionary with updated messages to be added to the state
        """
        return {
            "messages": [
                self.llm_with_tools.invoke(
                    [
                        SystemMessage(
                            content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                        )
                    ]
                    + state["messages"]
                )
            ]
        }

    def tool_executor(self, state: MessagesState) -> Dict[str, List]:
        """
        Executes the tool calls made by the LLM.

        Args:
            state: The current message state with tool calls

        Returns:
            Dictionary with tool results to be added to the state
        """
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = self.tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=str(observation),
                          tool_call_id=tool_call["id"]))
        return {"messages": result}

    def should_continue(self, state: MessagesState) -> Literal["Action", str]:
        """
        Decide if the agent should continue the loop or stop.

        Args:
            state: The current message state

        Returns:
            "Action" if the LLM made a tool call, END otherwise
        """
        messages = state["messages"]
        last_message = messages[-1]

        # If the LLM makes a tool call, then perform an action
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "Action"

        # Otherwise, we stop (reply to the user)
        return END

    def visualize(self) -> Image:
        """
        Generate a visualization of the agent graph.

        Returns:
            IPython Image object containing the agent diagram
        """
        return Image(self.agent.get_graph(xray=True).draw_mermaid_png())

    def run(self, query: str) -> MessagesState:
        """
        Execute the agent with the given query.

        Args:
            query: The user's query or task

        Returns:
            The final message state containing the conversation
        """
        messages = [HumanMessage(content=query)]
        result = self.agent.invoke({"messages": messages})
        return result


def example_usage():
    """Demonstrate the usage of Agent."""

    # Create the agent
    arithmetic_agent = Agent()

    # Visualize the agent (useful in notebooks)
    # display(arithmetic_agent.visualize())

    # Run the agent
    result = arithmetic_agent.run(
        "Add 3 and 4. Then, take the output and multiply by 4.")

    # Print results
    print("Final conversation:")
    for message in result["messages"]:
        print(
            f"\n{'User' if isinstance(message, HumanMessage) else 'Assistant'}: {message.content}")

        # Print any tool calls
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                print(f"  Tool Call: {tool_call['name']}({tool_call['args']})")


if __name__ == "__main__":
    example_usage()
