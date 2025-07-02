import re
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm


class RainfallFilesIOMsg(str):
    """Print message a string"""

    def __repr__(self):
        return str(self)


def _check_path(file_path):
    """Provide user feedback on file_path type."""
    if not isinstance(file_path, Path):
        if isinstance(file_path, str):
            raise TypeError(
                f"'file_path' should be a 'pathlib.Path' object, use "
                f"'Path({file_path})' to convert string file_path to valid 'Path'."
            )
        else:
            raise TypeError("'file_path' should be a pathlib.Path object")


def load_rain_file(file_path, load_fun, **kwargs):
    """Load file format of rainfall data with a given load function

    Parameters
    ----------
    file_path : pathlib.Path
        File path with rainfall data. Note that files in the folder should follow the
        input data format defined in the ``load_fun``.

    load_fun : Callable
        Please check the required input/output format for the files of the used load
        functions. The output of this function must comply with:

            - *datetime* (datetime64[ns]): timestamp, timezone naive
            - *station* (object): name of station, must be formatting accoring to a
              string.
            - *value* (float): in mm

    kwargs:
        Keyword arguments for load_fun


    Returns
    -------
    rain : pandas.DataFrame
        DataFrame with rainfall time series. Contains at least the following columns:

        - *rain_mm* (float): Rain in mm
        - *datetime* (pandas.Timestamp): Time stamp
        - *minutes_since* (float): Minutes since start of year.
        - *station* (str): station name
        - *year* (int): year of the measurement
        - *tag* (str): tag identifier, formatted as ``STATION_YEAR``
    """
    rain = load_fun(file_path, **kwargs)

    if not isinstance(rain, pd.core.frame.DataFrame):
        msg = f"Load function must '{load_fun.__name__}' return pandas.DataFrame"
        raise IOError(RainfallFilesIOMsg(msg))

    if not {"datetime", "station", "rain_mm"}.issubset(rain.columns):
        msg = (
            f"Load function '{load_fun.__name__}' must return columns 'datetime', "
            f"'station' and 'rain_mm'."
        )
        raise IOError(RainfallFilesIOMsg(msg))
    if not pd.api.types.is_datetime64_ns_dtype(rain["datetime"]):
        msg = (
            f"Load function '{load_fun.__name__}' must return datetime64[ns] type for "
            f"column 'datetime'."
        )
        raise IOError(RainfallFilesIOMsg(msg))
    if not pd.api.types.is_object_dtype(rain["station"]):
        msg = (
            f"Load function '{load_fun.__name__}' must return object (str) type for "
            f"column 'station'."
        )
        raise IOError(RainfallFilesIOMsg(msg))
    if not pd.api.types.is_float_dtype(rain["rain_mm"]):
        msg = (
            f"Load function '{load_fun.__name__}' must return float for column "
            f"'rain_mm'."
        )
        raise IOError(RainfallFilesIOMsg(msg))
    rain["year"] = rain["datetime"].dt.year
    rain["tag"] = rain["station"].astype(str) + "_" + rain["year"].astype(str)

    return rain


def load_rain_folder(folder_path, load_fun, **kwargs):
    """Load all (legacy Matlab format) files of rainfall data in a folder

    Parameters
    ----------
    folder_path : pathlib.Path
        Folder path with rainfall data, see also :func:`rfactor.process.load_rain_file`.
        Folder must contain txt files.

    load_fun : Callable
        Please check the required input format for the files in the above listed
        functions. The (custom) function must output:

        - *datetime* (datetime64[ns]): timestamp, timezone naive
        - *station* (object): name of station, must be formatting accoring to a string.
        - *value* (float): in mm

    kwargs:
        Keyword arguments for load_fun

    Returns
    -------
    rain : pandas.DataFrame
        See definition in :func:`rfactor.process.load_rain_file`
    """
    _check_path(folder_path)
    if not folder_path.exists():
        msg = f"Input folder '{folder_path}' does not exists."
        raise FileNotFoundError(msg)
    if folder_path.is_file():
        raise ValueError(
            "`folder_path` need to be the path " "to a directory instead of a file"
        )

    lst_df = []
    files = list(folder_path.glob("*.txt"))

    if len(files) == 0:
        msg = f"Input folder '{folder_path}' does not contain any 'txt'-files."
        raise FileNotFoundError(msg)

    for file_path in tqdm(files, desc="Processing input files"):
        df = load_rain_file(file_path, load_fun, **kwargs)
        lst_df.append(df)
    all_rain = pd.concat(lst_df)
    all_rain = all_rain.sort_values(["station", "datetime"])
    all_rain.index = range(len(all_rain))

    return all_rain


