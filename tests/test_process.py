import pytest
import re
from pathlib import Path


import numpy as np
import pandas as pd

from rfactor import compute_erosivity
from rfactor.process import (
    _days_since_start_year,
    _extract_metadata_from_file_path,
    _check_path,
    load_rain_file,
    load_rain_folder,
    write_erosivity_data,
    get_rfactor_station_year,
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
    """Split valid file names into station and name"""
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


def test_load_rain_folder(rain_data_foler):
    """Rainfall data should be parsed to rain DataFrame
    when loading multiple files adding a year and tag column"""
    rainfall_data = load_rain_folder(rain_data_foler)
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
    ]
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


@pytest.mark.parametrize(
    "debug,engine",
    [(True, "octave"), (False, "octave")],
)
@pytest.mark.externaldepedent
def test_rfactor(debug, engine):
    """test computation of r-factor

    Test the computation of the R-factor with as inputdata a non-zero rainfall
    time series.

    Parameters
    ----------
    debug: bool
        See :func:`rfactor.rfactor.compute_rfactor`
    engine: str
        See :func:`rfactor.rfactor.compute_rfactor`

    """

    fname = "KMI_6414_2004"
    compute_rfactor(fmap_rainfall_one_file, "results", engine=engine, debug=debug)
    f_test = (
        Path(__file__).parent
        / ".."
        / "src"
        / "rfactor"
        / Path("results")
        / (fname + "new cumdistr salles.txt")
    )
    df_test = load_erosivity_data(f_test, 2004)
    f_val = fmap_erosivity_one_file / (fname + "new cumdistr salles.txt")
    df_val = load_erosivity_data(f_val, 2004)

    np.testing.assert_allclose(
        df_val["cumEI30"], df_test["cumEI30"], rtol=1e-03, atol=1e-03
    )
    np.testing.assert_allclose(df_val["day"], df_test["day"], rtol=1e-03, atol=1e-03)


@pytest.mark.parametrize(
    "lst_exclude_stations,rfactor",
    [
        (["KMI_6447", "KMI_FS3"], 1171.538046511628),
        (
            [
                "KMI_6447",
                "KMI_FS3",
                "KMI_6455",
                "KMI_6459",
                "KMI_6472",
                "KMI_6494",
                "KMI_6484",
            ],
            1137.910242587601,
        ),
    ],
)
def test_flanders(lst_exclude_stations, rfactor):
    """Test the aggregation functions of EI30 to compute an R-value. Pull all
    EI30 data from all years and stations, except the lst_stations defined in the
    test function parameters.

    Parameters
    ----------
    lst_exclude_stations: list
        List of stations (strings) to exclude from analysis.
    rfactor: float
        Aggregated R-value computed for all years and all lst_stations, except the
        ones listed in 'lst_exclude_stations'
    """
    lst_stations = [
        station
        for station in erosivitydata.stations
        if station not in lst_exclude_stations
    ]
    df_R = erosivitydata.load_R(lst_stations)

    np.testing.assert_allclose(np.mean(df_R["value"]), rfactor, atol=1e-2)


@pytest.mark.parametrize(
    "lst_timeseries,rfactor",
    [
        (range(1898, 2003, 1), 958.1058095238096),
        (range(2003, 2021, 1), 1277.1105882352942),
        (range(1898, 2021, 1), 1002.5572950819673),
        (range(1996, 2021, 1), 1237.3845833333332),
        (range(1991, 2021, 1), 1239.4468965517242),
        (range(1990, 2001, 1), 1094.6436363636365),
        (range(2000, 2021, 1), 1272.774),
    ],
)
def test_ukkel(lst_timeseries, rfactor):
    """Test the aggregation functions of EI30 to compute an R-value for the
    station in Ukkel (Brussels, KMI_6447 and KMI_FS3). Pull all
    EI30 data from the years defined in timeseries,

    Parameters
    ----------
    lst_timeseries: list
        List of years (int) to include in the analysis.
    rfactor: float
        Aggregated R-value computed for all years and all stations, except the
        ones listed in 'exlude_stations'
    """
    df_R = erosivitydata.load_R(["KMI_6447", "KMI_FS3"], lst_timeseries)

    np.testing.assert_allclose(np.mean(df_R["value"]), rfactor, atol=1e-2)


@pytest.mark.parametrize(
    "generate_df_files,number_of_files_to_consider",
    [(True, 872), (False, 554)],
)
def test_build_dataset(generate_df_files, number_of_files_to_consider):
    """Test the building of the erosivity data set.

    Parameters
    ----------
    generate_df_files: bool
        Generate a df_files (holding references to files and whethet to consider
        them or not) automatically (if False you need to generate one yourself).
    number_of_files_to_consider: int
        Expected number of to consider files.
    """
    from .conftest import fmap_rainfall, fmap_erosivity, txt_files

    erosivitydata = ErosivityData(fmap_rainfall, fmap_erosivity)
    if generate_df_files:
        df_files = erosivitydata.build_data_set()
    else:
        df_files = erosivitydata.build_data_set(txt_files)
    assert number_of_files_to_consider == int(np.sum(df_files["consider"]))
