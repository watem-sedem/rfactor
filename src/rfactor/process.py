from pathlib import Path

import numpy as np
import pandas as pd


def _days_since_start_year(df):
    """Translate datetime series to days since start of the year

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with Datetime values. All datetime values should be of the same year.
        Need to contain the following columns:

        - *datetime* (pd.Timestamp): Time stamp

    Returns
    -------
    days_since_start : pd.Series
        days since the start of the year

    Notes
    -----
    Support function to provide integration with original Matlab implementation.
    """
    current_year = df["datetime"].dt.year.unique()
    if not len(current_year) == 1:
        raise Exception("Data should all be in the same year.")

    days_since_start = (
        (df["datetime"] - pd.Timestamp(f"{current_year[0]}-01-01")).dt.total_seconds()
        / 60.0
        / 1440.0
    )
    return days_since_start


def _extract_metadata_from_file_path(file_path):
    """Get metadata from file name

    Expects to be 'STATION_NAME_YYYY.txt' as format

    Parameters
    ----------
    file_path : pathlib.Path
        File path of the file to extract station/year from
    """
    return {
        "station": "_".join(file_path.stem.split("_")[:-1]),
        "year": file_path.stem.split("_")[-1],
    }


def _check_path(file_path):
    """Provide user feedback on file_path specification"""
    if not isinstance(file_path, Path):
        if isinstance(file_path, str):
            raise TypeError(
                f"file_path should be a pathlib.Path object, use "
                f"Path({file_path}) to convert string file_path to Path."
            )
        else:
            raise TypeError(f"file_path should be a pathlib.Path object")


def load_rain_file(file_path):
    """Load (legacy Matlab) file format of rainfall data of a single station/year

    The input files are defined by text files (extension: ``.txt``) that hold
    non-zero rainfall timeseries. The data are split per station and per year with
    a specific datafile tag (file name format: SOURCE_STATION_YEAR.txt)

    TODO -> not requiring non-zero time series would improve the intensity measurement
      within the Python-implementation making sure these are handled well is possible.

    Parameters
    ----------
    file_path : pathlib.Path
        File path with rainfall data

    Returns
    -------
    rain : pd.DataFrame
        DataFrame with rainfall time series. Contains the following columns:

        - *datetime* (pd.Timestamp): Time stamp
        - *rain_mm* (float): Rain in mm
    """
    _check_path(file_path)

    station, year = _extract_metadata_from_file_path(file_path).values()
    rain = pd.read_csv(
        file_path, delimiter=" ", header=None, names=["minutes_since", "rain_mm"]
    )
    rain["datetime"] = pd.Timestamp(f"{year}-01-01") + pd.to_timedelta(
        rain["minutes_since"], unit="min"
    )
    rain["station"] = station
    return rain


def load_rain_folder(folder_path):
    """Load all (legacy Matlab format) files of rainfall data in a folder

    Parameters
    ----------
    file_path : pathlib.Path
        Folder path with rainfall data according to legacy Matlab format,
        see :func:`rfactor.process.load_rain_file`.

    Returns
    -------
    rain : pd.DataFrame
        DataFrame with rainfall time series. Contains the following columns:

        - *datetime* (pd.Timestamp): Time stamp
        - *rain_mm* (float): Rain in mm
    """
    _check_path(folder_path)

    lst_df = []
    for file_path in folder_path.glob("*.txt"):
        lst_df.append(load_rain_file(file_path))

    all_rain = pd.concat(lst_df)
    all_rain = all_rain.sort_values(["station", "minutes_since"])
    all_rain.index = range(len(all_rain))
    return all_rain


def write_erosivity_data(df, folder_path):
    """Write output erosivity to (legacy Matlab format) in folder

    Written data is split up for each year and station
    (file name format: SOURCE_STATION_YEAR.txt) and do not contain any headers. The
    columns in the written text files represent the following:

    - *days_since* (float): Days since the start of the year
    - *erosivity_cum* (float): Cumulative erosivity over events
    - *all_event_rain_cum* (float): Cumulative rain over events

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with rfactor/erosivity time series. Coan contain, multiple columns,
        but should have at least the following:

        - *datetime* (pd.Timestamp): Time stamp
        - *station* (str): Station identifier
        - *days_since* (float): Days since the start of the year
        - *erosivity_cum* (float): Cumulative erosivity over events
        - *all_event_rain_cum* (float): Cumulative rain over events

    folder_path : pathlib.Path
        Folder path with rainfall data according to legacy Matlab format,
        see :func:`rfactor.process.load_rain_file`.

    """
    _check_path(folder_path)

    folder_path.mkdir(exist_ok=True, parents=True)

    for (station, year), df_group in df.groupby(["station", df["datetime"].dt.year]):
        df_group["days_since"] = _days_since_start_year(df_group)
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


def compute_rainfall_statistics(df_rainfall, df_station_metadata=None):
    """Compute general statistics for rainfall timeseries

    Statistics (number of records, min, max, median and years data) are
    computed for each measurement station

    Parameters
    ----------
    df_rainfall: pandas.DataFrame
        See :func:`rfactor.process.load_dict_format`
    df_station_metadata: pandas.DataFrame
        Dataframe holding station metadata. This dataframe has one mandatory
        column:

        - *station* (str): Name or code of the measurement station

    Returns
    -------
    df_statistics: pandas.DataFrame

    """
    df_rainfall["year"] = df_rainfall["year"].astype(int)
    df_rainfall = df_rainfall.sort_values(by="year")
    df_statistics = (
        df_rainfall[["year", "station", "value"]]
        .groupby("station")
        .aggregate(
            {
                "year": lambda x: sorted(set(x)),
                "value": [np.min, np.max, np.median, lambda x: np.shape(x)[0]],
            }
        )
    )
    if df_station_metadata is not None:
        df_statistics = df_statistics.merge(
            df_station_metadata, on="station", how="left"
        )

    df_statistics["year"] = df_statistics[("year", "<lambda>")]
    df_statistics["min"] = df_statistics[("value", "amin")]
    df_statistics["median"] = df_statistics[("value", "median")]
    df_statistics["max"] = df_statistics[("value", "amax")]
    df_statistics["records"] = df_statistics[("value", "<lambda_0>")]

    if df_station_metadata is not None:
        return df_statistics[
            ["station", "year", "location", "x", "y", "records", "min", "median", "max"]
        ]
    else:
        return df_statistics[["station", "year", "records", "min", "median", "max"]]
