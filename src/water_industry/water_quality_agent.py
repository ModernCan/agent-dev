"""
Water Quality Monitoring Agent Module.

This module demonstrates the fully autonomous agent pattern applied to
continuous water quality monitoring, taking independent actions based on readings.
"""

import os
from typing import Dict, Any, Optional, Callable, Literal, List
from dotenv import load_dotenv
import time
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from IPython.display import Image

# Load environment variables
load_dotenv()


class WaterQualityAgent:
    """
    Implements a fully autonomous agent for water quality monitoring.
    
    This class demonstrates an agent that can continuously monitor water quality parameters,
    detect anomalies, diagnose problems, recommend treatment adjustments, and alert
    operators when necessary, all without human intervention.
    """
    
    def __init__(
        self, 
        model_name: str = "claude-3-5-sonnet-latest", 
        api_key: Optional[str] = None
    ):
        """
        Initialize the WaterQualityAgent with specified model.
        
        Args:
            model_name: The name of the Anthropic model to use
            api_key: Optional API key for Anthropic (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")
            
        self.model_name = model_name
        self.llm = ChatAnthropic(model=model_name)
        
        # Create tools
        self.tools = self._create_tools()
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        
        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build the agent graph
        self.agent = self._build_agent()
        
        # Store historical readings
        self.historical_readings = []
        
    def _create_tools(self) -> List[Callable]:
        """
        Create the tools that the water quality monitoring agent can use.
        
        Returns:
            A list of tool functions available to the agent
        """
        @tool
        def get_current_readings() -> Dict[str, float]:
            """
            Get the current water quality parameter readings from sensors.
            Returns a dictionary with key parameters and their current values.
            """
            # In a real implementation, this would connect to SCADA or sensor APIs
            # For demonstration purposes, we'll simulate readings with some randomness
            import random
            
            # Base readings (typical values)
            base_readings = {
                "pH": 7.2,
                "turbidity": 0.3,  # NTU
                "chlorine_residual": 0.9,  # mg/L
                "total_dissolved_solids": 285,  # mg/L
                "temperature": 15.5,  # °C
                "pressure": 65,  # PSI
                "flow_rate": 3.2,  # MGD
            }
            
            # Add some randomness to simulate real conditions
            # Occasionally introduce an anomaly for demonstration purposes
            current_time = datetime.now()
            if current_time.second % 30 < 5:  # Create anomaly 5 seconds out of every 30
                # Create a pH anomaly
                base_readings["pH"] = 8.7
                base_readings["turbidity"] = 1.8
                base_readings["chlorine_residual"] = 0.3
            else:
                # Normal variation
                for param in base_readings:
                    variation = random.uniform(-0.1, 0.1)
                    base_readings[param] *= (1 + variation)
                    
            # Round values for cleaner display
            rounded_readings = {k: round(v, 2) for k, v in base_readings.items()}
            
            # Add timestamp
            rounded_readings["timestamp"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            return rounded_readings
        
        @tool
        def get_historical_trends(parameter: str, hours: int = 24) -> str:
            """
            Retrieve historical trends for a specific water quality parameter.
            
            Args:
                parameter: The parameter to retrieve history for (pH, turbidity, etc.)
                hours: Number of hours of history to retrieve (default 24)
                
            Returns:
                A summary of the parameter's trend over the specified period
            """
            # In a real implementation, this would query a database or historian
            if len(self.historical_readings) < 2:
                return f"Insufficient historical data for {parameter}. Only {len(self.historical_readings)} readings available."
            
            # Extract the parameter values from historical readings
            try:
                values = [reading.get(parameter, None) for reading in self.historical_readings]
                values = [v for v in values if v is not None]
                
                if not values:
                    return f"No historical data found for parameter: {parameter}"
                
                avg_value = sum(values) / len(values)
                min_value = min(values)
                max_value = max(values)
                latest_value = values[-1]
                
                # Calculate simple trend
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                first_half_avg = sum(first_half) / len(first_half)
                second_half_avg = sum(second_half) / len(second_half)
                
                if second_half_avg > first_half_avg * 1.05:
                    trend = "rising significantly"
                elif second_half_avg > first_half_avg:
                    trend = "rising slightly"
                elif second_half_avg < first_half_avg * 0.95:
                    trend = "falling significantly"
                elif second_half_avg < first_half_avg:
                    trend = "falling slightly"
                else:
                    trend = "stable"
                
                return f"""
                Parameter: {parameter}
                Latest value: {latest_value}
                Average over period: {avg_value:.2f}
                Range: {min_value:.2f} - {max_value:.2f}
                Trend: {trend}
                Number of readings: {len(values)}
                """
            except Exception as e:
                return f"Error analyzing historical data for {parameter}: {str(e)}"
        
        @tool
        def check_regulatory_compliance(parameter: str, value: float) -> str:
            """
            Check if a water quality parameter is within regulatory compliance.
            
            Args:
                parameter: The water quality parameter name
                value: The current value of the parameter
                
            Returns:
                Compliance status and relevant regulatory information
            """
            # Define regulatory limits (simplified for demonstration)
            regulatory_limits = {
                "pH": {"min": 6.5, "max": 8.5, "authority": "EPA"},
                "turbidity": {"max": 1.0, "unit": "NTU", "authority": "EPA"},
                "chlorine_residual": {"min": 0.2, "max": 4.0, "unit": "mg/L", "authority": "EPA"},
                "total_dissolved_solids": {"max": 500, "unit": "mg/L", "authority": "EPA"},
                "temperature": {"max": 30.0, "unit": "°C", "authority": "State DEP"},
                "pressure": {"min": 20, "unit": "PSI", "authority": "State DEP"},
                "flow_rate": {"info": "No direct regulatory limit, monitored for system performance"}
            }
            
            if parameter not in regulatory_limits:
                return f"No regulatory information available for parameter: {parameter}"
            
            limits = regulatory_limits[parameter]
            
            # Check compliance
            if "min" in limits and "max" in limits:
                if value < limits["min"]:
                    status = f"VIOLATION: {parameter} is {value}, below minimum limit of {limits['min']}"
                elif value > limits["max"]:
                    status = f"VIOLATION: {parameter} is {value}, exceeds maximum limit of {limits['max']}"
                else:
                    status = f"COMPLIANT: {parameter} is {value}, within limits ({limits['min']} - {limits['max']})"
            elif "min" in limits:
                if value < limits["min"]:
                    status = f"VIOLATION: {parameter} is {value}, below minimum limit of {limits['min']}"
                else:
                    status = f"COMPLIANT: {parameter} is {value}, above minimum limit of {limits['min']}"
            elif "max" in limits:
                if value > limits["max"]:
                    status = f"VIOLATION: {parameter} is {value}, exceeds maximum limit of {limits['max']}"
                else:
                    status = f"COMPLIANT: {parameter} is {value}, below maximum limit of {limits['max']}"
            else:
                status = f"INFO: {parameter} is {value}. {limits.get('info', '')}"
            
            unit = limits.get("unit", "")
            authority = limits.get("authority", "")
            
            return f"""
            {status}
            Unit: {unit}
            Regulatory authority: {authority}
            """
        
        @tool
        def recommend_treatment_adjustment(parameter: str, value: float, trend: str) -> str:
            """
            Recommend treatment adjustments based on a water quality parameter.
            
            Args:
                parameter: The water quality parameter name
                value: The current value of the parameter
                trend: Description of recent trend (rising, falling, stable)
                
            Returns:
                Recommended treatment adjustments, if any
            """
            # This would contain expert knowledge in a real system
            # Simplified for demonstration purposes
            
            recommendations = {
                "pH": {
                    "high": "Reduce caustic feed rate. Consider increasing carbon dioxide injection if available.",
                    "low": "Increase caustic or soda ash feed rate. Check alkalinity levels.",
                    "normal": "No adjustment needed. Continue monitoring."
                },
                "turbidity": {
                    "high": "Increase coagulant dose. Verify filter operation and consider reducing flow rate.",
                    "rising": "Proactively increase coagulant dose by 10%. Check source water for changes.",
                    "normal": "No adjustment needed. Continue monitoring."
                },
                "chlorine_residual": {
                    "high": "Reduce chlorine feed rate. Check for ammonia fluctuations if using chloramines.",
                    "low": "Increase chlorine feed rate. Check for possible contamination or high demand.",
                    "normal": "No adjustment needed. Continue monitoring."
                },
                "total_dissolved_solids": {
                    "high": "Check source water. Consider blending with alternate source if available.",
                    "rising": "Monitor closely. Prepare for potential blending if trend continues.",
                    "normal": "No adjustment needed. Continue routine monitoring."
                }
            }
            
            if parameter not in recommendations:
                return f"No standard treatment recommendations available for {parameter}."
            
            # Determine condition based on parameter
            condition = "normal"
            if parameter == "pH":
                if value > 8.0:
                    condition = "high"
                elif value < 7.0:
                    condition = "low"
            elif parameter == "turbidity":
                if value > 0.8:
                    condition = "high"
                elif trend.startswith("rising"):
                    condition = "rising"
            elif parameter == "chlorine_residual":
                if value > 2.0:
                    condition = "high"
                elif value < 0.5:
                    condition = "low"
            elif parameter == "total_dissolved_solids":
                if value > 400:
                    condition = "high"
                elif trend.startswith("rising"):
                    condition = "rising"
            
            return recommendations[parameter][condition]
        
        @tool
        def send_operator_alert(message: str, severity: Literal["info", "warning", "critical"] = "info") -> str:
            """
            Send an alert to the plant operators.
            
            Args:
                message: The alert message
                severity: Alert severity level (info, warning, critical)
                
            Returns:
                Confirmation that the alert was sent
            """
            # In a real implementation, this would send an email, SMS, or push notification
            # For demonstration purposes, we'll just log it
            print(f"[{severity.upper()} ALERT] {message}")
            
            # In reality we would integrate with alerting systems
            return f"Alert sent to operators with severity: {severity}"
            
        return [get_current_readings, get_historical_trends, check_regulatory_compliance, 
                recommend_treatment_adjustment, send_operator_alert]
    
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
                            content="""You are a water quality monitoring agent at a water treatment plant.
                            Your job is to monitor water quality parameters, detect anomalies, ensure regulatory
                            compliance, recommend treatment adjustments, and alert operators when necessary.
                            
                            Always follow this workflow when monitoring water quality:
                            1. Get the current water quality readings
                            2. Check for anomalies or concerning values
                            3. If a parameter is concerning, check its historical trend
                            4. Verify regulatory compliance for any concerning parameters
                            5. Recommend treatment adjustments if needed
                            6. Send operator alerts for any significant issues
                            
                            For concerning parameters, follow these guidelines:
                            - pH should normally be between 7.0-7.5
                            - Turbidity should be below 0.3 NTU
                            - Chlorine residual should be 0.5-2.0 mg/L
                            - Total dissolved solids should be below 400 mg/L
                            
                            Be proactive, autonomous, and thorough in your monitoring.
                            """
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
            
            # Special case for get_current_readings to store historical data
            if tool_call["name"] == "get_current_readings":
                observation = tool.invoke(tool_call["args"])
                
                # Store readings for historical analysis
                if isinstance(observation, dict) and "timestamp" in observation:
                    self.historical_readings.append(observation)
                    # Keep only the last 100 readings
                    if len(self.historical_readings) > 100:
                        self.historical_readings.pop(0)
            else:
                observation = tool.invoke(tool_call["args"])
                
            result.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
        return {"messages": result}
    
    def should_continue(self, state: MessagesState) -> str:
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
    
    def run(self, initial_prompt: str = "Start water quality monitoring", 
            monitoring_cycles: int = 1) -> Dict[str, Any]:
        """
        Execute the water quality monitoring agent for a specific number of cycles.
        
        Args:
            initial_prompt: The initial command to the agent
            monitoring_cycles: Number of monitoring cycles to run
            
        Returns:
            Dictionary with monitoring results and agent messages
        """
        messages = [HumanMessage(content=initial_prompt)]
        
        for cycle in range(monitoring_cycles):
            print(f"\n--- Monitoring Cycle {cycle+1} of {monitoring_cycles} ---")
            
            # Run the agent
            result = self.agent.invoke({"messages": messages})
            
            # Extract the last AI message for the next cycle
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                last_ai_message = ai_messages[-1]
                # Display the AI's summary/analysis
                print(f"\nAgent Analysis: {last_ai_message.content}")
            
            # Store the complete conversation
            messages = result["messages"]
            
            # Add a transition message for the next cycle if not the last cycle
            if cycle < monitoring_cycles - 1:
                messages.append(HumanMessage(content="Continue monitoring for the next cycle."))
                # Add a slight delay to simulate real-time monitoring
                time.sleep(1)
        
        return {
            "messages": messages,
            "historical_readings": self.historical_readings,
            "monitoring_cycles": monitoring_cycles
        }


def example_usage():
    """Demonstrate the usage of WaterQualityAgent."""
    
    # Create the water quality monitoring agent
    agent = WaterQualityAgent()
    
    # Visualize the agent (useful in notebooks)
    # display(agent.visualize())
    
    # Run the agent for 3 monitoring cycles
    print("Starting water quality monitoring agent...")
    result = agent.run(monitoring_cycles=3)
    
    # Display a summary
    print("\n--- Monitoring Summary ---")
    print(f"Completed {result['monitoring_cycles']} monitoring cycles")
    print(f"Collected {len(result['historical_readings'])} sensor readings")
    
    # Display final assessment
    ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
    if ai_messages:
        print("\nFinal Assessment:", ai_messages[-1].content)


if __name__ == "__main__":
    example_usage()
