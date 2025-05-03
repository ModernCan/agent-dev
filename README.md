# Agent Development
The following is the structure of this project
```
my_project/
├── pyproject.toml
├── README.md
├── .venv/                    # Local Poetry environment (if enabled)
├── notebooks/                # 🧪 Exploratory notebooks
│   ├── 01_data_exploration.ipynb
│   └── 02_model_training.ipynb
├── data/                     # 📊 Input or output data files
│   ├── raw/
│   └── processed/
├── scripts/                  # 🛠️ Standalone run scripts
│   └── run_pipeline.py
├── tests/                    # 🧪 Unit tests
│   └── test_data_loader.py
├── src/                      # 📦 Installable package
│   └── agent_development/
│       ├── __init__.py
│       ├── main.py
│       ├── data_loader.py
│       ├── models/
│       ├── utils/
├── .gitignore
└── .env                      # 🔐 Env vars (if needed)
```