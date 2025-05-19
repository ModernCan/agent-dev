# -*- coding: utf-8 -*-
"""Example data for water industry AI patterns.

This module provides sample data sets for testing and demonstrating
the water industry AI patterns.
"""

import datetime

# Sample water quality parameters for testing the Water Quality Analysis workflow
sample_water_quality_parameters = {
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

# Sample treatment plant data for the Treatment Plant Monitoring workflow
sample_treatment_plant_data = {
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

# Sample customer inquiries for the Customer Service System
sample_customer_inquiries = [
    "I think my water bill is too high this month. Can you explain the charges?",
    "There's water gushing out of a pipe on Main Street near Oak Avenue!",
    "My water has a strange chlorine smell and tastes funny.",
    "What rebates do you offer for installing water-efficient toilets?",
    "I'm building a new house and need to set up water service.",
    "What are your office hours?",
    "I noticed brown water coming from my faucet this morning.",
    "I'll be away for 3 months, can I temporarily stop my water service?",
    "My neighbor's sprinkler has been running for 2 days straight during water restrictions.",
    "I need to know the water hardness in my area for a new appliance."
]

# Sample drought conditions for the Drought Management System
sample_drought_conditions = {
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

# Sample treatment parameters for the Treatment Process Optimization
sample_treatment_parameters = {
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

# Sample optimization goals for the Treatment Process Optimization
sample_optimization_goals = {
    "finished_water_turbidity": "<0.1 NTU 95% of time, never >0.3 NTU",
    "disinfection_byproducts": "THMs <40 μg/L, HAA5 <30 μg/L",
    "chemical_consumption": "Reduce coagulant usage by 15% without compromising quality",
    "energy_efficiency": "Reduce energy consumption by 10%",
    "water_loss": "Improve filter run times by 20%, reduce backwash water to <2% of production",
    "operational_stability": "Maintain stable operation across seasonal water quality variations",
    "capital_constraints": "Optimize existing infrastructure, minimal new construction"
}

# Function to generate a time series of water quality data


def generate_water_quality_time_series(days: int = 30, parameter: str = "turbidity",
                                       base_value: float = 1.0,
                                       variance: float = 0.5) -> dict:
    """
    Generate a time series of water quality data for demonstration.

    Args:
        days: Number of days in the time series
        parameter: Water quality parameter name
        base_value: Base value for the parameter
        variance: Maximum random variance from base value

    Returns:
        Dictionary with dates as keys and parameter values as values
    """
    import random
    from datetime import datetime, timedelta

    start_date = datetime.now() - timedelta(days=days)
    time_series = {}

    for day in range(days):
        date = start_date + timedelta(days=day)
        # Generate a value with some randomness and a slight trend
        trend_factor = 1.0 + (day / days) * 0.2  # Slight upward trend
        random_factor = random.uniform(-variance, variance)
        value = base_value * trend_factor + random_factor
        # Ensure no negative values
        value = max(0.01, value)
        time_series[date.strftime('%Y-%m-%d')] = round(value, 2)

    return time_series


# Sample operational metrics for utility performance
sample_utility_metrics = {
    "water_production": {
        "value": 12.45,
        "unit": "MGD",
        "description": "Average daily water production",
        "trend": "+3% from previous month"
    },
    "energy_intensity": {
        "value": 1820,
        "unit": "kWh/MG",
        "description": "Energy used per million gallons treated",
        "trend": "-5% from previous month"
    },
    "customer_complaints": {
        "value": 23,
        "unit": "complaints/month",
        "description": "Water quality complaints received",
        "trend": "+15% from previous month"
    },
    "non_revenue_water": {
        "value": 12.3,
        "unit": "%",
        "description": "Percentage of water lost or unbilled",
        "trend": "No change from previous month"
    },
    "chemical_cost": {
        "value": 104.50,
        "unit": "$/MG",
        "description": "Chemical cost per million gallons",
        "trend": "+2% from previous month"
    }
}
