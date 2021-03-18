import os
from datetime import timedelta, datetime
from pathlib import Path
from dataclasses import dataclass
import warnings
import numpy as np
import pandas as pd
from tqdm import tqdm
import pandas as pd

@dataclass
class ErosivityData():

    fmap_rainfall_data: Path
    fmap_erosivity_data: Path

    def __post_init__(self):

        self.fmap_rainfall = check_if_folder_exists(self.fmap_rainfall_data)
        self.fmap_erosivity = check_if_folder_exists(self.fmap_erosivity_data)
        self.lst_txt_rainfall = list(self.fmap_rainfall.glob('*.txt*'))
        self.lst_txt_erosivity = list(self.fmap_erosivity.glob('*.txt*'))
        self.check_number_of_files()

    def check_number_of_files(self):

        lst_rainfall = [txt.stem for txt in self.lst_txt_rainfall]
        lst_erosivity = [txt.stem.split("new")[0] for txt in self.lst_txt_erosivity]
        flag1 = check_missing_files(lst_rainfall,lst_erosivity,self.fmap_erosivity_data)
        flag2 = check_missing_files(lst_erosivity,lst_rainfall,self.fmap_rainfall_data)

        if flag1 or flag2:
            msg = "Unequal number of input rainfall and erosivity calculation files."
            IOError(msg)

    def build_data_set(self,txt_files):

        df_files = self.check_df_files(txt_files)

        return df_files

    def check_df_files(self,txt_files):
        df_files = pd.read_csv(txt_files)
        df_files["year"] = [i.split("_")[2] for i in
                                   df_files["datafile"]]
        df_files["station"] = [i.split("_")[0] + "_" + i.split("_")[1]
                                      for i
                                      in df_files["datafile"]]
        df_files.index = df_files["datafile"]
        df_files["fname_rainfall"]=""
        df_files["fname_erosivity"]=""
        for file in self.lst_txt_rainfall:
            datafile = file.stem
            if file.stem not in df_files.index:
                msg = f"'{file.stem}' not listed in '{Path(txt_files).absolute()}', please add the file datafile record and indicate if you want to consider it for analysis."
                raise IOError(msg)
            df_files.loc[datafile,"file_exists"] = 1
            df_files.loc[datafile,"fname_rainfall"] = self.fmap_rainfall / (datafile +".txt")
            df_files.loc[datafile,"fname_erosivity"] = self.fmap_erosivity / (datafile + "new cumdistr salles.txt")
        return df_files

    def load_data(self,df_files):

        self.stations = np.unique(df_files.loc[df_files["consider"]==1,"station"])
        self.dict_erosivity_data = {}
        self.dict_rainfall_data = {}
        self.lst_nr_files = {}
        for station in tqdm(self.stations):
            stationdata = StationData(station,df_files[df_files["station"]==station])
            dict_rainfall,dict_erosivity =stationdata.load_data()
            self.dict_rainfall_data[station]=dict_rainfall
            self.dict_erosivity_data[station]=dict_erosivity
            self.lst_nr_files[station] = stationdata.n_files
        self.nr_files = sum(self.lst_nr_files.values())

    def load_R(self,stations=[],years=[]):

        return load_R(self.dict_erosivity_data,stations,years)

def load_R(dict_erosivity_data,stations=[],years=[]):

    lst_df = []
    lst_stations=dict_erosivity_data.keys() if len(stations)==0 else stations
    for station in lst_stations:
        dict_R=load_R_station(dict_erosivity_data[station],years)
        df = pd.DataFrame.from_dict(dict_R,orient="index",columns=["value"])
        df["station"] = station
        lst_df.append(df)
    return pd.concat(lst_df)

def load_R_station(dict_erosivity_data,years=[]):

    dict_R = {}
    lst_years = dict_erosivity_data.keys() if len(years)==0 else years
    for year in lst_years:
        if year in dict_erosivity_data.keys():
            dict_R[year] = get_R(dict_erosivity_data,year)
    return dict_R

def get_R(dict_erosivity_data,year):

    return dict_erosivity_data[year]["cumEI30"].iloc[-1]

