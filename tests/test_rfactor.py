import numpy as np
import pandas as pd
import pytest
from pytest import approx

from rfactor import compute_erosivity, maximum_intensity, maximum_intensity_matlab_clone
from rfactor.rfactor import (
    RFactorInputError,
    RFactorKeyError,
    RFactorTypeError,
    _apply_rfactor,
    _compute_erosivity,
    rain_energy_per_unit_depth,
)


@pytest.mark.parametrize(
    "rain,energy",
    [
        (np.array([]), 0.0),  # empty input returns zero value (default numpy)
        (np.zeros(10), 0.0),
        (np.array([np.nan]), np.nan),
        (np.array([1.0]), 0.19379),
        (np.array([1.1, 1.2, 1.3]), 0.73891),
    ],
)
def test_rain_energy_per_unit_depth(rain, energy):
    """Rain energy calculation can handle zero arrays, zero values and nan."""
    assert energy == approx(rain_energy_per_unit_depth(rain), nan_ok=True, abs=1e-5)


@pytest.mark.parametrize(
    "rain_mm,intensity",
    [(np.ones(30), 6.0), (np.zeros(30), 0.0), (np.arange(30), 168.0)],
)
def test_maximum_intensity(rain_mm, intensity):
    """Maximum intsensity derivations provide the same output"""
    df = pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2021-01-01 00:00", periods=30, freq="10min"
            ),
            "rain_mm": rain_mm,
            "event_rain_cum": np.cumsum(rain_mm),  # single event
        }
    )
    assert intensity == approx(maximum_intensity(df), nan_ok=True, abs=1e-5)
    assert intensity == approx(
        maximum_intensity_matlab_clone(df), nan_ok=True, abs=1e-5
    )


def test_maximum_intensity_nan():
    """Maximum intsensity from matlab can not handle single nan-values, Python method
    supports Nan."""
    # single Nan value in the time series
    rain_with_single_nan = np.arange(30).astype(float)
    rain_with_single_nan[10] = np.nan
    df = pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2021-01-01 00:00", periods=30, freq="10min"
            ),
            "rain_mm": rain_with_single_nan,
            "event_rain_cum": np.cumsum(rain_with_single_nan),
        }
    )
    assert 168.0 == approx(maximum_intensity(df), abs=1e-5)
    with pytest.raises(Exception) as excinfo:
        maximum_intensity_matlab_clone(df)
    assert "does not support Nan values" in str(excinfo.value)

    # Only Nans in time series
    df = pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2021-01-01 00:00", periods=30, freq="10min"
            ),
            "rain_mm": np.empty(30) * np.nan,
        }
    )
    assert np.nan == approx(maximum_intensity(df), nan_ok=True, abs=1e-5)


def test_maximum_intensity_matlab_multiple_years():
    """Maximum intsensity from matlab can not handle data from multiple years."""
    df = pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2020-12-31 23:00", periods=30, freq="10min"
            ),
            "rain_mm": np.ones(30),
            "event_rain_cum": np.cumsum(np.ones(30)),
        }
    )
    with pytest.raises(RFactorInputError) as excinfo:
        maximum_intensity_matlab_clone(df)
    assert "should all be in the same year" in str(excinfo.value)


def test_maximum_intensity_short():
    """Maximum intsensity from time series shorter than 30Min provides intensity of
    period as such"""
    df = pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2020-01-01 00:00", periods=2, freq="10min"
            ),
            "rain_mm": np.ones(2),
            "event_rain_cum": np.cumsum(np.ones(2)),
        }
    )
    assert 4.0 == approx(maximum_intensity(df), abs=1e-5)
    assert 4.0 == approx(maximum_intensity_matlab_clone(df), abs=1e-5)


def test_compute_erosivity_wrong_df():
    """Erosivity input DataFrame should contain 'datetime' and 'rain_mm' columns."""
    df = pd.DataFrame(
        {
            "datetime": pd.date_range(
                start="2020-12-31 23:00", periods=30, freq="10min"
            ),
            "rain_mm": np.ones(30),
        }
    )
    with pytest.raises(RFactorInputError) as excinfo:
        _compute_erosivity(df, maximum_intensity)
    assert "contain data of a single year." in str(excinfo.value)


def test_apply_rfactor(rain_benchmark_closure):
    """apply_rfactor adds the station/year data to dataframe"""
    station, year = "P01_001", 2018
    rain = rain_benchmark_closure(station, year)
    erosivity_support_func = _compute_erosivity(rain, maximum_intensity)
    erosivity_apply_rfactor = _apply_rfactor((station, year), rain, maximum_intensity)

    pd.testing.assert_frame_equal(
        erosivity_support_func,
        erosivity_apply_rfactor.drop(columns=["station", "year"]),
    )


