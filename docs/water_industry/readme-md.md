# Water Industry AI Patterns

This repository contains implementations of five essential AI workflow and agent patterns, applied specifically to water industry use cases. These examples demonstrate how modern AI techniques can be used to solve complex challenges in water management, treatment, conservation, and customer service.

## Project Organization

The examples are organized into two main directories:

- `/src/water_industry/` - Contains Python implementations of each pattern
- `/docs/water_industry/` - Contains educational markdown files explaining each pattern

## Patterns Overview

Each example demonstrates a different AI pattern applied to a water industry challenge:

1. **Water Quality Analysis** (Prompt Chaining): Sequential analysis of water quality data through multiple specialized steps
2. **Treatment Plant Monitoring** (Parallelization): Concurrent analysis of different aspects of treatment plant operations
3. **Customer Service System** (Routing): Smart classification and routing of customer inquiries to specialized handlers
4. **Drought Management System** (Orchestrator-Worker): Coordinated planning and delegation of drought response actions
5. **Treatment Process Optimization** (Evaluator-Optimizer): Iterative improvement of treatment processes through feedback loops

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)

### Installation

1. Clone this repository
2. Install dependencies with Poetry:
   ```
   poetry install
   ```
3. Set up your API keys in the `.env` file (see `.env.example`)

### Running the Examples

Each pattern can be run independently:

```python
# Example: Running the Water Quality Analysis workflow
from water_industry.water_quality_workflow import WaterQualityWorkflow
import example_data

workflow = WaterQualityWorkflow()
result = workflow.run(example_data.water_sample)
print(result["final_report"])
```

## Example Use Cases

Here's how these patterns apply to common water industry challenges:

### 1. Water Quality Analysis (Prompt Chaining)

**Use Case**: Processing water quality samples through sequential analysis stages

**Benefits**:
- Break complex analysis into manageable steps
- Apply quality gates to ensure reliable results
- Build comprehensive understanding through progressive analysis

### 2. Treatment Plant Monitoring (Parallelization)

**Use Case**: Comprehensive monitoring of treatment plant operations across multiple domains

**Benefits**:
- Analyze chemical, biological, operational, and energy aspects simultaneously
- Identify interdependencies between different operational areas
- Maintain balanced attention across all critical systems

### 3. Customer Service System (Routing)

**Use Case**: Efficiently handling diverse customer inquiries at water utilities

**Benefits**:
- Direct inquiries to specialized knowledge domains
- Prioritize emergency issues appropriately
- Provide consistent, domain-specific responses

### 4. Drought Management System (Orchestrator-Worker)

**Use Case**: Coordinated drought response planning across utility departments

**Benefits**:
- Develop comprehensive strategies across all operational areas
- Ensure coordination between supply, operations, communications, and conservation
- Maintain strategic alignment while leveraging departmental expertise

### 5. Treatment Process Optimization (Evaluator-Optimizer)

**Use Case**: Iteratively improving water treatment processes until goals are achieved

**Benefits**:
- Continuously refine processes based on performance evaluation
- Balance multiple optimization goals (quality, efficiency, cost)
- Maintain a history of improvements for transparency and learning

## Educational Resources

Each pattern includes a detailed educational markdown file explaining:

- The concept and principles of the pattern
- How it's applied to water industry challenges
- The implementation architecture
- Business value and benefits
- Practical applications and considerations

These files are intended for sharing with management, executives, and stakeholders to explain the value and application of these AI patterns in the water industry.

## Extending the Examples

These examples provide a foundation that can be extended in several ways:

1. **Integration with Real Data Sources**: Connect to SCADA systems, laboratory databases, or customer information systems
2. **Additional Water Industry Patterns**: Develop examples for leak detection, infrastructure planning, or regulatory compliance
3. **Hybrid Human-AI Workflows**: Add human-in-the-loop components for critical decisions
4. **Multi-Modal Inputs**: Incorporate image processing for visual inspection data
5. **Deployment Patterns**: Add examples of production deployment in utility environments

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
