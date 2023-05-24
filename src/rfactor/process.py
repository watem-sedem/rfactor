import re
from pathlib import Path

import numpy as np
import pandas as pd


class RainfallFilesIOMsg(str):
    """Print message a string"""

    def __repr__(self):
        return str(self)


def _days_since_start_year(series):
    """Translate datetime series to days since start of the year

    Parameters
    ----------
    series : pandas.Series
        Series with Datetime values. All datetime values should be of the same year.

    Returns
    -------
    days_since_start : pandas.Series
        Days since the start of the year as a float value.

    Notes
    -----
    Support function to provide integration with original Matlab implementation. Output
    is different from Pandas datetime attribute `dayofyear` as it includes time of the
    day as decimal value.
    """
    current_year = series.dt.year.unique()
    if not len(current_year) == 1:
        raise Exception("Input data should all be in the same year.")

    days_since_start = (
        (series - pd.Timestamp(f"{current_year[0]}-01-01")).dt.total_seconds()
        / 60.0
        / 1440.0
    )
    return days_since_start


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


def _check_path(file_path):
    """Provide user feedback on file_path type."""
    if not isinstance(file_path, Path):
        if isinstance(file_path, str):
            raise TypeError(
                f"`file_path` should be a `pathlib.Path` object, use "
                f"`Path({file_path})` to convert string file_path to valid `Path`."
            )
        else:
            raise TypeError("`file_path` should be a pathlib.Path object")


