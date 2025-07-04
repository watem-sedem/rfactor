import os
import textwrap
from pathlib import Path

import pandas as pd
import pytest

from rfactor.rain import load_rain_file, load_rain_file_matlab_legacy, load_rain_folder
from rfactor.rfactor import (
    maximum_intensity,
    maximum_intensity_matlab_clone,
    rain_energy_brown_and_foster1987,
    rain_energy_mcgregor1995,
    rain_energy_verstraeten2006,
)

CURRENT_DIR = Path(os.path.dirname(__file__))


@pytest.fixture()
def rain_benchmark_closure():
    """Rain data used for benchmark reference case"""

    def rain_benchmark_year(station, year):
        """Get benchmark data for given year and station"""
        rain = load_rain_file(
            CURRENT_DIR / "data" / "test_rainfalldata" / f"{station}_{year}.txt",
            load_rain_file_matlab_legacy,
        )
        return rain

    return rain_benchmark_year


@pytest.fixture()
def rain_benchmark_data():
    """Rain data used for benchmark reference case"""
    return load_rain_folder(CURRENT_DIR / "data" / "test_rainfalldata")


@pytest.fixture()
def erosivity_benchmark_closure():
    """Erosivity data used for benchmark reference case"""

    def erosivity_benchmark_energy_intensity(energy_method, intensity_method):
        """Erosivity output used for benchmark reference case

        Parameters
        ----------
        energy_method: callable
            Energy function from source package

            - :func:`rfactor.rfactor.rain_energy_verstraeten2006`
            - :func:`rfactor.rfactor.rain_energy_mcgregor1995`
            - :func:`rfactor.rfactor.rain_energy_brown_and_foster1987`

        intensity_method: callable
            Energy function from source package

            - :func:`rfactor.rfactor.maximum_intensity`
            - :func:`rfactor.rfactor.maximum_intensity_matlab_clone`
        """
        msg = f"Intensity function '{intensity_method}' not implemented"
        if energy_method is rain_energy_verstraeten2006:
            if intensity_method is maximum_intensity:
                file = "test_data_verstraeten_maximum_intensity.csv"
            elif intensity_method is maximum_intensity_matlab_clone:
                file = "test_data_verstraeten_maximum_intensity_matlab_clone.csv"
            else:
                NotImplementedError(msg)
        elif energy_method is rain_energy_mcgregor1995:
            if intensity_method is maximum_intensity:
                file = "test_data_mcgregor_maximum_intensity.csv"
            elif intensity_method is maximum_intensity_matlab_clone:
                file = "test_data_mcgregor_maximum_intensity_matlab_clone.csv"
            else:
                NotImplementedError(msg)
        elif energy_method is rain_energy_brown_and_foster1987:
            if intensity_method is maximum_intensity:
                file = "test_data_brown_and_foster_maximum_intensity.csv"
            elif intensity_method is maximum_intensity_matlab_clone:
                file = "test_data_brown_and_foster_maximum_intensity_matlab_clone.csv"
            else:
                NotImplementedError(msg)
        else:
            msg = f"Energy function '{energy_method}' not implemented"
            NotImplementedError(msg)

        erosivity = pd.read_csv(
            CURRENT_DIR / "data" / "test_erosivitydata" / file,
            index_col=0,
            parse_dates=[0, 1],
        )
        erosivity = erosivity.rename(columns={"datetime.1": "datetime"})
        return erosivity

    return erosivity_benchmark_energy_intensity


@pytest.fixture()
def erosivity_benchmark_matlab_clone_data():
    """Erosivity output used for benchmark reference case"""
    erosivity = pd.read_csv(
        CURRENT_DIR
        / "data"
        / "test_erosivitydata"
        / "test_data_verstraeten_maximum_intensity_matlab_clone.csv",
        index_col=0,
        parse_dates=[0, 1],
    )
    erosivity = erosivity.rename(columns={"datetime.1": "datetime"})
    return erosivity


@pytest.fixture()
def rain_data_file_matlab(tmp_path):
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
def rain_data_file_flanders(tmp_path):
    """Example rainfall data file"""
    example_rain_path = tmp_path / "station_name_2021.txt"
    example_rain_data = """\
        2021-01-01 00:00:00\t0.0
        2021-01-01 00:01:00\t1.0
        2021-01-01 00:10:00\t0.0
        2021-01-01 00:20:00\t0.0
        2021-01-01 00:30:00\t10.5
        2021-01-01 00:40:00\t5.2
        2021-01-01 00:50:00\t1
        2021-01-01 01:00:00\t0.02
        2021-01-01 01:10:00\t
        2021-12-31 23:59:00\t10.
        """
    with open(example_rain_path, "w") as rain:
        rain.write(textwrap.dedent(example_rain_data))
    return example_rain_path


@pytest.fixture()
def rain_data_folder_matlab(tmp_path):
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
def data_folder_non_existing(tmp_path):
    """Example rainfall data file"""
    example_rain_path_non_existing = tmp_path / "non-existing"

    return example_rain_path_non_existing


@pytest.fixture()
def data_folder_empty(tmp_path):
    """Example rainfall data file"""
    example_rain_path_empty = tmp_path / "empty"
    example_rain_path_empty.mkdir()

    return example_rain_path_empty


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
