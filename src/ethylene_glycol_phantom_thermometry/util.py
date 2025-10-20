import ast  # Used to safely evaluate the string representation of the list
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


def get_project_root() -> Path:
    """
    Finds the project root directory by searching for a marker file (e.g., pyproject.toml).

    Returns:
        The path to the project root directory.
    """
    # Start from the current file's directory and go up
    current_path = Path(__file__).resolve().parent
    while current_path and not (current_path / "pyproject.toml").exists():
        current_path = current_path.parent
    if not current_path:
        raise FileNotFoundError("Project root with 'pyproject.toml' not found.")
    return current_path


@dataclass
class SeriesData:
    """A dataclass to hold study data."""

    patient_name: str
    study_id: str
    series_no: int
    run: int
    te_ms: list[float] = field(default_factory=list)
    nifti_file: Path | None = field(default=None)


@dataclass
class BidsSidecar:
    """A dataclass for BIDS sidecar information."""

    filename: Path
    study_id: str
    series_no: int
    sidecar: dict


def load_bids_sidecars_from_directory(directory: Path) -> list[BidsSidecar]:
    """
    Finds all .json files in a directory, loads them into BidsSidecar objects.
    Assumes BIDS-like filenames, e.g., '..._ses-1_..._run-1_...json'

    Args:
        directory: The directory to search for .json files.

    Returns:
        A list of BidsSidecar objects.
    """
    sidecar_files = list(directory.glob("*.json"))
    sidecars = []
    for p in sidecar_files:
        with open(p) as f:
            data: dict = json.load(f)

        study_id = data.get("StudyInstanceUID", "unknown_study")
        series_no = data.get("SeriesNumber", -1)

        sidecars.append(
            BidsSidecar(
                filename=p,
                study_id=study_id,
                series_no=series_no,
                sidecar=data,
            )
        )
    return sidecars


def load_series_info(filename: Path) -> list[SeriesData]:
    """
    Reads an Excel spreadsheet and loads each row into a SeriesData object.

    The spreadsheet must have the following columns:
    - patient_name: The name of the patient
    - study_id: The study ID
    - series_no: The series number
    - run: The run number
    - te_ms: The TE values in ms, stored as a string representation of a list (e.g., '[1.2, 3.4]')

    Args:
        filename: The path to the Excel file.

    Returns:
        A list of SeriesData objects.
    """
    try:
        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(filename)

        patient_records = []

        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            # Safely parse the string '[1.2, 3.4]' into a list of floats
            te_ms_list = ast.literal_eval(row["te_ms"]) if isinstance(row["te_ms"], str) else []

            # Create a dataclass instance and append it to our list
            record = SeriesData(
                patient_name=row["patient_name"],
                study_id=row["study_id"],
                series_no=int(row["series_no"]),
                run=int(row["run"]),
                te_ms=te_ms_list,
            )
            patient_records.append(record)

        return patient_records

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def export_unique_te_arrays(data: list[SeriesData], output_dir: Path, te_units: str = "ms"):
    """
    Finds unique te_ms arrays and exports each to a separate text file.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    divisor = 1.0
    if te_units.lower() == "s":
        divisor = 1000.0

    # Use a set of tuples to find unique lists (lists aren't hashable, tuples are)
    unique_arrays = set(tuple(item.te_ms) for item in data)
    # divide by divisor
    unique_arrays = set(tuple(value / divisor for value in te_tuple) for te_tuple in unique_arrays)

    print(f"\nFound {len(unique_arrays)} unique te_ms arrays. Exporting to '{output_dir}/'...")

    # Loop through the unique arrays and save each to a file
    for i, te_tuple in enumerate(unique_arrays, 1):
        filename = os.path.join(output_dir, f"unique_te_{i}.txt")
        with open(filename, "w") as f:
            for value in te_tuple:
                f.write(f"{value}\n")
        print(f" -> Saved {filename}")


if __name__ == "__main__":
    # Check if a filename was provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python read_spreadsheet.py <filename.xlsx>")
        sys.exit(1)

    # Get the filename from the command line
    excel_file = Path(sys.argv[1])

    # Check if the file exists
    if not excel_file.exists():
        print(f"Error: The file '{excel_file}' was not found.")
        sys.exit(1)

    # get the directory of the excel file
    excel_dir = excel_file.parent

    # Load the data
    data_list = load_series_info(excel_file)

    # Print the loaded data to verify
    print(f"Successfully loaded {len(data_list)} records.\n")
    for item in data_list:
        print(item)

    # Export unique te_ms arrays
    export_unique_te_arrays(data_list, excel_dir, te_units="s")
    # pdb.set_trace()
