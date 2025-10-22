from pathlib import Path
import typer
from rich.console import Console
import logging
import pandas as pd
from datetime import datetime, timedelta
from enum import Enum
from matplotlib import pyplot as plt
import pdb

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


class Method(str, Enum):
    """The analysis method to use."""

    REGIONWISE = "regionwise"
    VOXELWISE = "voxelwise"
    REGIONWISE_BOOTSTRAP = "regionwise_bootstrap"


def analysis(
    data_dir: Path, method: Method = Method.REGIONWISE, n_bootstrap: int = 10
) -> None:
    console.print(f"[bold blue]Starting analysis in: {data_dir}[/bold blue]")
    image_info_file = data_dir / "image_information.xlsx"
    series_data_list = load_series_info(image_info_file)
    bids_sidecars = load_bids_sidecars_from_directory(data_dir)

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
    analysis_results = []
    for run in unique_runs:
        console.print(
            f"[bold blue]Processing run {run} of {len(unique_runs)}[/bold blue]"
        )
        # collect the series data for this run
        run_series = [sd for sd in series_data_list if sd.run == run]
        # save echo times in seconds to text files
        te_files = []
        multiecho_files: list[Path] = []
        for sd in run_series:
            te_s = [te / 1000.0 for te in sd.te_ms]
            te_file = data_dir / f"run-{run:02d}_series-{sd.series_no:03d}_te_s.txt"
            te_files.append(te_file)
            with open(te_file, "w") as f:
                for te in te_s:
                    f.write(f"{te}\n")
            multiecho_files.append(sd.nifti_file)  # type: ignore

        output_prefix = f"run-{run:02d}_thermometry"
        _, report_data = multiecho_thermometry(
            multiecho_nifti_files=multiecho_files,
            echo_times_files=te_files,
            segmentation_nifti_file=(data_dir / run_series[0].segmentation).with_suffix(
                ".nii.gz"
            ),
            output_prefix=output_prefix,
            method=method,
            n_bootstrap=n_bootstrap,
        )

        # convert acquisition_date_time to datetime
        # pdb.set_trace()
        acq_dt_list = [
            datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f")
            for dt in report_data.acquisition_date_time
        ]
        duration_list = [sd.duration for sd in run_series if sd.duration]
        sort_indices = sorted(range(len(acq_dt_list)), key=lambda k: acq_dt_list[k])
        acq_dt_list_sorted = [acq_dt_list[i] for i in sort_indices]
        duration_list_sorted = [duration_list[i] for i in sort_indices]

        # acquisition took place from first datetime to last + acquisition duration. We want to use the midpoint time
        midpoint_time = (
            acq_dt_list_sorted[0]
            + (
                acq_dt_list_sorted[-1]
                + timedelta(seconds=duration_list_sorted[-1])
                - acq_dt_list_sorted[0]
            )
            / 2
        )

        for region in report_data.report:
            analysis_results.append(
                {
                    "run": run,
                    "time": midpoint_time,
                    "region_id": region.region_id,
                    "temperature": region.region_mean_temperature,
                    "uncertainty": region.region_temperature_uncertainty[0],
                    "interval": region.region_temperature_uncertainty[1],
                }
            )
    console.print(
        f"[bold blue]Thermometry processing using method {method} complete[/bold blue]"
    )
    results_df = pd.DataFrame(analysis_results)
    results_file = data_dir / f"thermometry_analysis_{method}.xlsx"
    results_df.to_excel(results_file, index=False)
    console.print(
        f"[bold green]Analysis complete! Results saved to {results_file}[/bold green]"
    )
    # make a plot of temperature vs time for each region
    plt.figure(figsize=(10, 6))
    for region_id in results_df["region_id"].unique():
        region_df = results_df[results_df["region_id"] == region_id]
        plt.errorbar(
            x=region_df["time"],
            y=region_df["temperature"],
            yerr=region_df["uncertainty"],
            label=f"Region {region_id}",
            marker="o",
            linestyle="-",
        )

    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature by Region")
    plt.legend()
    plt.grid(True)
    # plt.show()
    console.print(f"[bold blue]Saving plot to files[/bold blue]")
    # save the plot as png and svg
    plot_file_png = data_dir / f"thermometry_analysis_{method}.png"
    plot_file_svg = data_dir / f"thermometry_analysis_{method}.svg"
    plt.savefig(plot_file_png)
    plt.savefig(plot_file_svg)


def main(data_dir: Path, method: Method) -> None:
    """
    Main analysis function.

    Args:
        data_dir: The path to the data directory.
        method: The analysis method to use.
    """
    print(f"Starting analysis in: {data_dir}")
    print(f"Using method: {method.value}")
    analysis(data_dir, method)
