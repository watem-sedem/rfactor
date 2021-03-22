import os
from datetime import timedelta, datetime
from pathlib import Path
from dataclasses import dataclass
import warnings
import numpy as np
import pandas as pd
from tqdm import tqdm


@dataclass
class ErosivityData():
    """Build and load erosivity and rainfall data

    Data class containing references to all rainfall input data files (.txt)
    and computed erosivity data files (.txt).

    Parameters
    ----------
    fmap_rainfall: pathlib.Path
        Folder path to directory holding rainfall data. Rainfall data are
        stored in separate *.txt files per station and year. For the format of
        the `txt`-files, see :func:`rfactor.rfactor.load_rainfall_data`

    fmap_erosivity_data: pathlib.Path
        Folder path to directory holding erosivity data. Erosvity data are
        stored in separate *.txt files per station and year. For the format of
        the `txt`-files, see :func:`rfactor.rfactor.load_erosivity_data`

    Example
    -------
    >>> # Define input folders
    >>> fmap_rainfall=  Path(
    r'C:\Users\$USERNAME\GitHub\rfactor\rfactor\docs\data\example_inputdata')
    >>> fmap_erosivity = Path(
    r"C:\Users\\$USERNAME\GitHub\rfactor\src\rfactor\results")
    >>> txt_files= Path(r'C:\Users\$USERNAME\GitHub\rfactor\flanders\data
    \datafiles_completeness.csv')
    >>> # Compile and load data
    >>> data = ErosivityData(fmap_rainfall,fmap_erosivity)
    >>> df_files = data.build_data_set(txt_files)
    >>> data.load_data(df_files)
    >>> # Get dataframe with R for year 2018 and station KMI_6447 and KMI_FS3
    >>> df_R=data.load_R(["KMI_6447","KMI_FS3"], 2018)
    """

    fmap_rainfall_data: Path
    fmap_erosivity_data: Path

    def __post_init__(self):
        """Check if folders exist and number of files are equal
        """
        self.fmap_rainfall = check_if_folder_exists(self.fmap_rainfall_data)
        self.fmap_erosivity = check_if_folder_exists(self.fmap_erosivity_data)
        self.lst_txt_rainfall = list(self.fmap_rainfall.glob('*.txt*'))
        self.lst_txt_erosivity = list(self.fmap_erosivity.glob('*.txt*'))
        self.check_number_of_files()

    def check_number_of_files(self):
        """Check if the number of files in the rainfall and erosivity data
        folder are equal.
        """
        lst_rainfall = [txt.stem for txt in self.lst_txt_rainfall]
        lst_erosivity = [txt.stem.split("new")[0] for txt in
                         self.lst_txt_erosivity]
        flag1 = check_missing_files(lst_rainfall, lst_erosivity,
                                    self.fmap_erosivity_data)
        flag2 = check_missing_files(lst_erosivity, lst_rainfall,
                                    self.fmap_rainfall_data)

        if flag1 or flag2:
            msg = "Unequal number of input rainfall and erosivity " \
                  "calculation files."
            IOError(msg)

    def build_data_set(self, txt_files=None):
        """Build data set with the help of a text file, containing an overview
        of the to use rainfall and erosivity files.

        Parameters
        ----------
        txt_files: pathlib.Path
            File path of rainfall and erosivity overview file, see
            `:func:rfactor.rfactor.load_df_files`.

        Returns
        -------
        df_files: pandas.DataFrame
            Loaded txt_files data, see `:func:rfactor.rfactor.load_df_files`.
        """
        df_files = self.check_df_files(txt_files)

        return df_files

    def check_df_files(self, txt_files):
        """ Load and check if rainfall/erosivity datafile is tabulated the
        datafile overview file.

        Parameters
        ----------
        txt_files: pathlib.Path
            File path of rainfall and erosivity overview file, see
            `:func:rfactor.rfactor.load_df_files`.

        Returns
        -------
        df_files: pandas.DataFrame
            Loaded txt_files data, see `:func:rfactor.rfactor.load_df_files`.
        """
        df_files = load_df_files(txt_files)

        for file in self.lst_txt_rainfall:
            datafile = file.stem
            if file.stem not in df_files.index:
                msg = f"'{file.stem}' not liste" \
                      f"d in '{Path(txt_files).absolute()}', please add the " \
                      f"file datafile record and indicate if you want to " \
                      f"consider it for analysis."
                raise IOError(msg)
            df_files.loc[datafile, "file_exists"] = 1
            df_files.loc[datafile, "fname_rainfall"] = self.fmap_rainfall / (
                        datafile + ".txt")
            df_files.loc[datafile, "fname_erosivity"] = self.fmap_erosivity / (
                        datafile + "new cumdistr salles.txt")
        return df_files

    def load_data(self, df_files):
        """Load erosivity and rainfall data.

        This function loads the erosivity and rainfall data for each station.
        It only loads data for stations which have at least one year that is
        considered for analysis.

        Parameters
        ----------
        df_files: pandas.DataFrame
            Input file overview file, see
            `:func:rfactor.rfactor.load_df_files`.
        """
        self.stations = np.unique(
            df_files.loc[df_files["consider"] == 1, "station"])
        self.dict_erosivity_data = {}
        self.dict_rainfall_data = {}
        self.lst_nr_files = {}

        for station in tqdm(self.stations):
            stationdata = StationData(station,
                                      df_files[df_files["station"] == station])
            dict_rainfall, dict_erosivity = stationdata.load_data()
            self.dict_rainfall_data[station] = dict_rainfall
            self.dict_erosivity_data[station] = dict_erosivity
            self.lst_nr_files[station] = stationdata.n_files
        self.nr_files = sum(self.lst_nr_files.values())

    def load_R(self, stations=[], years=[]):
        """Load R-value for all/selected stations and years.

        For more info, see `:func:rfactor.rfactor.load_R`.

        Parameters
        ----------
        stations: list
            List of stations for which to load yearly R-value.

        years: list
            List of years for which to load yearly R-factor.

        Returns
        -------
        load_R: function
            see `:func:rfactor.rfactor.load_R`
        """
        return load_R(self.dict_erosivity_data, stations, years)