@dataclass
class StationData():

    station: str
    df_files: pd.DataFrame()

    def __post_init__(self):

        self.df_erosivity = pd.DataFrame()
        self.df_rainfall = pd.DataFrame()
        self.dict_erosivity = {}
        self.dict_rainfall = {}
        self.n_files = np.sum(self.df_files["consider"]==1)

    def load_data(self):

        dict_rainfall = {}
        dict_erosivity = {}

        if self.n_files>0:
            for index in self.df_files.index:
                year = self.df_files.loc[index,"year"]
                consider = self.df_files.loc[index,"consider"]
                fname_erosivity = self.df_files.loc[index,"fname_erosivity"]
                fname_rainfall = self.df_files.loc[index, "fname_rainfall"]
                if (consider==1) & (fname_rainfall!=""):
                    dict_rainfall[int(year)] = load_rainfall_data(fname_rainfall,self.station,year)
                    dict_erosivity[int(year)] = load_erosivity_data(fname_erosivity,year)

        return dict_rainfall,dict_erosivity


def load_rainfall_data(fname,station,year):

    fname = np.loadtxt(fname, delimiter=" ")
    df= pd.DataFrame(fname, columns=["timestamp", "value"])
    df["year"] = year
    df["station"] = station

    return df

def load_erosivity_data(fname,year):

    df = load_output_file(fname)
    df = assign_datetime_df_output(df.copy(), year)
    df = clip_output_df(df.copy(), year)

    return df

def clip_output_df(df,year):

    # if R-value goes out of bound, than map the last value in the year
    cond = df.index.year == int(year) + 1
    if np.sum(cond) > 0:
        maxR  = df["cumEI30"].iloc[-1]
        df.loc[df.index[-2],"cumEI30"] = maxR
        df = df.drop(df.index[len(df)-1])
    return df


def get_year_fname(fname,station):

    year = fname.replace(station, "")
    year = year.replace("_", "")
    year = "".join([x for x in year if x.isdigit()])

    return year

def assign_datetime_df_output(df,year,resample=False):

    startdate = datetime.strptime("01/01/" + year, "%d/%m/%Y")
    df.loc[:,"date"] = [startdate + timedelta(days=i) for i in df['day']]
    df.index = df["date"]
    if resample:
        df_resample = df[["cumEI30"]].resample("SM", closed="right").ffill()
        df_resample["doy"] = df_resample.index.dayofyear
        return df_resample
    else:
        df["doy"] =  df.index.dayofyear
        return df

def check_if_folder_exists(folder):

    if not folder.exists():
        msg = f"{folder} does not exists."
        raise IOError(msg)
    return folder

def check_missing_files(lst_target,lst_reference,fmap_reference):

    diff = set(lst_target)-set(lst_reference)
    flag=True
    if len(diff)>0:
        msg = f"{str(diff)} are not in {fmap_reference}"
        warnings.warn(msg)
        flag=False
    return flag

def load_data_completeness_file(txt_completeness):

    df_completeness = pd.read_csv(txt_completeness)
    df_completeness["year"] = [i.split("_")[2] for i in
                               df_completeness["datafile"]]
    df_completeness["station"] = [i.split("_")[0] + "_" + i.split("_")[1] for i
                                  in df_completeness["datafile"]]

    df_completeness.index = df_completeness["datafile"]

    return df_completeness

def load_input_data(fmap, df_completeness):
    """
    Load input data used for running matlab file marco.m

    Parameters
    ----------
    fmap: str
        the folder which holds the inputdata
    completeness: pandas.DataFrame
        columns: ["source","datafile","completeness","year","station"]
        index: datafile, name of the data files, i.e.  ["P01_003_2004", "P01_003_2005", ..],
        completeness: float
            in [0,1] degree of NaN in the non-zero timeseries

    Returns
    -------
    data: dictionary
        keys: str
            station names
        values: pandas.DataFrame
            columns: ["timestamp","value","year","station","completeness"]
    Notes
    -----
    These input data are non-zero timeseries for one year for one station, extracted from the source data of KMI and VMM

    """
    dict_inputdata = {}

    fmap =  Path(fmap)
    fmap.mkdir(parents=True, exist_ok=True)
    fnames = os.listdir(fmap)

    for i in fnames:

        station = i[:len(i)-1-i[::-1].index("_")]
        fname = np.loadtxt(os.path.join(fmap,i),delimiter=" ")
        temp = pd.DataFrame(fname,columns=["timestamp","value"])
        temp["year"] = i[len(i)-i[::-1].index("_"):i.index(".")]
        temp["station"] = station
        temp["completeness"] = df_completeness.loc[i.split(".")[0],"completeness"]
        if (station in list(dict_inputdata.keys())):
            dict_inputdata[station] = dict_inputdata[station].append(temp)
        else:
            dict_inputdata[station] = temp.copy()

    return dict_inputdata

