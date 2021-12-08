import os
import textwrap
from pathlib import Path

import pandas as pd
import pytest

from rfactor.process import load_rain_file, load_rain_folder

CURRENT_DIR = Path(os.path.dirname(__file__))


@pytest.fixture()
def rain_benchmark_closure():
    """Rain data used for benchmark reference case"""

    def rain_benchmark_year(station, year):
        """Get benchmark data for given year and station"""
        rain = load_rain_file(
            CURRENT_DIR / "data" / "test_rainfalldata" / f"{station}_{year}.txt"
        )
        return rain

    return rain_benchmark_year


@pytest.fixture()
def rain_benchmark_data():
    """Rain data used for benchmark reference case"""
    return load_rain_folder(CURRENT_DIR / "data" / "test_rainfalldata")


@pytest.fixture()
def erosivity_benchmark_data():
    """Erosivity output used for benchmark reference case"""
    erosivity = pd.read_csv(
        CURRENT_DIR / "data" / "test_erosivitydata" / "test_data_maximum_intensity.csv",
        index_col=0,
        parse_dates=[0, 1],
    )
    erosivity = erosivity.rename(columns={"datetime.1": "datetime"})
    return erosivity


@pytest.fixture()
def erosivity_benchmark_matlab_clone_data():
    """Erosivity output used for benchmark reference case"""
    erosivity = pd.read_csv(
        CURRENT_DIR
        / "data"
        / "test_erosivitydata"
        / "test_data_maximum_intensity_matlab_clone.csv",
        index_col=0,
        parse_dates=[0, 1],
    )
    erosivity = erosivity.rename(columns={"datetime.1": "datetime"})
    return erosivity


@pytest.fixture()
def rain_data_file(tmp_path):
    """Example rainfall data file"""
    example_rain_path = tmp_path / "station_name_2021.txt"
    example_rain_data = """\
        1 1.00
        2 0.20
        525599 10.00
        """
    with open(example_rain_path, "w") as rain:
        rain.write(textwrap.dedent(example_rain_data))
    return example_rain_path


@pytest.fixture()
def rain_data_folder(tmp_path):
    """Example rainfall data file"""
    example_rain_path = tmp_path / "rain"
    example_rain_path.mkdir()

    # create example data files for multiple years
    for idx, year in enumerate([2020, 2021]):
        rain_file = example_rain_path / f"station_{idx}_{year}.txt"
        example_rain_data = """\
            1 1.00
            2 0.20
            525599 10.00
            """
        with open(rain_file, "w") as rain:
            rain.write(textwrap.dedent(example_rain_data))

    return example_rain_path


@pytest.fixture()
def dummy_rain():
    """Dummy rainfall data according to required input data."""
    rain = [
        0.27,
        0.02,
        0.48,
        0.22,
        0.09,
        0.08,
        0.19,
        0.21,
        0.2,
        0.15,
        0.17,
        0.25,
        0.45,
        0.57,
    ]
    dates = [
        "2018-01-01 02:10:00",
        "2018-01-01 02:20:00",
        "2018-01-01 03:10:00",
        "2018-01-01 07:40:00",
        "2018-01-01 07:50:00",
        "2018-01-01 14:30:00",
        "2018-01-01 14:40:00",
        "2018-01-01 14:50:00",
        "2018-01-01 15:00:00",
        "2018-01-01 15:10:00",
        "2018-01-01 15:20:00",
        "2018-01-01 15:30:00",
        "2018-01-01 15:40:00",
        "2018-01-01 15:50:00",
    ]
    station = "P01_001"
    return pd.DataFrame(
        {"rain_mm": rain, "datetime": pd.to_datetime(dates), "station": station}
    )


@pytest.fixture()
def dummy_erosivity():
    """Erosivity output for different stations and years.

    Data is formatted as each second element is an rfactor for a given year/station.
    """
    dates = [
        "2018-01-01 14:30:00",
        "2018-01-02 16:30:00",
        "2005-01-04 21:00:00",
        "2005-01-10 19:00:00",
        "2005-01-01 19:00:00",
        "2005-01-10 19:10:00",
        "2005-01-10 17:40:00",
        "2005-01-17 17:00:00",
        "2009-01-05 02:50:00",
        "2009-01-12 18:10:00",
    ]
    all_event_rain_cum = [1.08, 12.37, 1.26, 4.09, 0.00, 5.52, 2.89, 9.35, 0.78, 3.70]
    erosivity_cum = [
        5.018784,
        8.008465,
        0.271870,
        3.467279,
        0.299340,
        2.419160,
        1.358869,
        4.406269,
        0.213214,
        0.595594,
    ]
    stations = [
        "P01_001",
        "P01_001",
        "P01_003",
        "P01_003",
        "P01_010",
        "P01_010",
        "P01_015",
        "P01_015",
        "P01_029",
        "P01_029",
    ]
    erosivity = pd.DataFrame(
        {
            "datetime": pd.to_datetime(dates),
            "all_event_rain_cum": all_event_rain_cum,
            "erosivity_cum": erosivity_cum,
            "station": stations,
        }
    )
    erosivity["year"] = erosivity["datetime"].dt.year
    return erosivity


@pytest.fixture()
def station_metadata():
    """Example station metadata file"""
    return pd.DataFrame(
        {"station": ["station_0", "station_1"], "x": [4.0, 4.1], "y": [51.2, 51.1]}
    )