@dataclass
class StationData():
    """Load and process erosivity and rainfall data for one measurement
     station.

    station: str
        Name or code of the measurement station.
    df_files: pandas.DataFrame
        See `:func:rfactor.rfactor.load_df_files`.

    """

    station: str
    df_files: pd.DataFrame()

    def __post_init__(self):

        self.df_erosivity = pd.DataFrame()
        self.df_rainfall = pd.DataFrame()
        self.dict_erosivity = {}
        self.dict_rainfall = {}
        self.n_files = np.sum(self.df_files["consider"] == 1)

    def load_data(self):
        """Load erosivity and rainfall data per year

        Returns
        -------
        dict_rainfall: dict of {str: pandas.DataFrame}
            Holding rainfall data (in pandas.DataFrame) for every year, i.e.
            {*year*: *rainfall_data*}. For structure *rainfall_data*, see
            :func:`rfactor.rfactor.load_rainfall_data`.

        dict_erosivity: dict of {str: pandas.DataFrame}
            Holding erosivity data (in pandas.DataFrame) for every year, i.e.
            {*year*: *erosivity_data*}. For structure *rainfall_data*, see
            :func:`rfactor.rfactor.load_rainfall_data`.

        """
        dict_rainfall = {}
        dict_erosivity = {}

        if self.n_files > 0:
            for index in self.df_files.index:
                year = self.df_files.loc[index, "year"]
                consider = self.df_files.loc[index, "consider"]
                fname_erosivity = self.df_files.loc[index, "fname_erosivity"]
                fname_rainfall = self.df_files.loc[index, "fname_rainfall"]
                if (consider == 1) & (fname_rainfall != ""):
                    dict_rainfall[int(year)] = load_rainfall_data(
                        fname_rainfall, self.station, year)
                    dict_erosivity[int(year)] = load_erosivity_data(
                        fname_erosivity, year)

        return dict_rainfall, dict_erosivity