def load_rain_file(file_path, load_fun):
    """Load file format of rainfall data with a given load function

    Parameters
    ----------
    file_path : pathlib.Path
        File path with rainfall data. Note that files in the folder should follow the
        input data format defined in the ``load_fun``.

    load_fun : Callable
        Load function, current supported functions:

        - :func:`rfactor.process.load_rain_file_matlab_legacy`.
        - :func:`rfactor.process.load_rain_file_csv_vmm`

        Please check the required input format for the files in the above listed
        functions.


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
    if load_fun not in [load_rain_file_matlab_legacy, load_rain_file_csv_vmm]:
        msg = f"Rainfall load  function {load_fun} not implemented in R-factor package."
        raise IOError(msg)

    rain = load_fun(file_path)
    rain["year"] = rain["datetime"].dt.year
    rain["tag"] = rain["station"].astype(str) + "_" + rain["year"].astype(str)

    return rain


def compute_diagnostics(rain):
    """Compute diagnostics for input rainfall.

    This function computes coverage (per year, station) and missing rainfall for each
    month (per year, station).

    Parameters
    ----------
    rain: pandas.DataFrame
        DataFrame with rainfall time series. Contains at least the following columns:

        - *rain_mm* (float): Rain in mm
        - *datetime* (pandas.Timestamp): Time stamp
        - *station* (str): station name
        - *year* (int): year of the measurement
        - *tag* (str): tag identifier, formatted as ``STATION_YEAR``

    Returns
    -------
    diagnostics: pandas.DataFrame
        Diagnostics per station, year with coverage and identifier for no-rain per
        month. Computed based on non-zero rainfall timeseries.

        - *station* (str): station identifier.
        - *year* (int): year.
        - *coverage* (float): percentage coverage non-zero timeseries (see Notes).

        Added with per month (id's 1 to 12):

        - *months* (int):  1: no rain observed in month, 0: rain observed.


    Notes
    -----
    The coverage is computed as:

    .. math::

        C = 100*[1-\\frac{\\text{number of NULL-data}}
        {\\text{length of non-zero timeseries}}]
    """
    # compute coverage
    diagnostics = rain.groupby([rain["datetime"].dt.year, "station"]).aggregate(
        {"rain_mm": lambda x: 1 - np.sum(np.isnan(x)) / len(x)}
    )
    diagnostics = diagnostics.rename(columns={"rain_mm": "coverage"})

    # no-rain for months
    df = rain.groupby(
        [rain["datetime"].dt.year, rain["datetime"].dt.month, "station"]
    ).aggregate({"rain_mm": np.sum})
    df.index.names = ["datetime", "month", "station"]
    df["norain"] = 0
    df.loc[df["rain_mm"] == 0, "norain"] = 1
    df = df.pivot_table(
        columns=["month"], index=["station", "datetime"], values=["norain"]
    )
    df = df["norain"].reset_index()
    # check if months are in df reported
    for month in range(1, 13, 1):
        if month not in df.columns:
            df[month] = 1

    # couple
    diagnostics = diagnostics.merge(df, how="left", on=["station", "datetime"])
    diagnostics = diagnostics.rename(columns={"datetime": "year"})

    return diagnostics


def load_rain_file_csv_vmm(file_path):
    """Load VMM CSV file format of rainfall data of a **single station**.

    The input files are defined by comma delimited files (extension: ``.CSV``) that
    hold rainfall timeseries. The data are split per monitoring station and the file
    name should be the station identifier. The header should contain at least:

    - *Date/Time*
    - *Value [millimeter]*

    Parameters
    ----------
    file_path : pathlib.Path
        File path (comma delimited, .CSV-extension) with rainfall data according to
        defined format:

        - *Date/Time*: ``%d/%m/%Y %H:%M:%S``-format
        - *Value [millimeter]*: str (containing floats and '---'-identifier)

        Definition of additional columns are allowed.

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

        Date/Time,Value [millimeter]
        01/01/2019 00:00,"0"
        01/01/2019 00:05,"0.03"
        01/01/2019 00:10,"0.04"
        01/01/2019 00:15,"0"
        01/01/2019 00:20,"0"
        01/01/2019 00:25,"---"
        01/01/2019 00:30,"0"

    Notes
    -----
    Strings ``---`` in column *Value [millimeter]* -identifiers are converted to
    NaN-values (np.nan). Note that the values in string should be convertable to float
    (except ``---``).
    """
    df = pd.read_csv(file_path)
    if not {"Date/Time", "Value [millimeter]"}.issubset(set(df.columns)):
        msg = "Input dataframe should contain 'Date/Time' and 'Value [millimeter]'"
        raise KeyError(msg)
    else:
        df = df[["Date/Time", "Value [millimeter]"]].rename(
            columns={"Date/Time": "datetime", "Value [millimeter]": "rain_mm"}
        )
    df = df.assign(datetime=pd.to_datetime(df["datetime"], format="%d/%m/%Y %H:%M"))
    df = df.assign(
        start_year=pd.to_datetime(
            [f"01/01/{x} 00:00:00" for x in df["datetime"].dt.year],
            format="%d/%m/%Y %H:%M:%S",
        )
    )
    df = df.assign(station=file_path.stem)
    df.loc[df["rain_mm"] == "---", "rain_mm"] = np.nan
    df = df.assign(rain_mm=df["rain_mm"].astype(np.float64))

    return df[["datetime", "station", "rain_mm"]]


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
    _check_path(file_path)
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


def load_rain_folder(folder_path, load_fun):
    """Load all (legacy Matlab format) files of rainfall data in a folder

    Parameters
    ----------
    folder_path : pathlib.Path
        Folder path with rainfall data, see also :func:`rfactor.process.load_rain_file`.

    load_fun : Callable
        Load function, current supported functions:

        - :func:`rfactor.process.load_rain_file_matlab_legacy`.
        - :func:`rfactor.process.load_rain_file_csv_vmm`

        Please check the required input format for the files in the above listed
        functions.

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
    if load_fun.__name__ == "load_rain_file_csv_vmm":
        files = list(folder_path.glob("*.CSV"))
    elif load_fun.__name__ == "load_rain_file_matlab_legacy":
        files = list(folder_path.glob("*.txt"))
    else:
        msg = f"Load function '{load_fun.__name__}' not recognized in R-factor package."
        raise NotImplementedError(msg)

    if len(files) == 0:
        msg = f"Input folder '{folder_path}' does not contain any 'txt'-files."
        raise FileNotFoundError(msg)

    for file_path in files:
        df = load_rain_file(file_path, load_fun)
        lst_df.append(df)
    all_rain = pd.concat(lst_df)
    all_rain = all_rain.sort_values(["station", "datetime"])
    all_rain.index = range(len(all_rain))

    return all_rain


def write_erosivity_data(df, folder_path):
    """Write output erosivity to (legacy Matlab format) in folder.

    Written data are split-up for each year and station
    (file name format: ``SOURCE_STATION_YEAR.txt``) and does not contain any headers.
    The columns (no header!) in the written text files represent the following:

    - *days_since* (float): Days since the start of the year.
    - *erosivity_cum* (float): Cumulative erosivity over events.
    - *all_event_rain_cum* (float): Cumulative rain over events.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with rfactor/erosivity time series. Can contain multiple columns,
        but should have at least the following:

        - *datetime* (pandas.Timestamp): Time stamp
        - *station* (str): Station identifier
        - *erosivity_cum* (float): Cumulative erosivity over events
        - *all_event_rain_cum* (float): Cumulative rain over events

    folder_path : pathlib.Path
        Folder path to save data according to legacy Matlab format,
        see :func:`rfactor.process.load_rain_file`.

    """
    _check_path(folder_path)

    folder_path.mkdir(exist_ok=True, parents=True)

    for (station, year), df_group in df.groupby(["station", df["datetime"].dt.year]):
        df_group = df_group.assign(
            days_since=_days_since_start_year(df_group["datetime"])
        )
        formats = {
            "days_since": "{:.3f}",
            "erosivity_cum": "{:.2f}",
            "all_event_rain_cum": "{:.1f}",
        }
        for column, fformat in formats.items():
            df_group[column] = df_group[column].map(lambda x: fformat.format(x))
        df_group[["days_since", "erosivity_cum", "all_event_rain_cum"]].to_csv(
            folder_path / f"{station}_{year}.csv", header=None, index=None, sep=" "
        )


def get_rfactor_station_year(erosivity, stations=None, years=None):
    """Get R-factor at end of every year for each station from cumulative erosivity.

    Parameters
    ----------
    erosivity: pandas.DataFrame
        See :func:`rfactor.rfactor.compute_erosivity`
    stations: list
        List of stations to extract R for.
    years: list
        List of years to extract R for.

    Returns
    -------
    erosivity: pandas.DataFrame
        Updated with:

        - *year* (int): year
        - *station* (str): station
        - *erosivity_cum* (float): cumulative erosivity at
          end of *year* and at *station*.

    """

    if stations is not None:
        unexisting_stations = set(stations).difference(
            set(erosivity["station"].unique())
        )
        if unexisting_stations:
            raise KeyError(
                f"Station name(s): {unexisting_stations} not part of data set."
            )
        erosivity = erosivity.loc[erosivity["station"].isin(stations)]
    if years is not None:
        unexisting_years = set(years).difference(set(erosivity["year"].unique()))
        if unexisting_years:
            raise KeyError(f"Year(s): {unexisting_years} not part of data set.")
        erosivity = erosivity.loc[erosivity["year"].isin(years)]

    erosivity = erosivity.groupby(["year", "station"]).aggregate("erosivity_cum").last()
    erosivity = erosivity.reset_index().sort_values(["station", "year"])
    erosivity.index = range(len(erosivity))
    return erosivity


def compute_rainfall_statistics(df_rainfall, df_station_metadata=None):
    """Compute general statistics for rainfall timeseries.

    Statistics (number of records, min, max, median and years data) are
    computed for each measurement station

    Parameters
    ----------
    df_rainfall: pandas.DataFrame
        See :func:`rfactor.process.load_rain_file`
    df_station_metadata: pandas.DataFrame
        Dataframe holding station metadata. This dataframe has one mandatory
        column:

        - *station* (str): Name or code of the measurement station
        - *x* (float): X-coordinate of measurement station.
        - *y* (float): Y-coordinate of measurement station.

    Returns
    -------
    df_statistics: pandas.DataFrame
        Apart from the ``station``, ``x``, ``y`` when ``df_station_metadata`` is
        provided, the following columns are returned:

        - *year* (list): List of the years fror which data is available for the station.
        - *records* (int): Total number of records for the station.
        - *min* (float): Minimal measured value for the station.
        - *median* (float): Median measured value for the station.
        - *max* (float): Maximal measured value for the station.

    """
    df_rainfall = df_rainfall.sort_values(by="year")
    df_statistics = (
        df_rainfall[["year", "station", "rain_mm"]]
        .groupby("station")
        .aggregate(
            {
                "year": lambda x: sorted(set(x)),
                "rain_mm": [np.min, np.max, np.median, "count"],
            }
        )
    ).reset_index()
    df_statistics.columns = df_statistics.columns.map("".join)
    rename_cols = {
        "year<lambda>": "year",
        "rain_mmamin": "min",
        "rain_mmamax": "max",
        "rain_mmmedian": "median",
        "rain_mmcount": "records",
    }
    df_statistics = df_statistics.rename(columns=rename_cols)

    if df_station_metadata is not None:
        df_statistics = df_statistics.merge(
            df_station_metadata, on="station", how="left"
        )
        df_statistics = df_statistics[
            [
                "year",
                "station",
                "x",
                "y",
                "records",
                "min",
                "median",
                "max",
            ]
        ]
    else:
        df_statistics = df_statistics[["year", "records", "min", "median", "max"]]

    return df_statistics
