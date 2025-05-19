# Agent Development
The following is the structure of this project
```
agent-development/
│
├── pyproject.toml                   # Updated package configuration
│
├── src/
│   ├── agent_dev/                   # Original agent development examples
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── augmented_llm.py
│   │   └── ...
│   │
│   └── water_industry/                     # New water industry implementations
│       ├── __init__.py                     # Package initialization with imports
│       ├── utils.py                        # Utility functions for water industry
│       ├── example_data.py                 # Sample data for demonstrations
│       ├── water_quality_workflow.py       # Pattern 1: Prompt Chaining
│       ├── treatment_monitoring.py         # Pattern 2: Parallelization
│       ├── customer_service_system.py      # Pattern 3: Routing
│       ├── drought_management_system.py    # Pattern 4: Orchestrator-Worker
│       └── treatment_optimizer.py          # Pattern 5: Evaluator-Optimizer
│
├── docs/
│   ├── water_industry/                     # Educational resources
│   │   ├── water-quality-md.md             # Guide for Pattern 1
│   │   ├── treatment-monitoring-md.md      # Guide for Pattern 2
│   │   ├── customer-service-md.md          # Guide for Pattern 3
│   │   ├── drought-management-md.md        # Guide for Pattern 4
│   │   ├── treatment-optimizer-md.md       # Guide for Pattern 5
│   │   └── workshop-guide.md               # Workshop facilitation guide
│   │
│   └── README.md                           # Overview of water industry patterns
│
└── notebooks/                       # For workshop demonstrations
    └── water_industry_demos/
        ├── 1_water_quality_workflow.ipynb
        ├── 2_treatment_monitoring.ipynb
        ├── 3_customer_service_system.ipynb
        ├── 4_drought_management_system.ipynb
        └── 5_treatment_optimizer.ipynb
```