def load_df_files(txt_files):
    """Load overview file of rainfall and erosivity data

    Parameters
    ----------
    txt_files: pathlib.Path
        File path of overview file holding `datafile` tag (format
        "%STATION_%YEAR") and 'consider' column.

    Returns
    -------
    df_files: pandas.DataFrame
        loaded txt_files data with columns:

        - *datafile* (str): unique tag referring to rainfall and erosivity
        filename (format "%STATION_%YEAR" without suffix).
        - *year*: Year of registration.
        - *station*: Name or code of the measurement station.
        - *consider* (int): Consider file for year and station for
        analysis (0/1).
        - *fname_rainfall* (str): full path to rainfall input data file.
        - *fname_erosivity* (str): full path to erosivity data file.
    """
    df_files = pd.read_csv(txt_files)
    df_files = check_duplicates_df_files(df_files, txt_files)
    if "consider" not in df_files.columns:
        msg = f"Column 'consider' not file {txt_files}. Please add!"
        raise IOError(msg)
    if "year" not in df_files.columns:
        df_files["year"] = [i.split("_")[2] for i in
                            df_files["datafile"]]
    if "station" not in df_files.columns:
        df_files["station"] = [i.split("_")[0] + "_" + i.split("_")[1]
                               for i
                               in df_files["datafile"]]
    df_files.index = df_files["datafile"]
    df_files["fname_rainfall"] = ""
    df_files["fname_erosivity"] = ""

    return df_files


def check_duplicates_df_files(df_files, txt_files):
    df_files = df_files.drop_duplicates(['datafile', 'consider'])
    lst_datafiles = df_files["datafile"].to_list()
    for datafile in lst_datafiles:
        c = lst_datafiles.count(datafile)
        if c > 1:
            msg = f"Check duplicate and remove for {datafile} in {txt_files}"
            raise IOError(msg)
    return df_files


def load_R(dict_erosivity_data, stations=[], years=[]):
    """Load the yearly R-value for stations and years

    Load and return a dataframe of the erosivity data for the stations and
    years defined in the input.

    Parameters
    ----------
    dict_erosivity_data: dict of {str: dict}
        Dictionary format of erosivity data. The nested dict {station: dict}
        holds {str: pandas.DataFrame} (key: year, value: dataframe) with the
        dataframe being a format defined in
        func:`rfactor.rfactor.assign_datetime_df_erosivity`.
    stations: list, default []
        List of stations to load R-factor for. If list == [], then all data
        for all stations are loaded.
    years: list, default []
        List of years to load R-factor for. If years == [], then all data for
        all years are loaded.

    Return
    ------
    pandas.DataFrame
        Dataframe holding R-factor values for years and stations.

        - *station* (str): Name or code of the measurement station.
        - *year* (int): Year of registration.
        - *value* (float): R-value.
    """
    lst_df = []
    lst_stations = dict_erosivity_data.keys() if len(
        stations) == 0 else stations
    for station in lst_stations:
        dict_R = load_R_station(dict_erosivity_data[station], years)
        df = pd.DataFrame.from_dict(dict_R, orient="index", columns=["value"])
        df["station"] = station
        lst_df.append(df)
    return pd.concat(lst_df)


def load_R_station(dict_erosivity_data, years=[]):
    """Load the yearly R-value for years, for one station.

    Parameters
    ----------
    dict_erosivity_data: dict of {int: pd.DataFrame}
        Dictionary format of erosivity data (key: year, value: dataframe). For
        the format of the dataframe,
        see func:`rfactor.rfactor.assign_datetime_df_erosivity`.

    years: list, default []
        List of years to load R-factor for. If years == [], then all data for
        all years are loaded.

    Returns
    -------
    dict_R: dictionary of {int: float}
        R-values (value) for every year (key).
    """
    dict_R = {}
    lst_years = dict_erosivity_data.keys() if len(years) == 0 else years
    for year in lst_years:
        if year in dict_erosivity_data.keys():
            dict_R[year] = get_R_year(dict_erosivity_data, year)
    return dict_R


def get_R_year(dict_df_erosivity, year):
    """Get R-value from erosvity dictionary data format

    Parameters
    ----------
    dict_df_erosivity: dict of {str: pandas.DataFrame}
        Dictionary format of erosivity data (key: year, value: dataframe). For
        the format of the dataframe,
        see func:`rfactor.rfactor.assign_datetime_df_erosivity
    year: int
        Year of registration.

    Returns
    -------
    float
        R-value for year.
    """
    return dict_df_erosivity[year]["cumEI30"].iloc[-1]


