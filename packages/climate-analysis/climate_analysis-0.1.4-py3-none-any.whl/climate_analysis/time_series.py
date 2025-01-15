import argparse

import dask
import fsspec
import intake
import numpy as np
import seaborn as sns
import xarray as xr
from dask.diagnostics import progress
from matplotlib import pyplot as plt
from tqdm.autonotebook import tqdm

# Load the catalog
CATALOG_URL = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
col = intake.open_esm_datastore(CATALOG_URL)

# Configuration
expts = [
    "historical",
    "ssp126",
    "ssp245",
    "ssp370",
    "ssp585",
]  # Experiments to consider
query = dict(
    experiment_id=expts,
    table_id="Amon",
    variable_id=["tas"],
    member_id="r1i1p1f1",
)

lat_range = (35, 57)  # Latitude bounds for Central Asia
lon_range = (45, 87)  # Longitude bounds for Central Asia
time_slices = {
    "2011-2040": (2011, 2040),
    "2041-2070": (2041, 2070),
    "2071-2100": (2071, 2100),
}

# Generate a dynamic output path
EXPERIMENT_LABEL = "_".join(expts)
TIME_SLICE_LABEL = "-".join([f"{k}" for k in time_slices.keys()])
OUTPUT_PATH = f"Time-series_{EXPERIMENT_LABEL}_{TIME_SLICE_LABEL}.png"

# Query data
col_subset = col.search(require_all_on=["source_id"], **query)
col_subset.df.groupby("source_id")[
    ["experiment_id", "variable_id", "table_id"]
].nunique()


def drop_all_bounds(ds):
    drop_vars = [
        vname for vname in ds.coords if (("_bounds") in vname) or ("_bnds") in vname
    ]
    return ds.drop(drop_vars)


def open_dset(df):
    assert len(df) == 1
    ds = xr.open_zarr(fsspec.get_mapper(df.zstore.values[0]), consolidated=True)
    return drop_all_bounds(ds)


def open_delayed(df):
    return dask.delayed(open_dset)(df)


from collections import defaultdict

dsets = defaultdict(dict)

for group, df in col_subset.df.groupby(by=["source_id", "experiment_id"]):
    dsets[group[0]][group[1]] = open_delayed(df)

dsets_ = dask.compute(dict(dsets))[0]


# Define the regional_mean function
def get_lat_name(ds):
    for lat_name in ["lat", "latitude"]:
        if lat_name in ds.coords:
            return lat_name
    raise RuntimeError("Couldn't find a latitude coordinate")


def get_lon_name(ds):
    for lon_name in ["lon", "longitude"]:
        if lon_name in ds.coords:
            return lon_name
    raise RuntimeError("Couldn't find a longitude coordinate")


def regional_mean(ds, lat_range, lon_range):
    lat = ds[get_lat_name(ds)]
    lon = ds[get_lon_name(ds)]

    region_ds = ds.sel(
        **{
            get_lat_name(ds): slice(lat_range[0], lat_range[1]),
            get_lon_name(ds): slice(lon_range[0], lon_range[1]),
        }
    )

    weight = np.cos(np.deg2rad(region_ds[get_lat_name(ds)]))
    weight /= weight.mean()
    other_dims = set(region_ds.dims) - {"time"}
    return (region_ds * weight).mean(other_dims)


def calculate_time_slice_means(ds, slices):
    means = {}
    for label, (start, end) in slices.items():
        means[label] = ds.sel(year=slice(start, end)).mean("year")
    return means


# Default configurations
CATALOG_URL = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
EXPERIMENTS = [
    "historical",
    "ssp126",
    "ssp245",
    "ssp370",
    "ssp585",
]  # Experiments to consider
LAT_RANGE = (35, 57)  # Latitude bounds for Central Asia
LON_RANGE = (45, 87)  # Longitude bounds for Central Asia
TIME_SLICES = {
    "2011-2040": (2011, 2040),
    "2041-2070": (2041, 2070),
    "2071-2100": (2071, 2100),
}
VARIABLE = ["tas"]


