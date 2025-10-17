# ethylene-glycol-phantom-thermometry

A Python package for multi-echo MR thermometry using ethylene glycol probes in phantoms.

This project provides data and analysis for ethylene glycol MR thermometry, intended for the 2026 ISMRM Abstract.

- Python 3.11+
- MIT License

## Getting Started

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
    uv source --python311

    # Install development dependencies using uv
    uv sync --all-extras

    # Install documentation dependencies
    uv sync --group docs
    ```

    This installs the project in editable mode along with all optional dependencies.
