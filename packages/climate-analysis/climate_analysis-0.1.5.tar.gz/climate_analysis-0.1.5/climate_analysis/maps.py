import argparse
import os
from concurrent.futures import ThreadPoolExecutor

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cftime
import fsspec
import intake
import matplotlib.pyplot as plt
import numpy as np
import requests_cache
import xarray as xr
import xesmf as xe
from cartopy.io.shapereader import Reader, natural_earth
from matplotlib.colors import BoundaryNorm
from shapely.geometry import box

# Enable requests caching
CACHE_PATH = "./cmip6_cache"
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)

requests_cache.install_cache(
    os.path.join(CACHE_PATH, "http_cache"), expire_after=86400
)  # Cache for 1 day


def load_catalog(url):
    """Load the CMIP6 data catalog with caching."""
    return intake.open_esm_datastore(url)


def add_country_labels(ax, lat_range, lon_range):
    """Adds country labels for countries within the specified latitude and longitude range."""
    map_bbox = box(lon_range[0], lat_range[0], lon_range[1], lat_range[1])
    shapefile_path = natural_earth(
        category="cultural", name="admin_0_countries", resolution="110m"
    )

    for country in Reader(shapefile_path).records():
        country_name = country.attributes["NAME"]
        country_geometry = country.geometry
        if map_bbox.contains(country_geometry):
            centroid = country_geometry.centroid
            ax.text(
                centroid.x,
                centroid.y,
                country_name,
                transform=ccrs.PlateCarree(),
                fontsize=14,
                color="black",
                ha="center",
                zorder=5,
            )


def preprocess_dataset(ds):
    """Preprocess a dataset, ensuring proper time handling and removing unwanted variables."""
    try:
        if "time" in ds.coords:
            if not isinstance(ds["time"].values[0], cftime.datetime):
                ds["time"] = xr.decode_cf(ds).time
            ds = ds.sortby("time")
            ds = ds.isel(time=~ds.get_index("time").duplicated())
        unwanted_vars = [var for var in ds.coords if var not in ["time", "lat", "lon"]]
        ds = ds.drop_vars(unwanted_vars, errors="ignore")
        return ds
    except Exception as e:
        print(f"Error preprocessing dataset: {e}")
        return None


def preprocess_dataset_parallel(args):
    """Wrapper for parallel dataset preprocessing."""
    group, df = args
    try:
        ds = xr.open_zarr(fsspec.get_mapper(df.zstore.values[0]), consolidated=True)
        print(
            f"Dataset {group} opened successfully with variables: {list(ds.data_vars)}"
        )
        return group, preprocess_dataset(ds)
    except Exception as e:
        print(f"Error processing dataset {group}: {e}")
        return group, None


def preprocess_data_parallel(col, query):
    """Preprocess datasets in parallel and group by source_id."""
    col_subset = col.search(require_all_on=["source_id"], **query)
    datasets = {}

    with ThreadPoolExecutor() as executor:
        results = executor.map(
            preprocess_dataset_parallel,
            col_subset.df.groupby(by=["source_id", "experiment_id"]),
        )

    for (source_id, experiment_id), ds in results:
        if source_id not in datasets:
            datasets[source_id] = {}
        if ds is not None:
            datasets[source_id][experiment_id] = ds

    return datasets


def create_target_grid(lat_range, lon_range, resolution):
    """Create a target grid for regridding."""
    lat = np.arange(lat_range[0], lat_range[1] + resolution, resolution)
    lon = np.arange(lon_range[0], lon_range[1] + resolution, resolution)
    return xr.Dataset({"lat": ("lat", lat), "lon": ("lon", lon)})


def regrid_dataset(ds, target_grid):
    """Regrid a dataset to a specified target grid."""
    try:
        regridder = xe.Regridder(ds, target_grid, "bilinear")
        return regridder(ds)
    except Exception as e:
        print(f"Error during regridding: {e}")
        return None


