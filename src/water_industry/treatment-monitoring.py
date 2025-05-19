# -*- coding: utf-8 -*-
"""Water Treatment Monitoring Module (Parallelization).

This module demonstrates the parallelization pattern applied to comprehensive
water treatment plant monitoring, running multiple independent analyses simultaneously.
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


class MonitoringState(TypedDict):
    """Type definition for the water treatment monitoring state."""
    plant_data: Dict[str, Any]         # Complete plant operational data
    chemical_analysis: str             # Analysis of chemical parameters
    biological_assessment: str         # Analysis of biological parameters
    operational_evaluation: str        # Analysis of operational parameters
    energy_efficiency_report: str      # Analysis of energy usage and efficiency
    consolidated_report: str           # Combined comprehensive monitoring report


class TreatmentMonitoring:
    """
    Implements the parallelization pattern for comprehensive water treatment monitoring.

    This class demonstrates how to perform multiple independent analyses of different
    aspects of water treatment plant data simultaneously, then combine the results
    into a unified assessment.
    """

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-latest",
        api_key: Optional[str] = None
    ):
        """
        Initialize the TreatmentMonitoring with specified model.

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
        Builds the parallel workflow for water treatment monitoring.

        Returns:
            A compiled LangGraph StateGraph representing the workflow
        """
        # Build workflow
        monitoring_workflow = StateGraph(MonitoringState)

        # Add nodes for each parallel analysis
        monitoring_workflow.add_node("analyze_chemical", self.analyze_chemical)
        monitoring_workflow.add_node(
            "analyze_biological", self.analyze_biological)
        monitoring_workflow.add_node(
            "analyze_operational", self.analyze_operational)
        monitoring_workflow.add_node("analyze_energy", self.analyze_energy)
        monitoring_workflow.add_node(
            "consolidate_results", self.consolidate_results)

        # Add edges to connect nodes with parallelization
        monitoring_workflow.add_edge(START, "analyze_chemical")
        monitoring_workflow.add_edge(START, "analyze_biological")
        monitoring_workflow.add_edge(START, "analyze_operational")
        monitoring_workflow.add_edge(START, "analyze_energy")
        monitoring_workflow.add_edge("analyze_chemical", "consolidate_results")
        monitoring_workflow.add_edge(
            "analyze_biological", "consolidate_results")
        monitoring_workflow.add_edge(
            "analyze_operational", "consolidate_results")
        monitoring_workflow.add_edge("analyze_energy", "consolidate_results")
        monitoring_workflow.add_edge("consolidate_results", END)

        # Compile workflow
        return monitoring_workflow.compile()

    def analyze_chemical(self, state: MonitoringState) -> Dict[str, str]:
        """
        Analyzes chemical treatment aspects of plant data.

        Args:
            state: Current workflow state containing plant data

        Returns:
            Dictionary with chemical analysis to be added to the state
        """
        # Extract relevant chemical data
        chemical_data = {
            k: v for k, v in state['plant_data'].items()
            if k in ['ph_levels', 'chlorine_levels', 'coagulant_dosage', 'fluoride_levels',
                     'alkalinity', 'hardness', 'toc', 'disinfection_byproducts']
        }

        # Format the data for the LLM
        parameters_text = "\n".join(
            [f"- {param}: {value}" for param, value in chemical_data.items()])

        prompt = f"""Analyze the following chemical treatment parameters from a water treatment plant:

{parameters_text}

Provide a detailed analysis covering:
1. Effectiveness of chemical treatments
2. Dosage optimization recommendations
3. Chemical balance assessment
4. Potential issues or concerns
5. Compliance with chemical treatment standards
"""

        msg = self.llm.invoke(prompt)
        return {"chemical_analysis": msg.content}

    def analyze_biological(self, state: MonitoringState) -> Dict[str, str]:
        """
        Analyzes biological treatment aspects of plant data.

        Args:
            state: Current workflow state containing plant data

        Returns:
            Dictionary with biological assessment to be added to the state
        """
        # Extract relevant biological data
        biological_data = {
            k: v for k, v in state['plant_data'].items()
            if k in ['bacteria_count', 'coliform_levels', 'microscopic_analysis',
                     'biological_oxygen_demand', 'biological_filter_performance',
                     'algae_levels', 'biofilm_formation']
        }

        # Format the data for the LLM
        parameters_text = "\n".join(
            [f"- {param}: {value}" for param, value in biological_data.items()])

        prompt = f"""Analyze the following biological parameters from a water treatment plant:

