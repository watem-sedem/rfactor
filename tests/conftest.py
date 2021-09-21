import pytest
import textwrap
from pathlib import Path

import pandas as pd


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
def rain_data_foler(tmp_path):
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
def dummy_erosivity():
    """Return"""
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
    return pd.DataFrame(
        {
            "datetime": pd.to_datetime(dates),
            "all_event_rain_cum": all_event_rain_cum,
            "erosivity_cum": erosivity_cum,
            "station": stations,
        }
    )


# folder_data = Path("tests/data")
# folder_example = Path("docs/example_data/")
#
# # references to input data
# txt_files = (folder_data / "files_tests.csv").absolute()
# fmap_rainfall = (folder_data / "test_rainfalldata").absolute()
# fmap_erosivity = (folder_data / "test_erosivitydata").absolute()
#
# fmap_rainfall_one_file = (folder_example / "rainfall").absolute()
# fmap_erosivity_one_file = (folder_example / "erosivity").absolute()
#
# def create_data_instance_with_test_data():
#     """
#     Compile database with test rainfall and erosivity data
#
#     The aim of this function is to create a data instance with the given test
#     data. This data instance will be used in the test functions to compute
#     EI30 and R-values. Make use of files.csv file to define which specific
#     input data files are considered to compute EI30 and R-factor values.
#
#     Returns
#     -------
#     erosivitydata: rfactor.process.ErosivityData
#         See :class:`rfactor.process.ErosivityData`
#     """
#     # create erosvity data instance and load data
#     erosivitydata = ErosivityData(fmap_rainfall, fmap_erosivity)
#     df_files = erosivitydata.build_data_set(txt_files)
#     erosivitydata.load_data(df_files)
#
#     return erosivitydata
#
#
# erosivitydata = create_data_instance_with_test_data()