def compute_statistics_inputdata(dict_inputdata,resmap,df_stations):
    """
    Compute the statistics for each station

    Parameters
    ----------
    dict_inputdata: dictionary
        see load_input_data
    resmap: string | pathlib.Path

    """
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

    """pd.concat(dict_inputdata)[["station", "year"]].drop_duplicates().sort_values(
        "station").groupby("station").aggregate(
        {"year": [np.min, np.max]}).reset_index().to_csv(resmap / "year.csv")"""

def get_files_rfactor_script(fmap,dict_inputdata,df_completeness, threshold=0.95):
    """
    Get the output files of the rfactors matlab scripts

    Parameters
    ----------
    fmap: str | pathlib.Path
        directory where matlab files are stored
    dict_inputdata: see 'data' in functin `load_input_data`
    threshold: float, default 0.95
        minimal coverage threshold required to consider Rfactor for year y and station s

    Returns
    -------
    dict_output_files: dictionary
        holding dataframes for each station {station:df_filename}
        df_filename: columns [tag,fname]
        fname is None if it is not considered for the analysis (completness <0.95)

    """
    dict_output_files = {}

    for station in list(dict_inputdata.keys()):
        tag = "cumdistr"
        fnames = [i for i in os.listdir(fmap) if (tag in i) & (station in i)]
        dict_output_files[station] = pd.DataFrame(data=np.empty([len(fnames), 2]),
                                   columns=["tag", "fname"])

        for i in range(len(fnames)):
            index = fnames[i].index(tag)
            year = fnames[i][index - 8:index - 4]
            compl = df_completeness.loc[station + "_" + year, "completeness"]
            if compl > threshold:
                dict_output_files[station].iloc[i] = [fnames[i][0:index],
                                       os.path.join(fmap, fnames[i])]
            else:
                dict_output_files[station].iloc[i] = [fnames[i][0:index], ""]

    return dict_output_files

def load_cumulative_erosivity(dict_df_output_files):
    """
    Load the cumulative erosivity for each year/station

    Parameters
    ----------
    dict_df_output_files: see get_files_rfactor_script

    Returns
    -------
    dict_df_output: dictionary
        holding the station and dataframe of the cumulative erosivity

    """
    dict_df_output = {}

    for station in dict_df_output_files.keys():
        dict_df_output[station] = process_output_station(dict_df_output_files[station], station)
    return dict_df_output

def process_output_station(df_output_files,station):

    lst_output = []
    for i in df_output_files.index:
        fname = df_output_files["fname"].loc[i]
        if (fname != ""):
            df = process_output_file(fname, station)
            lst_output.append(df)

    return pd.concat(lst_output)

def process_output_file(fname,station):

    df = load_output_file(fname)
    year = get_year_fname(fname, station)
    df = assign_datetime_df_output(df.copy(), year)
    df = clip_output_df(df.copy(), year)

    return df

def load_output_file(fname):

    arr = np.loadtxt(fname)
    df = pd.DataFrame(np.zeros([len(arr), 5]),
                      columns=["fname", "cumEI30", "day", "year","date"])
    df.loc[:,"cumEI30"] = arr[:, 1]
    df.loc[:,"day"] = arr[:, 0]
    df.loc[:,"fname"] = fname

    return df

def reformat_resolution(dict_df_output,resolution="hm"):
    """
    Reformat the dictionary of the dataframe 'output' to a half-montlhy basis

    Parameters
    ----------
    dict_df_output: dictionary
        see load_cumulative_erosivity

    Returns
    -------
    dict_df_output_hm: dictionary
        half monthly formatting of dict_output_file
    """
    dict_df_output_hm = {}

    for station in dict_df_output.keys():
        if resolution=="hm":
            dict_df_output_hm[station] = reformat_half_montlhy_analysis(dict_df_output[station])

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