{parameters_text}

Provide a detailed biological assessment covering:
1. Microbial contamination risk
2. Biological treatment effectiveness
3. Concerning biological indicators
4. Biofilm management recommendations
5. Biological stability of treated water
"""

        msg = self.llm.invoke(prompt)
        return {"biological_assessment": msg.content}

    def analyze_operational(self, state: MonitoringState) -> Dict[str, str]:
        """
        Analyzes operational aspects of plant data.

        Args:
            state: Current workflow state containing plant data

        Returns:
            Dictionary with operational evaluation to be added to the state
        """
        # Extract relevant operational data
        operational_data = {
            k: v for k, v in state['plant_data'].items()
            if k in ['flow_rates', 'retention_time', 'filter_performance', 'backwash_frequency',
                     'pressure_readings', 'valve_positions', 'pump_status', 'turbidity_readings',
                     'maintenance_logs', 'alarm_history']
        }

        # Format the data for the LLM
        parameters_text = "\n".join(
            [f"- {param}: {value}" for param, value in operational_data.items()])

        prompt = f"""Analyze the following operational parameters from a water treatment plant:

{parameters_text}

Provide a detailed operational evaluation covering:
1. Process efficiency assessment
2. Equipment performance analysis
3. Operational bottlenecks and constraints
4. Maintenance recommendations
5. Process control optimization opportunities
"""

        msg = self.llm.invoke(prompt)
        return {"operational_evaluation": msg.content}

    def analyze_energy(self, state: MonitoringState) -> Dict[str, str]:
        """
        Analyzes energy efficiency aspects of plant data.

        Args:
            state: Current workflow state containing plant data

        Returns:
            Dictionary with energy efficiency report to be added to the state
        """
        # Extract relevant energy data
        energy_data = {
            k: v for k, v in state['plant_data'].items()
            if k in ['power_consumption', 'pump_efficiency', 'motor_load_factors',
                     'hvac_usage', 'lighting_consumption', 'peak_demand_periods',
                     'renewable_energy_contribution', 'energy_cost_data']
        }

        # Format the data for the LLM
        parameters_text = "\n".join(
            [f"- {param}: {value}" for param, value in energy_data.items()])

        prompt = f"""Analyze the following energy usage parameters from a water treatment plant:

{parameters_text}

Provide a detailed energy efficiency assessment covering:
1. Overall energy consumption patterns
2. High-consumption processes identification
3. Energy efficiency metrics and benchmarks
4. Cost-saving opportunities
5. Renewable energy integration potential
"""

        msg = self.llm.invoke(prompt)
        return {"energy_efficiency_report": msg.content}

    def consolidate_results(self, state: MonitoringState) -> Dict[str, str]:
        """
        Consolidates all parallel analyses into a comprehensive report.

        Args:
            state: Current workflow state containing all analyses

        Returns:
            Dictionary with consolidated report to be added to the state
        """
        prompt = f"""Create a consolidated water treatment plant monitoring report based on the following specialized analyses:

CHEMICAL ANALYSIS:
{state['chemical_analysis']}

BIOLOGICAL ASSESSMENT:
{state['biological_assessment']}

OPERATIONAL EVALUATION:
{state['operational_evaluation']}

ENERGY EFFICIENCY REPORT:
{state['energy_efficiency_report']}

