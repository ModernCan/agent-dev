"""
Water Industry AI Patterns Package.

This package contains implementations of various AI workflow and agent patterns
applied specifically to water industry use cases, demonstrating how modern AI
techniques can solve complex challenges in water management.
"""

# Core pattern implementations
from .water_quality_workflow import WaterQualityWorkflow, WaterQualityState
from .treatment_monitoring import TreatmentMonitoring, MonitoringState
from .customer_service_system import CustomerServiceSystem, CustomerServiceState, InquiryRoute
from .drought_management_system import DroughtManagementSystem, DroughtResponseState, DroughtAction, DroughtPlan
from .treatment_optimizer import TreatmentOptimizer, OptimizationState, ProcessEvaluation

# Common utilities
from .utils import (
    initialize_llm,
    visualize_workflow,
    format_parameters,
    save_report_as_pdf,
    load_water_sample_data,
    generate_report_chart
)

# Example data loaders
from .example_data import (
    sample_water_quality_parameters,
    sample_treatment_plant_data,
    sample_customer_inquiries,
    sample_drought_conditions,
    sample_treatment_parameters,
    sample_optimization_goals
)

__all__ = [
    # Core pattern implementations
    'WaterQualityWorkflow',
    'WaterQualityState',
    'TreatmentMonitoring',
    'MonitoringState',
    'CustomerServiceSystem',
    'CustomerServiceState',
    'InquiryRoute',
    'DroughtManagementSystem',
    'DroughtResponseState',
    'DroughtAction',
    'DroughtPlan',
    'TreatmentOptimizer',
    'OptimizationState',
    'ProcessEvaluation',
    
    # Common utilities
    'initialize_llm',
    'visualize_workflow',
    'format_parameters',
    'save_report_as_pdf',
    'load_water_sample_data',
    'generate_report_chart',
    
    # Example data loaders
    'sample_water_quality_parameters',
    'sample_treatment_plant_data',
    'sample_customer_inquiries',
    'sample_drought_conditions',
    'sample_treatment_parameters',
    'sample_optimization_goals'
]
