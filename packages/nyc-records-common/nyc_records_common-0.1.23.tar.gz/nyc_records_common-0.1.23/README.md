# NYC Records Packages

[![PyPI version](https://badge.fury.io/py/nyc-records-common.svg)](https://pypi.org/project/nyc-records-common/)

Common utilities for NYC Records projects.

## Prerequisites
- Python 3.11+
- pip
- virtualenv

## Installation

1. Create and activate virtual environment:
```bash
cd packages
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements/dev.txt
pip install -r requirements/prod.txt
pip install -e .
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

### Testing
```
pytest tests/ -v                  # Command line
pytest tests/ --cov=src          # With coverage
```

### Code Formating
```bash
black src/ tests/                # Format code
isort src/ tests/                # Sort imports
flake8 src/ tests/              # Check style
mypy src/                       # Type checking
pytest tests/                   # Run tests
pylint --rcfile=.pylintrc src/nyc_records_common
pylint --rcfile=.pylintrc src/nyc_records_db
```
