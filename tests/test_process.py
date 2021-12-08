import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from rfactor.process import (
    _check_path,
    _days_since_start_year,
    _extract_metadata_from_file_path,
    compute_rainfall_statistics,
    get_rfactor_station_year,
    load_rain_file,
    load_rain_folder,
    write_erosivity_data,
)


def test_days_since_last_year_float():
    """Moment of the day is translated as decimal number."""
    ts_series = pd.Series(
        pd.date_range("2021-01-01 00:00", "2021-01-02 00:00", freq="6H")
    )
    np.testing.assert_allclose(
        _days_since_start_year(ts_series).values, np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    )


def test_days_since_last_year_single_year():
    """Data should all be from the same year."""
    ts_series = pd.Series(
        pd.date_range("2020-12-31 00:00", "2021-01-02 00:00", freq="6H")
    )
    with pytest.raises(Exception):
        _days_since_start_year(ts_series)


@pytest.mark.parametrize(
    "file_name,station,year",
    [
        ("UKKEL_2002.txt", "UKKEL", "2002"),
        ("U_K_K_E_L_1998.txt", "U_K_K_E_L", "1998"),
        ("U_K_K_E_L_1998.txt", "U_K_K_E_L", "1998"),
        ("UK-KEL_1998.txt", "UK-KEL", "1998"),
    ],
)
def test_extract_metadata_from_file_path(file_name, station, year):
    """Split valid file names into station and nam.e"""
    assert _extract_metadata_from_file_path(Path(file_name)) == (station, year)


@pytest.mark.parametrize(
    "file_name",
    [
        "UKKEL_2002---.txt",  # text after year
        "UKKEL_2002_.txt",  # text after year
        "UKKEL_202.txt",  # invalid year
        "UKKEL20022.txt",  # invalid year
        "2002.txt" "UKKEL.txt",  # no station name  # no year
    ],
)
def test_extract_metadata_from_file_path_invalid(file_name):
    """Invalid file paths should raise ValueError"""
    with pytest.raises(ValueError) as excinfo:
        assert _extract_metadata_from_file_path(Path(file_name))
    assert "Input file_path_format should" in str(excinfo.value)


def test_check_path():
    """File path checks should provide user with info on pathlib.Path"""
    assert _check_path(Path("./")) is None
    with pytest.raises(TypeError) as excinfo:
        _check_path("invalid_string_input_path")
    assert "to convert string file_path to valid" in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        _check_path(np.array([1, 2]))
    assert " should be a pathlib.Path" in str(excinfo.value)


def test_load_rain_file(rain_data_file):
    """Valid rainfall data should be parsed to rain DataFrame"""
    rainfall_data = load_rain_file(rain_data_file)
    assert isinstance(rainfall_data, pd.DataFrame)
    assert list(rainfall_data.columns) == [
        "minutes_since",
        "rain_mm",
        "datetime",
        "station",
        "year",
        "tag",
    ]
    assert list(rainfall_data["station"].unique()) == ["station_name"]
    assert list(rainfall_data.iloc[0].values) == [
        1,
        1.0,
        pd.to_datetime("2021-01-01 00:01:00"),
        "station_name",
        2021,
        "station_name_2021",
    ]
    assert list(rainfall_data.iloc[-1].values) == [
        525599,
        10.00,
        pd.to_datetime("2021-12-31 23:59:00"),
        "station_name",
        2021,
        "station_name_2021",
    ]


def test_load_rain_file_with_folder(rain_data_folder):
    """When input is a file, should return ValueError to user"""
    with pytest.raises(ValueError) as excinfo:
        load_rain_file(rain_data_folder)
    assert "a file instead of a directory" in str(excinfo.value)


def test_load_rain_folder(rain_data_folder):
    """Rainfall data should be parsed to rain DataFrame
    when loading multiple files adding a year and tag column"""
    rainfall_data = load_rain_folder(rain_data_folder)
    assert isinstance(rainfall_data, pd.DataFrame)
    assert list(rainfall_data.columns) == [
        "minutes_since",
        "rain_mm",
        "datetime",
        "station",
        "year",
        "tag",
    ]
    assert list(rainfall_data["station"].unique()) == ["station_0", "station_1"]
    assert list(rainfall_data.iloc[0].values) == [
        1,
        1.0,
        pd.to_datetime("2020-01-01 00:01:00"),
        "station_0",
        2020,
        "station_0_2020",
    ]
    assert list(rainfall_data.iloc[-1].values) == [
        525599,
        10.00,
        pd.to_datetime("2021-12-31 23:59:00"),
        "station_1",
        2021,
        "station_1_2021",
    ]


