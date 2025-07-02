import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from rfactor.process import (
    _days_since_start_year,
    compute_rainfall_statistics,
    get_rfactor_station_year,
    write_erosivity_data,
)
from rfactor.rain import load_rain_file_matlab_legacy, load_rain_folder


def test_days_since_last_year_float():
    """Moment of the day is translated as decimal number."""
    ts_series = pd.Series(
        pd.date_range("2021-01-01 00:00", "2021-01-02 00:00", freq="6h")
    )
    np.testing.assert_allclose(
        _days_since_start_year(ts_series).values, np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    )


def test_days_since_last_year_single_year():
    """Data should all be from the same year."""
    ts_series = pd.Series(
        pd.date_range("2020-12-31 00:00", "2021-01-02 00:00", freq="6h")
    )
    with pytest.raises(Exception):
        _days_since_start_year(ts_series)


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


def test_rainfall_statistics(rain_data_folder_matlab):
    """"""
    rainfall_data = load_rain_folder(
        rain_data_folder_matlab, load_rain_file_matlab_legacy
    )
    rf_stats = compute_rainfall_statistics(rainfall_data)
    assert set(rf_stats.columns) == set(["year", "records", "min", "median", "max"])
    assert isinstance(rf_stats["year"][0], list)
    assert rf_stats["records"].dtype == np.int64


def test_rainfall_statistics_with_metadata(rain_data_folder_matlab, station_metadata):
    """Extend rain stats with metadata"""
    rainfall_data = load_rain_folder(
        rain_data_folder_matlab, load_rain_file_matlab_legacy
    )
    rf_stats = compute_rainfall_statistics(rainfall_data, station_metadata)
    assert set(rf_stats.columns) == set(
        ["year", "station", "x", "y", "records", "min", "median", "max"]
    )
