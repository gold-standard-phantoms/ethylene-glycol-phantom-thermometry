import typer
from pathlib import Path
from enum import Enum
from typing import Annotated

from ethylene_glycol_phantom_thermometry.analysis import analysis, Method
from ethylene_glycol_phantom_thermometry.util import get_project_root

app = typer.Typer()


class Dataset(str, Enum):
    """The dataset to analyze."""

    T1_5 = "1.5T"
    T3 = "3T"


@app.command()
def main(
    dataset: Annotated[
        Dataset,
        typer.Argument(..., help="The dataset to analyze, either '1.5T' or '3T'."),
    ],
    method: Annotated[
        Method,
        typer.Option(
            "--method",
            "-m",
            help="The analysis method to use: 'regionwise', 'voxelwise', or 'regionwise_bootstrap'",
            case_sensitive=False,
        ),
    ] = Method.REGIONWISE,
    bootstrap_iterations: Annotated[
        int,
        typer.Option(
            "--bootstrap-iterations",
            "-b",
            help="Number of bootstrap iterations (only used if method is 'regionwise_bootstrap')",
            min=1,
        ),
    ] = 10,
) -> None:
    """
    Run the ethylene glycol phantom thermometry analysis.
    """
    project_root = get_project_root()
    data_dir = project_root / "data" / dataset.value
    print(f"Constructed data directory path: {data_dir}")

    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}")
        raise typer.Exit(code=1)

    analysis(data_dir=data_dir, method=method, n_bootstrap=bootstrap_iterations)


if __name__ == "__main__":
    app()