def generate_time_series_plot(
    catalog_url,
    experiments,
    lat_range,
    lon_range,
    variable,
    climatology_start,
    climatology_end,
    output_path,
):
    # Load the CMIP6 data catalog
    col = intake.open_esm_datastore(catalog_url)

    # Query configuration
    query = dict(
        experiment_id=experiments,
        table_id="Amon",
        variable_id=[variable],
        member_id="r1i1p1f1",
    )

    # Fetch and preprocess datasets
    col_subset = col.search(require_all_on=["source_id"], **query)

    dsets = defaultdict(dict)
    for group, df in col_subset.df.groupby(by=["source_id", "experiment_id"]):
        dsets[group[0]][group[1]] = dask.delayed(open_dset)(df)

    dsets_ = dask.compute(dict(dsets))[0]

    # Define time slices
    time_slices = {
        "2011-2040": (2011, 2040),
        "2041-2070": (2041, 2070),
        "2071-2100": (2071, 2100),
    }

    # Processing datasets
    expt_da = xr.DataArray(
        experiments,
        dims="experiment_id",
        name="experiment_id",
        coords={"experiment_id": experiments},
    )

    dsets_aligned = {}
    time_slice_means = {}

    for k, v in tqdm(dsets_.items()):
        expt_dsets = v.values()
        if any([d is None for d in expt_dsets]):
            print(f"Missing experiment for {k}")
            continue

        for ds in expt_dsets:
            ds.coords["year"] = ds.time.dt.year

        dsets_ann_mean = [
            v[expt]
            .pipe(regional_mean, lat_range, lon_range)
            .swap_dims({"time": "year"})
            .drop("time")
            .coarsen(year=12)
            .mean()
            for expt in experiments
        ]

        dsets_aligned[k] = xr.concat(dsets_ann_mean, join="outer", dim=expt_da)
        time_slice_means[k] = calculate_time_slice_means(dsets_aligned[k], time_slices)

    with progress.ProgressBar():
        dsets_aligned_ = dask.compute(dsets_aligned)[0]

    # Combine and prepare data for plotting
    source_ids = list(dsets_aligned_.keys())
    source_da = xr.DataArray(
        source_ids, dims="source_id", name="source_id", coords={"source_id": source_ids}
    )

    big_ds = xr.concat(
        [ds.reset_coords(drop=True) for ds in dsets_aligned_.values()], dim=source_da
    )
    df_all = big_ds.sel(year=slice(1900, 2100)).to_dataframe().reset_index()
    # Exclude the last year of the historical period
    historical_end_year = (
        climatology_end  # This corresponds to the end year of the climatology
    )
    df_all = df_all[
        ~(
            (df_all["experiment_id"] == "historical")
            & (df_all["year"] == historical_end_year)
        )
    ]
    # Compute climatology
    climatology = (
        df_all[
            (df_all["year"] >= climatology_start) & (df_all["year"] < climatology_end)
        ]
        .groupby("experiment_id")[variable]
        .mean()
    )

    # Compute anomalies
    df_all[f"{variable}_anomaly"] = df_all.apply(
        lambda row: row[variable] - climatology["historical"], axis=1
    )

    # Plotting the time series
    g = sns.relplot(
        data=df_all,
        x="year",
        y=f"{variable}_anomaly",
        hue="experiment_id",
        kind="line",
        errorbar="sd",
        aspect=2,
        legend=True,
    )
    plt.savefig(output_path, dpi=300)
    print(f"Time series plot saved as {output_path}")
    # Save the list of models to a text file
    models_file = output_path.replace(".png", "_models.txt")
    with open(models_file, "w") as file:
        file.write("Models used in the time series plot:\n")
        file.writelines(f"- {model}\n" for model in source_ids)
    print(f"List of models saved as {models_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate time series plots.")
    parser.add_argument(
        "--catalog_url", type=str, default=CATALOG_URL, help="URL of the CMIP6 catalog"
    )
    parser.add_argument(
        "--experiments",
        type=str,
        nargs="+",
        default=EXPERIMENTS,
        help="Experiments to include",
    )
    parser.add_argument(
        "--lat_range", type=float, nargs=2, default=LAT_RANGE, help="Latitude range"
    )
    parser.add_argument(
        "--lon_range", type=float, nargs=2, default=LON_RANGE, help="Longitude range"
    )
    parser.add_argument(
        "--variable", type=str, default=VARIABLE, help="Variable to process"
    )
    parser.add_argument(
        "--climatology_start",
        type=int,
        required=True,
        help="Start year for climatology",
    )

    parser.add_argument(
        "--climatology_end", type=int, required=True, help="End year for climatology"
    )
    parser.add_argument("--output", type=str, required=True, help="Output file path")

    args = parser.parse_args()
    generate_time_series_plot(
        args.catalog_url,
        args.experiments,
        args.lat_range,
        args.lon_range,
        args.variable,
        args.climatology_start,
        args.climatology_end,
        args.output,
    )


def generate_time_series():
    """Wrapper function for the CLI entry point to generate time series plots."""
    main()

if __name__ == "__main__":
    main()