def load_rainfall_data(fname, station, year):
    """ Load rainfall data file

    Load the rainfall data file in a pandas dataframe. Add headers.

    Parameters
    ----------
    fname: pathlib.Path
        File path to rainfall data file. This file contains no header, two
        columns, and a value for the depth of rainfall (mm) registered during
        the last x minutes. Please ensure the fname is of format
        "%STATION_%YEAR".
    station: str
        Name or code of the measurement station
    year: int
        Year of registration.

    Return
    ------
    df: pandas.DataFrame
        Holds non-zero rainfall time series for one year, one station
        - *timestamp* (int): number of passed minutes since start of the year.
        - *value* (float): amount of rainfal (mm) fallen during past x minutes.

    Notes
    -----
    1. The content of fname should be a non-zero timeseries:
        10  1.00
        20  0.20
        50  0.50
        60  0.30
        ... ...
    2. The rainfall datafile can only hold data for one year: maximum value
       for column one is 525600 (365 days) minutes (527040, leap year).
    """
    fname = np.loadtxt(fname, delimiter=" ")
    df = pd.DataFrame(fname, columns=["timestamp", "value"])
    df["year"] = year
    df["station"] = station

    return df


def load_erosivity_data(fname, year):
    """Load and process erosivity data

    Parameters
    ----------
    fname: pathlib.Path
        File path to erosivity data file. See :func:`load_erosivity_file`
    year: int
        Year of registration.

    Returns
    -------
    df: pandas.DataFrame
        See :func:`rfactor.flanders.data_processing.load_erosivity_file`
    """
    df = load_erosivity_file(fname)
    df = assign_datetime_df_erosivity(df.copy(), year)
    df = clip_erosivity_data(df.copy(), year)

    return df

def load_erosivity_file(fname):
    """Load in a single erosivity file.

    Parameters
    ----------
    fname: pathlib.Path
        File path to erosivity data file. This file contains no header, three
        columns: a time stamp (DOY, float), a cumulative value for the
        rainfall erosivity (MJ mm ha-1 h-1) (float).

    Returns
    -------
    df: pandas.DataFrame
        Cumulative erosivity (cumulative EI30) for day-of-the-year. Columns:
        - *day* (float): day of the year.
        - *cumEI30* (float): cumulative erosivity (MJ mm ha-1 h-1).
        - *fname* (pathlib.Path): file path of data source.
    """
    arr = np.loadtxt(fname)
    df = pd.DataFrame(np.zeros([len(arr), 5]),
                      columns=["fname", "cumEI30", "day", "year", "date"])
    df.loc[:, "cumEI30"] = arr[:, 1]
    df.loc[:, "day"] = arr[:, 0]
    df.loc[:, "fname"] = fname

    return df

def assign_datetime_df_erosivity(df, year, resample=False):
    """Compile a pandas datatime index from day-of-the-year column.

    Parameters
    ----------
    df: pandas.DataFrame
        See :func:`rfactor.flanders.load_erosivity_file`
    year: int
        Year of registration.
    resample: boolean, default False
        Resample to semi-montlhy format.

    Returns
    -------
    df: pandas.DataFrame
        Updated dataframe with datetime index added.
        - *index* (pd.datetime64 series).
        - *day* (float): day of the year.
        - *cumEI30* (float): cumulative erosivity (MJ mm ha-1 h-1).
        - *fname* (pathlib.Path): file path of data source.
    """
    startdate = datetime.strptime("01/01/" + year, "%d/%m/%Y")
    df.loc[:, "date"] = [startdate + timedelta(days=i) for i in df['day']]
    df.index = df["date"]
    if resample:
        df_resample = df[["cumEI30"]].resample("SM", closed="right").ffill()
        df_resample["doy"] = df_resample.index.dayofyear
        return df_resample
    else:
        df["doy"] = df.index.dayofyear
        return df