Provide a comprehensive plant status report that:
1. Summarizes key findings from each area
2. Identifies critical issues requiring immediate attention
3. Highlights interconnected issues across different aspects
4. Provides prioritized recommendations
5. Suggests an integrated optimization approach
"""

        msg = self.llm.invoke(prompt)
        return {"consolidated_report": msg.content}

    def visualize(self) -> Image:
        """
        Generate a visualization of the workflow graph.

        Returns:
            IPython Image object containing the workflow diagram
        """
        return Image(self.workflow.get_graph().draw_mermaid_png())

    def run(self, plant_data: Dict[str, Any]) -> MonitoringState:
        """
        Execute the treatment monitoring workflow with the given plant data.

        Args:
            plant_data: Dictionary of water treatment plant operational data

        Returns:
            The final state containing all analyses and the consolidated report
        """
        state = self.workflow.invoke({"plant_data": plant_data})
        return state


def example_usage():
    """Demonstrate the usage of TreatmentMonitoring."""

    # Example water treatment plant data
    plant_data = {
        # Chemical parameters
        "ph_levels": "Influent: 7.1, Post-coagulation: 6.4, Final: 7.3",
        "chlorine_levels": "Pre-contact tank: 1.8 mg/L, Post-contact tank: 1.2 mg/L, Distribution: 0.9 mg/L",
        "coagulant_dosage": "Alum: 25 mg/L, Current feed rate: 120 L/hour",
        "fluoride_levels": "0.7 mg/L",
        "alkalinity": "Raw: 110 mg/L as CaCO3, Finished: 85 mg/L as CaCO3",
        "hardness": "140 mg/L as CaCO3",
        "toc": "Raw: 3.8 mg/L, Finished: 2.1 mg/L",
        "disinfection_byproducts": "THMs: 55 μg/L, HAA5: 32 μg/L",

        # Biological parameters
        "bacteria_count": "HPC: 10 CFU/mL",
        "coliform_levels": "Total coliform: None detected, E. coli: None detected",
        "microscopic_analysis": "Occasional diatoms observed, no cyanobacteria",
        "biological_oxygen_demand": "Raw: 3.2 mg/L, Effluent: 1.1 mg/L",
        "biological_filter_performance": "Head loss: 1.2 ft, Run time: 72 hours since backwash",
        "algae_levels": "Raw reservoir: Minimal presence, primarily green algae",
        "biofilm_formation": "Pipe coupons show minimal biofilm development",

        # Operational parameters
        "flow_rates": "Plant inflow: 18 MGD, Filter loading rates: 2.1 gpm/ft²",
        "retention_time": "Sedimentation: 3.5 hours, Contact tank: 45 minutes",
        "filter_performance": "Turbidity: 0.08 NTU, Particle counts <2μm: 22/mL",
        "backwash_frequency": "Filter 1: 70 hours, Filter 2: 65 hours, Filter 3: 72 hours",
        "pressure_readings": "Filter influent: 5.2 psi, Filter effluent: 3.8 psi",
        "valve_positions": "All automated valves operating normally, Valve 23B sluggish response",
        "pump_status": "High-service pumps at 72% capacity, Raw water pumps at 65% capacity",
        "turbidity_readings": "Raw: 5.2 NTU, Post-sedimentation: 1.8 NTU, Filtered: 0.08 NTU",
        "maintenance_logs": "Pump #3 maintenance performed 2 days ago, UV system calibrated last week",
        "alarm_history": "Low chlorine alarm triggered twice in past week, High turbidity alarm once",

        # Energy parameters
        "power_consumption": "Total plant: 25,000 kWh/day, Peak demand: 1,200 kW",
        "pump_efficiency": "Raw water pumps: 78%, High-service pumps: 82%, Backwash pumps: 75%",
        "motor_load_factors": "Average across plant: 82% of rated capacity",
        "hvac_usage": "12% of total plant energy consumption",
        "lighting_consumption": "5% of total plant energy consumption",
        "peak_demand_periods": "6:00-9:00 AM and 4:00-7:00 PM",
        "renewable_energy_contribution": "Solar array providing 8% of daily consumption",
        "energy_cost_data": "$0.092/kWh average, Demand charges: $14.50/kW"
    }

    # Create the monitoring workflow
    monitoring = TreatmentMonitoring()

    # Visualize the workflow (useful in notebooks)
    # display(monitoring.visualize())

    # Run the workflow
    result = monitoring.run(plant_data)

    # Print final report
    print("WATER TREATMENT PLANT MONITORING REPORT:")
    print("=======================================")
    print(result["consolidated_report"])


if __name__ == "__main__":
    example_usage()
