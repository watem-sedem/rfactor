import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from rfactor.rain import (
    _check_path,
    _extract_metadata_from_file_path,
    load_rain_file,
    load_rain_file_flanders,
    load_rain_file_matlab_legacy,
    load_rain_folder,
)


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


@pytest.mark.parametrize(
    "fixture, load_fun",
    [
        ("rain_data_file_matlab", load_rain_file_matlab_legacy),
        ("rain_data_file_flanders", load_rain_file_flanders),
    ],
)
def test_load_rain_file(request, fixture, load_fun):
    """Valid rainfall data should be parsed to rain DataFrame"""
    rain_data_file = request.getfixturevalue(fixture)
    rainfall_data = load_rain_file(rain_data_file, load_fun)
    assert isinstance(rainfall_data, pd.DataFrame)

    assert list(rainfall_data.columns) == [
        "datetime",
        "station",
        "rain_mm",
        "year",
        "tag",
    ]
    assert list(rainfall_data["station"].unique()) == ["station_name"]
    assert list(rainfall_data.iloc[0].values) == [
        pd.to_datetime("2021-01-01 00:01:00"),
        "station_name",
        1.0,
        2021,
        "station_name_2021",
    ]
    assert list(rainfall_data.iloc[-1].values) == [
        pd.to_datetime("2021-12-31 23:59:00"),
        "station_name",
        10.00,
        2021,
        "station_name_2021",
    ]


class TestLoadRainFlandersSanitize:
    """Test the special data formatting cases of the Flanders rainfall data format."""

    def test_rain_flanders_nan(self, tmp_path):
        """Dashes, empty and negative values are interpreted as Nan and ignored in
        the result."""
        example_rain_path = tmp_path / "D1_2021.txt"
        example_rain_data = """\
            2021-01-01 00:00:00\t1.0
            2021-01-01 00:10:00\t---
            2021-01-01 00:20:00\t10.5
            2021-01-01 00:30:00\t-9.0
            """
        with open(example_rain_path, "w") as rain:
            rain.write(textwrap.dedent(example_rain_data))

        rainfall_data = load_rain_file(example_rain_path, load_rain_file_flanders)
        assert len(rainfall_data) == 2
        np.testing.assert_array_equal(
            rainfall_data["rain_mm"].values, np.array([1.0, 10.5])
        )

    def test_rain_flanders_threshold(self, tmp_path):
        """Rain intensities above certain values are ignored."""
        example_rain_path = tmp_path / "D1_2021.txt"
        example_rain_data = """\
            2021-01-01 00:00:00\t1.0
            2021-01-01 00:10:00\t10.5
            """
        with open(example_rain_path, "w") as rain:
            rain.write(textwrap.dedent(example_rain_data))

        rainfall_data = load_rain_file(
            example_rain_path, load_rain_file_flanders, threshold_outliers=10.0
        )
        assert len(rainfall_data) == 1
        np.testing.assert_array_equal(rainfall_data["rain_mm"].values, np.array([1.0]))

    def test_rain_flanders_interpolate(self, tmp_path):
        """Rain intensities gaps of length smaller than defined interval are
        interpolated using user-defined interpolation method."""
        example_rain_path = tmp_path / "D1_2021.txt"
        example_rain_data = """\
            2021-01-01 00:00:00\t1.0
            2021-01-01 00:10:00\t
            2021-01-01 00:20:00\t5.
            2021-01-01 00:30:00\t
            2021-01-01 00:40:00\t
            2021-01-01 00:50:00\t
            2021-01-01 01:00:00\t10.
            """
        with open(example_rain_path, "w") as rain:
            rain.write(textwrap.dedent(example_rain_data))

        rainfall_data = load_rain_file(
            example_rain_path, load_rain_file_flanders, interval=2, interpolate="pad"
        )
        assert len(rainfall_data) == 4
        expected = pd.DataFrame(
            [
                {
                    "datetime": pd.Timestamp("2021-01-01 00:00:00"),
                    "station": "D1",
                    "rain_mm": 1.0,
                    "year": np.int32(2021),
                    "tag": "D1_2021",
                },
                {
                    "datetime": pd.Timestamp("2021-01-01 00:10:00"),
                    "station": "D1",
                    "rain_mm": 1.0,
                    "year": np.int32(2021),
                    "tag": "D1_2021",
                },
                {
                    "datetime": pd.Timestamp("2021-01-01 00:20:00"),
                    "station": "D1",
                    "rain_mm": 5.0,
                    "year": np.int32(2021),
                    "tag": "D1_2021",
                },
                {
                    "datetime": pd.Timestamp("2021-01-01 01:00:00"),
                    "station": "D1",
                    "rain_mm": 10.0,
                    "year": np.int32(2021),
                    "tag": "D1_2021",
                },
            ]
        )
        pd.testing.assert_frame_equal(rainfall_data.reset_index(drop=True), expected)