def calculate_difference(historical_ds, future_ds, historical_period, future_period):
    """Calculate the difference between historical and future datasets."""
    try:
        historical_clim = historical_ds.sel(time=slice(*historical_period)).mean(
            dim="time"
        )
        future_clim = future_ds.sel(time=slice(*future_period)).mean(dim="time")
        return future_clim - historical_clim
    except Exception as e:
        print(f"Error during difference calculation: {e}")
        return None


def plot_ensemble_mean(
    ensemble_mean, lat_range, lon_range, color_limits, output_path, colormaps
):
    """Plot the ensemble mean of differences."""
    try:
        variable_name = list(ensemble_mean.data_vars.keys())[0]
        data_array = ensemble_mean[variable_name]
        levels = np.arange(color_limits[0], color_limits[1] + 0.5, 0.5)
        cmap = plt.get_cmap(colormaps)
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

        fig, ax = plt.subplots(
            figsize=(10, 6), subplot_kw={"projection": ccrs.PlateCarree()}
        )
        img = data_array.plot(
            ax=ax,
            cmap=cmap,
            norm=norm,
            add_colorbar=False,
            levels=levels,
            extend="both",
        )

        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle="-")
        ax.set_extent(
            [lon_range[0], lon_range[1], lat_range[0], lat_range[1]],
            crs=ccrs.PlateCarree(),
        )
        add_country_labels(ax, lat_range, lon_range)

        cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
        cbar = fig.colorbar(img, cax=cbar_ax, orientation="vertical", extend="both")
        #cbar.set_label("Temperature Difference (K)")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        
    except Exception as e:
        print(f"Error during ensemble mean plotting: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate climate maps.")
    parser.add_argument(
        "--catalog_url", type=str, required=True, help="URL of the data catalog"
    )
    parser.add_argument(
        "--experiments", type=str, nargs="+", required=True, help="List of experiments"
    )
    parser.add_argument(
        "--lat_range",
        type=float,
        nargs=2,
        required=True,
        help="Latitude range (min max)",
    )
    parser.add_argument(
        "--lon_range",
        type=float,
        nargs=2,
        required=True,
        help="Longitude range (min max)",
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to save the output map"
    )
    args = parser.parse_args()

    col = load_catalog(args.catalog_url)
    query = {
        "experiment_id": ["historical"] + args.experiments,
        "table_id": "Amon",
        "variable_id": ["tas"],
        "member_id": "r1i1p1f1",
    }

    datasets = preprocess_data_parallel(col, query)
    target_grid = create_target_grid(args.lat_range, args.lon_range, resolution=0.50)
    regridded_differences = []

    for model, experiments in datasets.items():
        if "historical" not in experiments or args.experiments[0] not in experiments:
            print(f"Skipping {model}: Missing required experiments.")
            continue

        historical_ds = preprocess_dataset(experiments["historical"])
        future_ds = preprocess_dataset(experiments[args.experiments[0]])

        if historical_ds is None or future_ds is None:
            print(f"Skipping {model}: Invalid datasets for required experiments.")
            continue

        historical_ds_regridded = regrid_dataset(historical_ds, target_grid)
        future_ds_regridded = regrid_dataset(future_ds, target_grid)

        difference = calculate_difference(
            historical_ds_regridded,
            future_ds_regridded,
            ("1981", "2010"),
            ("2071", "2100"),
        )

        if difference is not None:
            regridded_differences.append(difference)

    if regridded_differences:
        ensemble_mean = xr.concat(regridded_differences, dim="model").mean(dim="model")
        plot_ensemble_mean(
            ensemble_mean,
            args.lat_range,
            args.lon_range,
            (-0.5, 6.5),
            args.output,
            "Reds",
        )
        print(f"Map saved as {args.output}.")
    else:
        print("No valid differences for ensemble mean calculation.")

def generate_maps():
    """Wrapper function for the CLI entry point to generate climate maps."""
    main()

if __name__ == "__main__":
    main()
