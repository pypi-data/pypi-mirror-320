# **QuantStream**

QuantStream is a Python-based financial modeling preperation platform designed to interact with real-time financial data via APIs, including the Financial Modeling Prep (FMP) API. The platform provides tools for model training, real-time data integration, and visualization. It is designed to be a central data structure for financial modeling and analysis based on Xarray, allowing users to easily access and manipulate financial data for their projects.

## **Features**

- **FMP API Wrapper**: Integration with the FMP API for fetching financial data.
- **Data Visualization**: Display and interact with real-time financial data.
- **Data Export**: Download financial data in various formats such as CSV.
- **Data Storage**: Store financial data easily in a SQLite databases.
- **Extensible Architecture**: Easily add new models or financial data providers.

## **Installation**

### **Requirements**

- Python 3.11 or higher
- `uv` package for environment and dependency management
- `ruff` for linting

### **Setup**

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/quantstream.git
   cd quantstream
   ```

1. Install `uv` and sync dependencies:

   ```bash
   curl -sSL https://install.astral.sh | sh
   uv sync --all-extras --dev
   ```

1. Set up the environment variable for your API key:

   ```bash
   export FMP_API_KEY=your_api_key_here
   ```

1. Run the application:

   ```bash
   uv run python -m quantstream
   ```

## **Usage**

## **Development Workflow**

### **Code Style and Linting**

We use `ruff` for code linting. You can check for any style issues by running:

```bash
uv run ruff check .
```

### **Running Tests**

Tests are managed using `pytest`. You can run all tests with:

```bash
uv run pytest tests/
```

### **Pre-commit Hooks**

This project uses `pre-commit` hooks to enforce code quality. Install the hooks by running:

```bash
pre-commit install
```

## **Contributing**

We welcome contributions! Please see the [CONTRIBUTING.md](./CONTRIBUTING.md) file for guidelines.

## **License**

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