def clip_erosivity_data(df, year):
    """Clip erosivity data so it only contains data for the given year.

    Parameters
    ----------
    df: pandas.DataFrame
        See :func:`rfactor.rfactor.assign_datetime_df_erosivity`
    year: int
        Year of registration.

    Returns
    -------
    df: pandas.DataFrame
        Data set filtered to year.
    """
    # if R-value goes out of bound, than map the last value in the year
    cond = df.index.year == int(year) + 1
    if np.sum(cond) > 0:
        maxR = df["cumEI30"].iloc[-1]
        df.loc[df.index[-2], "cumEI30"] = maxR
        df = df.drop(df.index[len(df) - 1])
    return df


def check_if_folder_exists(folder):
    """Check if folder exists

    Parameters
    ----------
    folder: pathlib.Path
        input folder

    Return
    ------
    folder: pathlib.Path
        input folder

    """
    if not folder.exists():
        msg = f"{folder} does not exists."
        raise IOError(msg)
    return folder


def check_missing_files(lst_target, lst_reference, fmap_reference):
    """Check if file in either rainfall or erosivity input folder is missing.


    Parameters
    ----------
    lst_target: list
        List of to-test files, file path of files in pathlib.Path format.
    lst_reference: list
        List of file references, file path of files in pathlib.Path format.
    fmap_reference: pathlib.Path
        Folder path of reference files.

    Returns
    -------
    flag: boolean
        Difference between two folders is zero (True), else False

    Notes
    -----
    The files in both the erosivity and rianfall input folder have
    to be exactly the same (same number of files, same tags).
    """
    diff = set(lst_target) - set(lst_reference)
    flag = True
    if len(diff) > 0:
        msg = f"{str(diff)} are not in {fmap_reference}"
        warnings.warn(msg)
        flag = False
    return flag

"""
def compute_statistics_inputdata(dict_inputdata, resmap, df_stations):


    dict_stat = {}
    resmap = Path(resmap)
    resmap.mkdir(parents=True, exist_ok=True)

    for i in list(dict_inputdata.keys()):
        condition = dict_inputdata[i]["completeness"] > 0.95
        dict_stat[i] = dict_inputdata[i][condition].describe().transpose()
    dict_stat = pd.concat(dict_stat).reset_index()

    dict_stat = dict_stat[dict_stat["level_1"] == "value"]
    dict_stat["station"] = dict_stat["level_0"]
    dict_stat = dict_stat.merge(df_stations, on="station")
    dict_stat.to_csv(resmap / "rainfall_data_statistics_filtered_data.csv")

    pd.concat(dict_inputdata)[["station", "year"]].drop_duplicates(
    ).sort_values(
        "station").groupby("station").aggregate(
        {"year": [np.min, np.max]}).reset_index().to_csv(resmap / 
        "year.csv")




def reformat_resolution(dict_df_output, resolution="hm"):

    dict_df_output_hm = {}

    for station in dict_df_output.keys():
        if resolution == "hm":
            dict_df_output_hm[station] = reformat_half_montlhy_analysis(
                dict_df_output[station])

    return dict_df_output_hm


def reformat_half_montlhy_analysis(df_):
    cond = df_["cumEI30"].isnull()
    df_[cond] = 0.
    df_["year"] = df_.index.year
    df_["month"] = ["0" + i if len(i) == 1 else i for i in
                    df_.index.month.astype(str)]
    df_["day"] = ["0" + i if len(i) == 1 else i for i in
                  df_.index.day.astype(str)]
    cond = (df_["day"] == "29") & (df_["month"] == "02")
    df_["day"].loc[cond] = "28"
    df_['md'] = df_["month"] + df_["day"]
    df_ = df_.pivot(index="md", values="cumEI30",
                    columns="year")

    df_ = fill_cumulative_EI30(df_)

    return df_


def fill_cumulative_EI30(df_):
    for i in df_.columns:
        if np.sum(df_[i].isnull()) > 0:
            indices = df_[i].index
            for ind, item in enumerate(indices):
                if (np.isnan(df_[i].loc[item])) & (ind != 0):
                    df_[i].loc[item] = df_[i].iloc[ind - 1]

    return df_
"""