def test_erosivity_rain_single_yearstation(dummy_rain):
    """Erosivity calculation need to work on rain input dataframe with datetime,
    rain_mm and station only for a given year/station."""
    erosivity = compute_erosivity(dummy_rain)

    # year column added when not existing
    assert "year" in erosivity.columns
    assert erosivity["year"][0] == 2018

    # station column preserved
    assert erosivity["station"][0] == "P01_001"

    # tag column added when not existing
    assert "tag" in erosivity.columns
    assert erosivity["tag"][0] == "P01_001_2018"


def test_erosivity_rain_single_yearstation_wrong_datetime_dtype(dummy_rain):
    """Erosivity calculation with wrong datetime dtype returns error."""
    dummy_rain["datetime"] = dummy_rain["datetime"].astype(str)
    with pytest.raises(RFactorTypeError) as excinfo:
        compute_erosivity(dummy_rain)
    assert "'datetime' column needs to be of a datetime" in str(excinfo.value)


def test_erosivity_rain_single_yearstation_wrong_station_dtype(dummy_rain):
    """Erosivity calculation with wrong station dtype returns error."""
    dummy_rain["station"] = 44
    with pytest.raises(RFactorTypeError) as excinfo:
        compute_erosivity(dummy_rain)
    assert "'station' column needs to be of a str/object" in str(excinfo.value)


def test_erosivity_rain_single_yearstation_wrong_rain_dtype(dummy_rain):
    """Erosivity calculation with wrong datetime dtype returns error."""
    dummy_rain["rain_mm"] = "0.44"
    with pytest.raises(RFactorTypeError) as excinfo:
        compute_erosivity(dummy_rain)
    assert "'rain_mm' column needs to be of a float" in str(excinfo.value)


def test_erosivity_rain_single_yearstation_missing_column(dummy_rain):
    """Erosivity calculation need on rain input dataframe a datetime,
    rain_mm and station column."""

    with pytest.raises(RFactorKeyError) as excinfo:
        compute_erosivity(dummy_rain[["rain_mm", "datetime"]])
    assert "should contain 'datetime', 'rain_mm' and 'station'" in str(excinfo.value)
    with pytest.raises(RFactorKeyError) as excinfo:
        compute_erosivity(dummy_rain[["station", "datetime"]])
    assert "should contain 'datetime', 'rain_mm' and 'station'" in str(excinfo.value)
    with pytest.raises(RFactorKeyError) as excinfo:
        compute_erosivity(dummy_rain[["station", "rain_mm"]])
    assert "should contain 'datetime', 'rain_mm' and 'station'" in str(excinfo.value)


def test_erosivity_existing_tag(dummy_rain):
    """Existing tag is not overwritten. If not tag, new one is created."""
    dummy_rain["tag"] = "MY_UNIQUE_TAG"
    erosivity = compute_erosivity(dummy_rain)
    assert "tag" in erosivity.columns
    assert erosivity["tag"][0] == "MY_UNIQUE_TAG"


@pytest.mark.parametrize(
    "intensity_method", [(maximum_intensity), (maximum_intensity_matlab_clone)]
)
@pytest.mark.parametrize(
    "station,year",
    [
        ("P01_001", 2018),
        ("P01_003", 2020),
        ("P01_010", 2012),
        ("P01_010", 2016),
        ("P05_038", 2018),
        ("P05_039", 2017),
        ("P08_018", 2012),
        ("P09_032", 2020),
        ("P11_007", 2008),
        ("P11_024", 2012),
    ],
)
def test_rfactor_benchmark_single_year(
    station,
    year,
    rain_benchmark_closure,
    intensity_method,
    erosivity_benchmark_data,
    erosivity_benchmark_matlab_clone_data,
):
    """Run the erosivity/rfactor calculation for single year/station combinations"""
    rain = rain_benchmark_closure(station, year)

    if intensity_method == maximum_intensity:
        eros_benchmark = erosivity_benchmark_data
    else:
        eros_benchmark = erosivity_benchmark_matlab_clone_data

    erosivity = compute_erosivity(rain, intensity_method)
    erosivity_reference = eros_benchmark[
        (eros_benchmark["year"] == year) & (eros_benchmark["station"] == station)
    ]

    pd.testing.assert_frame_equal(erosivity, erosivity_reference)

    # using support function provides the same output
    erosivity_support_func = _compute_erosivity(rain, intensity_method=intensity_method)
    erosivity_support_func.index = erosivity_support_func["datetime"]
    pd.testing.assert_frame_equal(
        erosivity.drop(columns=["tag", "station", "year"]), erosivity_support_func
    )


@pytest.mark.skip(reason="only works with full data set (not in package")
def test_rfactor_full_benchmark(rain_benchmark_data, erosivity_benchmark_data):
    """Run the full benchmark data set"""
    erosivity = compute_erosivity(rain_benchmark_data)
    pd.testing.assert_frame_equal(erosivity, erosivity_benchmark_data)
