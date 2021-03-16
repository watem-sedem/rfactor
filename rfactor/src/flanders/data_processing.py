import os
from datetime import timedelta, datetime
from pathlib import Path

import numpy as np
import pandas as pd


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

def compute_statistics_inputdata(dict_inputdata,resmap):
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
    fmap_geo = Path(__file__).parent.absolute() / "geodata"
    stations_KMI_meta = pd.read_csv(fmap_geo / "geoinfo_KMI.csv", delimiter=";")
    stations_VMM_meta = pd.read_csv(fmap_geo / "geoinfo_VMM.csv", delimiter=",")
    stations_meta = stations_KMI_meta.append(stations_VMM_meta)
    dict_stat = dict_stat[dict_stat["level_1"] == "value"]
    dict_stat["station"] = dict_stat["level_0"]
    dict_stat = dict_stat.merge(stations_meta, on="station")
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
                dict_output_files[station].iloc[i] = [fnames[i][0:index], None]

    return dict_output_files

def load_cumulative_erosivity(dict_output_files):
    """
    Load the cumulative erosivity for each year/station

    Parameters
    ----------
    dict_output_files: see get_files_rfactor_script

    Returns
    -------
    dict_df_output: dictionary
        holding the station and dataframe of the cumulative erosivity

    """
    dict_df_output = {}

    for station in list(dict_output_files.keys()):
    
        ind = 0
        fnames = dict_output_files[station]["tag"].unique()
    
        for i in range(len(fnames)):

            if isinstance(dict_output_files[station]["fname"].iloc[i],str):
                temp3 = np.genfromtxt(dict_output_files[station]["fname"].iloc[i], delimiter=' ',
                                      skip_header=1, invalid_raise=False,
                                      filling_values=np.nan)
    
                temp = pd.DataFrame(np.zeros([len(temp3), 4]),
                                    columns=["fname", "cumEI30", "day", "year"])
                temp["cumEI30"] = temp3[:, 2].tolist()
                temp["day"] = temp3[:, 1].tolist()
                temp["fname"] = fnames[i]
    
                year = fnames[i];
                year = year.replace(station, "")
                year = year.replace("_", "")
                year = "".join([x for x in year if x.isdigit()])
    
                startdate = datetime.strptime("01/01/" + year, "%d/%m/%Y")
                temp["date"] = [startdate + timedelta(days=i) for i in temp['day']]
                temp.index = temp["date"]
                temp = temp[["cumEI30"]].resample("SM", closed="right").ffill()
                temp["doy"] = temp.index.dayofyear
                cond = temp.index.year == int(year) + 1
                if np.sum(cond) > 0:
                    temp["cumEI30"].iloc[-2] = temp["cumEI30"].iloc[-1]
                    temp = temp.iloc[:-1]
    
                if ind == 0:
                    dict_df_output[station] = temp.copy();
                    ind = 1
                else:
                    dict_df_output[station] = dict_df_output[station].append(temp)
                    
    return dict_df_output

def reformat_half_montlhy_analysis(dict_df_output):
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

    for station in list(dict_df_output.keys()):
        df_ = dict_df_output[station].copy()
        cond = df_["cumEI30"].isnull()
        df_[cond] = 0.
        df_["year"] = df_.index.year
        df_["month"] = ["0" + i if len(i) == 1 else i for i in
                        dict_df_output[station].index.month.astype(str)]
        df_["day"] = ["0" + i if len(i) == 1 else i for i in
                      dict_df_output[station].index.day.astype(str)]
        # 29th of fe
        cond = (df_["day"] == "29") & (df_["month"] == "02")
        df_["day"].loc[cond] = "28"
        df_['md'] = df_["month"] + df_["day"]
        dict_df_output_hm[station] = df_.pivot(index="md", values="cumEI30", columns="year")
        for i in dict_df_output_hm[station].columns:
            if np.sum(dict_df_output_hm[station][i].isnull()) > 0:
                indices = dict_df_output_hm[station][i].index
                for ind, item in enumerate(indices):
                    if (np.isnan(dict_df_output_hm[station][i].loc[item])) & (ind != 0):
                        dict_df_output_hm[station][i].loc[item] = dict_df_output_hm[station][i].iloc[
                            ind - 1]

    return dict_df_output_hm