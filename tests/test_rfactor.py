import pytest
import pandas as pd

from rfactor import compute_erosivity


@pytest.mark.parametrize(
    "station,year",
    [
        ("P01_001", 2018),
        ("P01_010", 2016),
        ("P11_007", 2008),
        ("P01_003", 2020),
        ("P05_039", 2017),
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


@pytest.mark.slow
def test_rfactor_full_benchmark(rain_benchmark_data, erosivity_benchmark_data):
    """Run the full benchmark data set"""
    erosivity = compute_erosivity(rain_benchmark_data)
    pd.testing.assert_frame_equal(erosivity, erosivity_benchmark_data)