def _extract_metadata_from_file_path(file_path):
    """Get metadata from file name

    Expects to be 'STATION_NAME_YYYY.txt' as format with ``STATION_NAME`` the
    measurement station and the ``YYYY`` as the year of the measurement.

    Parameters
    ----------
    file_path : pathlib.Path
        File path of the file to extract station/year from

    Returns
    -------
    station: str
    year : str
    """
    if not re.fullmatch(".*_[0-9]{4}$", file_path.stem):
        raise ValueError(
            "Input file_path_format should " "match with 'STATION_NAME_YYYY.txt'"
        )
    station = "_".join(file_path.stem.split("_")[:-1])
    year = file_path.stem.split("_")[-1]
    return station, year


def load_rain_file_matlab_legacy(file_path):
    """Load (legacy Matlab) file format of rainfall data of a **single station/year**.

    The input files are defined by text files (extension: ``.txt``) that hold
    non-zero rainfall timeseries. The data are split per station and per year with
    a specific datafile tag (file name format: ``SOURCE_STATION_YEAR.txt``). The data
    should not contain headers, with the first column defined as 'minutes since the
    start of the year' and the second as the rainfall depth during the t last minutes
    (t is the temporal resolution of the timeseries).

    Parameters
    ----------
    file_path : pathlib.Path
        File path with rainfall data according to defined format, see notes.

    Returns
    -------
    rain : pandas.DataFrame
        DataFrame with rainfall time series. Contains the following columns:

        - *minutes_since* (int): Minutes since the start of the year
        - *rain_mm* (float): Rain in mm
        - *datetime* (pandas.Timestamp): Time stamp
        - *station* (str): station name

    Example
    -------
    1. Example of a rainfall file:

    ::

       9390 1.00 \n
       9470 0.20 \n
       9480 0.50 \n
       10770 0.10 \n
       ...  ...
    """
    if file_path.is_dir():
        raise ValueError(
            "`file_path` need to be the path " "to a file instead of a directory"
        )

    station, year = _extract_metadata_from_file_path(file_path)
    rain = pd.read_csv(
        file_path, delimiter=" ", header=None, names=["minutes_since", "rain_mm"]
    )
    if np.sum(rain["minutes_since"].isnull()) > 0:
        msg = (
            "Timestamp (i.e. minutes from start of year) column contains "
            "NaN-values. Input should be a (space-delimited) text file with the "
            "first column being the timestamp from the start of the year (minutes),"
            " and second the rainfall depth (in mm, non-zero series): \n \n9390 "
            "1.00\n9470 0.20\n9480 0.50\n... ..."
        )
        raise IOError(RainfallFilesIOMsg(msg))
    rain = rain.assign(
        datetime=pd.Timestamp(f"{year}-01-01")
        + pd.to_timedelta(pd.to_numeric(rain["minutes_since"]), unit="min")
    )

    rain = rain.assign(station=station)
    return rain[["datetime", "station", "rain_mm"]]


