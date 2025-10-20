from pathlib import Path
import typer
from rich.console import Console
import logging


from mrimagetools.pipelines.thermometry.multiecho_thermometry import (
    multiecho_thermometry,
)

from ethylene_glycol_phantom_thermometry.util import (
    get_project_root,
    load_bids_sidecars_from_directory,
    load_series_info,
)

PROJECT_ROOT = get_project_root()
DATA_DIR = PROJECT_ROOT / "data"

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = typer.Typer(pretty_exceptions_enable=False)


def analysis(data_dir: Path, method: str = "regionwise") -> None:
    image_info_file = data_dir / "image_information.xlsx"
    series_data_list = load_series_info(image_info_file)
    bids_sidecars = load_bids_sidecars_from_directory(data_dir)

    # pre-made segmentation image for these data
    segmentation_file = data_dir / "segmentation.nii.gz"
    if not segmentation_file.exists():
        raise FileNotFoundError(f"Segmentation file not found: {segmentation_file}")

    # map sidecars to series data
    # find the matching sidecar (study_id and series_no), then use the sidecar
    # filename to construct the nifti filename, assumed to be same name but .nii.gz
    for series_data in series_data_list:
        matching_sidecars = [
            sc
            for sc in bids_sidecars
            if sc.study_id == series_data.study_id
            and sc.series_no == series_data.series_no
        ]
        if matching_sidecars:
            sidecar = matching_sidecars[0]
            nifti_filename = sidecar.filename.with_suffix(".nii.gz")
            series_data.nifti_file = nifti_filename
        else:
            print(
                f"Warning: No matching sidecar found for study {series_data.study_id}, series {series_data.series_no}"
            )

    unique_runs = set(sd.run for sd in series_data_list)

    for run in unique_runs:
        # collect the series data for this run
        run_series = [sd for sd in series_data_list if sd.run == run]
        # save echo times in seconds to text files
        te_files = []
        multiecho_files = []
        for sd in run_series:
            te_s = [te / 1000.0 for te in sd.te_ms]
            te_file = data_dir / f"run-{run:02d}_series-{sd.series_no:03d}_te_s.txt"
            te_files.append(te_file)
            with open(te_file, "w") as f:
                for te in te_s:
                    f.write(f"{te}\n")
            multiecho_files.append(sd.nifti_file)

        output_prefix = f"run-{run:02d}_thermometry"
        multiecho_thermometry(
            multiecho_nifti_files=multiecho_files,
            echo_times_files=te_files,
            segmentation_nifti_file=segmentation_file,
            output_prefix=output_prefix,
            method=method,
            n_bootstrap=100,
        )


def main(data_dir: Path, method: str) -> None:
    """
    Main analysis function.

    Args:
        data_dir: The path to the data directory.
        method: The analysis method to use.
    """
    print(f"Starting analysis in: {data_dir}")
    print(f"Using method: {method}")
    analysis(data_dir, method)
