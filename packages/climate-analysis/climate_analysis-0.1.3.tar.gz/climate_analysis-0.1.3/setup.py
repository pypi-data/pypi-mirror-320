from setuptools import find_packages, setup

setup(
    name="climate_analysis",
    version="0.1.2",
    description="Climate analysis tools for generating maps and time-series",
    author="Bijan Fallah",
    author_email="bijan.fallah@gmail.com",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "xarray",
        "dask",
        "intake",
        "matplotlib",
        "cartopy",
        "xesmf",
        "requests_cache",
        "seaborn",
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "generate-maps=climate_analysis.maps:main",
            "generate-time-series=climate_analysis.time_series:main",
        ],
    },
)
