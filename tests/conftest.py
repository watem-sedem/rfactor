from rfactor.process import ErosivityData
from pathlib import Path

folder_data = Path("tests/data")

# references to input data
txt_files = (folder_data / "files.csv").absolute()
fmap_rainfall = (folder_data / "test_rainfalldata").absolute()
fmap_erosivity = (folder_data / "test_erosivitydata").absolute()


def create_data_instance_with_test_data():

    # create erosvity data instance and load data
    erosivitydata = ErosivityData(fmap_rainfall, fmap_erosivity)
    df_files = erosivitydata.build_data_set(txt_files)
    erosivitydata.load_data(df_files)

    return erosivitydata


erosivitydata = create_data_instance_with_test_data()
