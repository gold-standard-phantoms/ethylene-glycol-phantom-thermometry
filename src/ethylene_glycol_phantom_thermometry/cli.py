import typer
from pathlib import Path
from enum import Enum

from ethylene_glycol_phantom_thermometry.analysis import analysis
from ethylene_glycol_phantom_thermometry.util import get_project_root

app = typer.Typer()


class Dataset(str, Enum):
    """The dataset to analyze."""

    T1_5 = "1.5T"
    T3 = "3T"


class Method(str, Enum):
    """The analysis method to use."""

    REGIONWISE = "regionwise"
    VOXELWISE = "voxelwise"
    REGIONWISE_BOOTSTRAP = "regionwise_bootstrap"


@app.command()
def main(
    dataset: Dataset = typer.Argument(
        ..., help="The dataset to analyze, either '1.5T' or '3T'."
    ),
    method: Method = typer.Option(
        Method.REGIONWISE,
        "--method",
        "-m",
        help="The analysis method to use.",
        case_sensitive=False,
    ),
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

    analysis(data_dir=data_dir, method=method.value)


if __name__ == "__main__":
    app()
