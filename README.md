# Researcher

A Python research project managed with Poetry.

## Setup

This project uses Poetry for dependency management and conda for environment management.

### Prerequisites

- Miniconda or Anaconda installed
- Python 3.11+

### Installation

1. Create and activate the conda environment:
   ```bash
   conda create -n researcher python=3.11
   conda activate researcher
   ```

2. Install Poetry (if not already installed):
   ```bash
   pip install poetry
   ```

3. Install project dependencies:
   ```bash
   poetry install
   ```

### Development

To add new dependencies:
```bash
poetry add package-name
```

To add development dependencies:
```bash
poetry add --group dev package-name
```

To run the project:
```bash
poetry run python src/researcher/main.py
```

## Configuration

This project uses a **hybrid configuration approach** combining both `.env` files and YAML configuration for maximum flexibility and security.

### Configuration Strategy

- **`.env` file**: Contains sensitive data (API keys) and environment-specific settings
- **`config.yml`**: Contains application structure, defaults, and static configuration
- **Environment variables**: Override both .env and YAML values (highest priority)

### Setting up the Hybrid Configuration

1. **Set up the .env file** (for sensitive data):
   ```bash
   cp sample.env .env
   # Edit .env with your actual API keys
   ```

2. **Configure YAML structure** (already done):
   ```yaml
   # config.yml references .env variables
   api:
     openai:
       api_key: ${OPENAI_API_KEY:default_key}  # From .env
       model: gpt-4                            # Static in YAML
   ```

### Configuration Priority (highest to lowest)

1. **Environment variables** (e.g., `export OPENAI_API_KEY=...`)
2. **`.env` file values**
3. **YAML defaults**

### Example .env file structure

```bash
# API Keys (sensitive - never commit)
OPENAI_API_KEY=sk-your-actual-key-here
BRIGHT_DATA_API_KEY=your-key-here

# Environment settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### Using Configuration in Code

```python
from researcher.config import config

# Get API keys
openai_key = config.get_api_key('openai')
bright_data_key = config.get_api_key('bright_data')

# Get full configuration
openai_config = config.get_openai_config()
bright_data_config = config.get_bright_data_config()

# Check environment
if config.is_development():
    print("Running in development mode")
```

## Project Structure

```
researcher/
├── src/
│   └── researcher/
│       ├── __init__.py
│       ├── main.py
│       └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_config.py
├── config.yml              # Configuration file
├── config.example.yml      # Example configuration
├── pyproject.toml
└── README.md
``` 