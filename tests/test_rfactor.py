import numpy as np
import pandas as pd
import pytest
from pytest import approx

from rfactor import compute_erosivity, maximum_intensity, maximum_intensity_matlab_clone
from rfactor.rfactor import (
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
    with pytest.raises(Exception) as excinfo:
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
    with pytest.raises(Exception) as excinfo:
        _compute_erosivity(df, maximum_intensity)
    assert "contain data of a single year." in str(excinfo.value)


def test_compute_erosivity_multiple_years():
    """Erosivity input DataFrame should contain data of a single year"""
    df = pd.DataFrame(
        {
            "date": pd.date_range(start="2020-01-01 00:00", periods=2, freq="10min"),
            "rain": np.ones(2),
        }
    )
    with pytest.raises(Exception) as excinfo:
        _compute_erosivity(df, maximum_intensity)
    assert "should contain 'datetime' and 'rain_mm' columns" in str(excinfo.value)


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
    station, year, rain_benchmark_closure, erosivity_benchmark_data
):
    """Run the erosivity/rfactor calculation for single year/station combinations"""
    rain = rain_benchmark_closure(station, year)

    erosivity = compute_erosivity(rain)
    erosivity_reference = erosivity_benchmark_data[
        (erosivity_benchmark_data["year"] == year)
        & (erosivity_benchmark_data["station"] == station)
    ]

    pd.testing.assert_frame_equal(erosivity, erosivity_reference)

    # using support function provides the same output
    erosivity_support_func = _compute_erosivity(
        rain, intensity_method=maximum_intensity
    )
    erosivity_support_func.index = erosivity_support_func["datetime"]
    pd.testing.assert_frame_equal(
        erosivity.drop(columns=["tag", "station", "year"]), erosivity_support_func
    )


@pytest.mark.skip(reason="only works with full data set (not in package")
def test_rfactor_full_benchmark(rain_benchmark_data, erosivity_benchmark_data):
    """Run the full benchmark data set"""
    erosivity = compute_erosivity(rain_benchmark_data)
    pd.testing.assert_frame_equal(erosivity, erosivity_benchmark_data)