def test_load_rain_folder_with_file(rain_data_file):
    """When input is a file, should return ValueError to user"""
    with pytest.raises(ValueError) as excinfo:
        load_rain_folder(rain_data_file)
    assert "a directory instead of a file" in str(excinfo.value)


def test_write_erosivity(dummy_erosivity, tmpdir):
    """Check written legacy matlab format files output"""
    erosivity = dummy_erosivity

    # Write the erosivity to disk
    output_dir = Path(tmpdir) / "erosivity"
    output_dir.mkdir()
    write_erosivity_data(erosivity, output_dir)

    p = re.compile("(.*)_([0-9]{4})$")  # extract year/station from file path
    written_files = list(sorted(output_dir.glob("*.csv")))

    # check the written output files are split per year/station
    matched_stations = set([p.match(path.stem).group(1) for path in written_files])
    matched_years = set([int(p.match(path.stem).group(2)) for path in written_files])
    assert set(dummy_erosivity["station"].unique()) == matched_stations
    assert set(dummy_erosivity["datetime"].dt.year.unique()) == matched_years

    # verify content of first file
    columns_to_compare = ["days_since", "erosivity_cum", "all_event_rain_cum"]
    first_station, first_year = p.match(written_files[0].stem).group(1, 2)
    original_data = erosivity[
        (erosivity["station"] == first_station)
        & (erosivity["datetime"].dt.year == int(first_year))
    ].copy()
    original_data["days_since"] = _days_since_start_year(original_data["datetime"])
    written_data = pd.read_csv(
        written_files[0], delimiter=" ", names=columns_to_compare
    )
    # compare written filewith orginal to one digit (rawest of the three columns)
    pd.testing.assert_frame_equal(
        original_data[columns_to_compare], written_data, atol=0.1
    )


def test_rfactor_from_erosivity(dummy_erosivity):
    """Latest erosivity of a station at the end of the year returns station/year
    sorted output of rfactor values"""
    # dummy data is formatted as each second element is an erosivity
    reference = dummy_erosivity[["year", "station", "erosivity_cum"]].iloc[1::2, :]
    reference = reference.sort_values(["station", "year"])
    reference.index = range(len(reference))

    pd.testing.assert_frame_equal(get_rfactor_station_year(dummy_erosivity), reference)


def test_rfactor_from_erosivity_subset(dummy_erosivity):
    """Only a given subset of stations/years as output"""

    stations_of_interest = ["P01_001", "P01_003"]
    station_subset = get_rfactor_station_year(
        dummy_erosivity, stations=stations_of_interest
    )
    assert set(station_subset["station"].unique()) == set(stations_of_interest)

    years_of_interest = [2005, 2009]
    station_subset = get_rfactor_station_year(dummy_erosivity, years=years_of_interest)
    assert set(station_subset["year"].unique()) == set(years_of_interest)


def test_rfactor_from_erosivity_subset_not_existing(dummy_erosivity):
    """Years/station subset is not part of the data set should raise Keyerror"""

    stations_of_interest = ["UNEXISTING STATION", "P01_003"]
    with pytest.raises(KeyError) as excinfo:
        get_rfactor_station_year(dummy_erosivity, stations=stations_of_interest)
    assert "UNEXISTING STATION" in str(excinfo.value)

    years_of_interest = [2008, 1991]
    with pytest.raises(KeyError) as excinfo:
        get_rfactor_station_year(dummy_erosivity, years=years_of_interest)
    assert "1991" in str(excinfo.value)


def test_rainfall_statistics(rain_data_folder):
    """"""
    rainfall_data = load_rain_folder(rain_data_folder)
    rf_stats = compute_rainfall_statistics(rainfall_data)
    assert set(rf_stats.columns) == set(["year", "records", "min", "median", "max"])
    assert isinstance(rf_stats["year"][0], list)
    assert rf_stats["records"].dtype == np.int64


def test_rainfall_statistics_with_metadata(rain_data_folder, station_metadata):
    """Extend rain stats with metadata"""
    rainfall_data = load_rain_folder(rain_data_folder)
    rf_stats = compute_rainfall_statistics(rainfall_data, station_metadata)
    assert set(rf_stats.columns) == set(
        ["year", "station", "x", "y", "records", "min", "median", "max"]
    )
