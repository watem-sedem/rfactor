import pytest
import textwrap
from pathlib import Path


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