def load_rain_file_flanders(
    file_path, interpolate=None, interval=np.inf, threshold_outliers=None
):
    """Example load functions developed in context of Flanders.

    Translated the input file_path to the default input data used this package. This
    functions can be used for users an example to format functions. The file is a
    tab delimited files (extension: ``.txt``), and holds the timeseries for one
    location. The name of the file is the tag that will be used.

    Parameters
    ----------
    file_path: pathlib.Path
        File path (tab delimited, .txt-extension). Headerless

        - ``%d-%m-%Y %H:%M:%S``-format
        - float

    interpolate: str, default None
        Interpolation method to use for NaN-Values. Possible values:
        see pandas.DataFrame.interpolate.

    interval: int, default np.inf
        The max interval length over which NaN values are interpolated. The value
        needs to fit the index of the timeseries. For example, a timeseries with
        resolution of 10 min will have a maximum interval length of 6 hours if the
        interval value is set to 36 (36 * 10 min = 6 hours).

    threshold_outliers: int, default None
        Set rainfall values above this threshold to NaN.


    Returns
    -------
    rain : pandas.DataFrame
        DataFrame with rainfall time series. Contains the following columns:

        - *datetime* (pandas.Timestamp): Time stamp.
        - *minutes_since* (float): Minutes since start of year.
        - *station* (str): station identifier.
        - *rain_mm* (float): Rain in mm.

    Example
    -------
    1. Example of a rainfall file:

    ::

        2024-01-01 00:00:00	0.0
        2024-01-01 00:10:00	0.0
        2024-01-01 00:20:00	0.0
        2024-01-01 00:30:00	10.5
        2024-01-01 00:40:00	5.2
        2024-01-01 00:50:00	1
        2024-01-01 01:00:00	0.02
        2024-01-01 01:10:00

    Notes
    -----
    1. Current function is not maintained until further notice.
    """
    df = pd.read_csv(file_path, sep="\t", header=None, names=["datetime", "rain_mm"])

    if not {"datetime", "rain_mm"}.issubset(df.columns):
        msg = (
            f"File '{file_path}' should should contain columns 'datetime' and "
            f"'Value [millimeter]'"
        )
        raise KeyError(msg)

    df["datetime"] = pd.to_datetime(df["datetime"])
    df["start_year"] = pd.to_datetime(
        [f"01-01-{x} 00 : 00 : 00" for x in df["datetime"].dt.year],
    )
    station, year = _extract_metadata_from_file_path(file_path)
    df["station"] = station

    # todo: not mentioned in docs? necessary?
    nan = ["---", ""]
    df.loc[df["rain_mm"].isin(nan), "rain_mm"] = np.nan
    df.loc[df["rain_mm"] < 0, "rain_mm"] = np.nan

    if threshold_outliers is not None:
        df.loc[df["rain_mm"] > threshold_outliers, "rain_mm"] = np.nan

    # todo: search pandas alternative for forward filling
    if interpolate is not None:
        if df["rain_mm"].isna().any():
            # find indices for all NaN-values
            loc_nan = np.where(df["rain_mm"].isna())[0].tolist()

            temp = [loc_nan[0]]

            for i in loc_nan[1:]:  # loop over all NaN-indices
                if i != temp[-1] + 1 or i == loc_nan[-1]:
                    # check if indices are consequtive or if the final NaN-value is
                    # reached
                    if i == loc_nan[-1]:
                        temp.append(i)
                    if len(temp) > interval:
                        # check if lenght of consequetive indices > interval
                        # NaN-values serie > interval are set to 0.00 so they will not
                        # be interpolated and will be removed from the timeseries.
                        # NaN-value series <= interval will be kept as NaN-values
                        # which allows them to be interpolated.
                        df.loc[temp, "rain_mm"] = 0.00
                    temp = [i]
                elif i == temp[-1] + 1:  # check if indices are consequetive
                    temp.append(i)

            if interpolate is not None:
                df["rain_mm"] = df["rain_mm"].interpolate(method=interpolate)

    # remove 0
    df = df[df["rain_mm"] > 0]
    # remove NaN
    df = df[~df["rain_mm"].isna()]
    df["rain_mm"] = df["rain_mm"].astype(np.float64)

    return df[["datetime", "station", "rain_mm"]]