def test_load_rain_file_with_folder(rain_data_folder_matlab):
    """When input is a file, should return ValueError to user"""

    with pytest.raises(ValueError) as excinfo:
        load_rain_file(rain_data_folder_matlab, load_rain_file_matlab_legacy)
    assert "a file instead of a directory" in str(excinfo.value)


def test_load_rain_folder(
    rain_data_folder_matlab, data_folder_non_existing, data_folder_empty
):
    """Rainfall data should be parsed to rain DataFrame
    when loading multiple files adding a year and tag column"""
    rainfall_data = load_rain_folder(
        rain_data_folder_matlab, load_rain_file_matlab_legacy
    )
    assert isinstance(rainfall_data, pd.DataFrame)
    assert list(rainfall_data.columns) == [
        "datetime",
        "station",
        "rain_mm",
        "year",
        "tag",
    ]
    assert list(rainfall_data["station"].unique()) == ["station_0", "station_1"]
    assert list(rainfall_data.iloc[0].values) == [
        pd.to_datetime("2020-01-01 00:01:00"),
        "station_0",
        1.0,
        2020,
        "station_0_2020",
    ]
    assert list(rainfall_data.iloc[-1].values) == [
        pd.to_datetime("2021-12-31 23:59:00"),
        "station_1",
        10.00,
        2021,
        "station_1_2021",
    ]
    with pytest.raises(FileNotFoundError) as excinfo:
        load_rain_folder(data_folder_non_existing, load_rain_file_matlab_legacy)
    assert f"Input folder '{data_folder_non_existing}' does not exists." in str(
        excinfo.value
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        load_rain_folder(data_folder_empty, load_rain_file_matlab_legacy)
    assert (
        f"Input folder '{data_folder_empty}' does not contain any 'txt'-files."
        in str(excinfo.value)
    )


def test_load_rain_folder_with_file(rain_data_file_matlab):
    """When input is a file, should return ValueError to user"""
    with pytest.raises(ValueError) as excinfo:
        load_rain_folder(rain_data_file_matlab, load_rain_file_matlab_legacy)
    assert "a directory instead of a file" in str(excinfo.value)


class TestCustomLoadRainFile:
    """Test column name/type checking for custom load functions."""

    def test_dataframe(self, rain_data_file_matlab):
        """Check if it returns a dataframe"""

        def function_no_dataframe(_):
            return "test"

        with pytest.raises(IOError) as excinfo:
            load_rain_file(rain_data_file_matlab, function_no_dataframe)
        assert "return pandas.DataFrame" in str(excinfo.value)

    def test_custom_wrong_columns(self, rain_data_file_matlab):
        """Wrong column names return IOError"""

        def function_wrong_columns(_):
            """Return wrong columns"""
            return pd.DataFrame(columns=["test"])

        with pytest.raises(IOError) as excinfo:
            load_rain_file(rain_data_file_matlab, function_wrong_columns)
        assert "must return columns 'datetime', 'station' and 'rain_mm'." in str(
            excinfo.value
        )

    def function_wrong_datetime(self, rain_data_file):
        """Wrong datetime column format (must be datetime64[ns])"""

        def function_wrong_datetime(_):
            """Return datetime type"""
            return pd.DataFrame(
                {"rain_mm": [0.0], "datetime": [0.0], "station": ["str"]}
            )

        with pytest.raises(IOError) as excinfo:
            load_rain_file(rain_data_file, function_wrong_datetime)
        assert "must return datetime64[ns] type" in str(excinfo.value)

    def function_wrong_station(self, rain_data_file):
        """Wrong station column format (must be str)"""

        def function_wrong_station(_):
            """Return station type"""
            return pd.DataFrame(
                {
                    "rain_mm": [0.0],
                    "datetime": pd.to_datetime("01/01/2024 00:00:00"),
                    "station": [0.0],
                }
            )

        with pytest.raises(IOError) as excinfo:
            load_rain_file(rain_data_file, function_wrong_station)
        assert "must return object (str) type" in str(excinfo.value)

    def function_wrong_value(self, rain_data_file):
        """Wrong value column format (must be float)"""

        def function_wrong_value(_):
            """Return value type"""
            return pd.DataFrame(
                {
                    "rain_mm": [""],
                    "datetime": pd.to_datetime("01/01/2024 00:00:00"),
                    "station": [""],
                }
            )

        with pytest.raises(IOError) as excinfo:
            load_rain_file(rain_data_file, function_wrong_value)
        assert " must return float for column" in str(excinfo.value)
