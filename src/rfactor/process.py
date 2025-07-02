import numpy as np
import pandas as pd

# import for backward compatibility
from rfactor.rain import (  # noqa
    _check_path,
    load_rain_file,
    load_rain_file_flanders,
    load_rain_file_matlab_legacy,
    load_rain_folder,
)


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
                "rain_mm": ["min", "max", "median", "count"],
            }
        )
    ).reset_index()
    df_statistics.columns = df_statistics.columns.map("".join)
    rename_cols = {
        "year<lambda>": "year",
        "rain_mmamin": "min",
        "rain_mmamax": "max",
        "rain_mmmin": "min",
        "rain_mmmax": "max",
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
