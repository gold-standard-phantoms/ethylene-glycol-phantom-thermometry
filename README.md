# ethylene-glycol-phantom-thermometry

A Python package for multi-echo MR thermometry using ethylene glycol probes in phantoms.

This project provides data and analysis for ethylene glycol MR thermometry, intended for the 2026 ISMRM Abstract.

- Python 3.11+
- MIT License

## Installation

### Prerequisites

- Git
- Python 3.11 or higher
- `uv` (optional, but recommended for faster environment and package management)

You can install `uv` by following the official instructions: https://github.com/astral-sh/uv

### Development Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/gold-standard-phantoms/ethylene-glycol-phantom-thermometry.git
    cd ethylene-glycol-phantom-thermometry
    ```

2.  **Create a virtual environment and install dependencies:**

    The `pyproject.toml` file is configured to use `uv` as the build system and includes all dependencies.

    Using `uv`, you can create the virtual environment and install all required dependencies in one go. `uv` will automatically find the `pyproject.toml` and install the dependencies specified.

    ```bash
    # Install the virtual environment and standard dependencies using uv
    uv source --python=311

    # Install development dependencies using uv
    uv sync --all-extras

    # Install documentation dependencies
    uv sync --group docs
    ```

    This installs the project in editable mode along with all optional dependencies.

## Quick Start

### CLI Usage

The command-line interface runs the analsis on a dataset, with options for the analysis method, and the number of bootstrap iterations

- dataset: "1.5T" or "3T"
- method: "regionwise", "voxelwise", or "regionwise_bootstrap"
- bootstrap_iterations: integer. The number of bootstrap iterations to perform for the "regionwise_bootstrap" method

````bash
    # Display help information
    phantom-thermometry --help

    # Run the analysis
    phantom-thermometry dataset --method method --bootstrap-iterations N

    ```

## Development

### Running Tests

```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=pyruvate_kinetics --cov-report=term-missing

# Quick test run
uv run pytest tests/ -q
````

### Code Quality

```bash
# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/pyruvate_kinetics/

# Format code
uv run ruff format src/
```

### Docstring Style

This project uses **Google-style docstrings**. When contributing, please follow this format:

```python
def example_function(arg1: str, arg2: int) -> bool:
    """Brief description of the function.

    More detailed description if needed.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.

    Returns:
        Description of return value.

    Raises:
        ValueError: Description of when this error is raised.
    """
```

### Building Documentation

```bash
# Build HTML docs
uv run mkdocs build

# Serve docs locally
uv run mkdocs serve
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`uv run pytest`)
4. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Commit Message Format

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification. Commit messages should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**

- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, missing semicolons, etc.)
- `refactor:` - Code changes that neither fix bugs nor add features
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks, dependency updates, etc.
