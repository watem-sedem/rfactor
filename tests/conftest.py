from pathlib import Path

from rfactor.process import ErosivityData

folder_data = Path("tests/data")
folder_example = Path("docs/example_data/")

# references to input data
txt_files = (folder_data / "files_tests.csv").absolute()
fmap_rainfall = (folder_data / "test_rainfalldata").absolute()
fmap_erosivity = (folder_data / "test_erosivitydata").absolute()

fmap_rainfall_one_file = (folder_example / "rainfall").absolute()
fmap_erosivity_one_file = (folder_example / "erosivity").absolute()


def create_data_instance_with_test_data():
    """
    Compile database with test rainfall and erosivity data

    The aim of this function is to create a data instance with the given test
    data. This data instance will be used in the test functions to compute
    EI30 and R-values. Make use of files.csv file to define which specific
    input data files are considered to compute EI30 and R-factor values.

    Returns
    -------
    erosivitydata: rfactor.process.ErosivityData
        See :class:`rfactor.process.ErosivityData`
    """
    # create erosvity data instance and load data
    erosivitydata = ErosivityData(fmap_rainfall, fmap_erosivity)
    df_files = erosivitydata.build_data_set(txt_files)
    erosivitydata.load_data(df_files)

    return erosivitydata


erosivitydata = create_data_instance_with_test_data()
