import multiprocessing as mp
from functools import partial

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

TIME_BETWEEN_EVENTS = "6 hours"
MIN_CUMUL_EVENT = 1.27


class RFactorInputError(Exception):
    """Raise when input data are not conform the rfactor required input format."""


class RFactorKeyError(Exception):
    """Raise when input data missing required column names."""


class RFactorTypeError(Exception):
    """Raise when input data data type of a data column is wrong."""


def rain_energy_per_unit_depth(rain):
    """Calculate rain energy per unit depth according to Salles/Verstraeten.

    Parameters
    ----------
    rain : numpy.ndarray
        Rain (mm)

    Returns
    -------
    energy : float
        Energy per unit depth.

    Notes
    -----
    The rain energy per unit depth :math:`e_r` (:math:`\\text{J}.\\text{mm}^{-1}.
    \\text{m}^{-2}`) for an application for Flanders/Belgium is defined
    by [1]_ [2]_ [3]_:

    .. math::

        e_r = 11.12i_r^{0.31}

    with

     - :math:`i_r` the rain intensity for every 10-min
       increment (mm :math:`\\text{h}^{-1}` ).

    References
    ----------
    .. [1] Salles, C., Poesen, J., Pissart, A., 1999, Rain erosivity indices and drop
        size distribution for central Belgium. Presented at the General Assembly of
        the European Geophysical Society, The Hague, The Netherlands, p. 280.

    .. [2] Salles, C., Poesen, J., Sempere-Torres, D., 2002. Kinetic energy of rain and
        its functional relationship with intensity. Journal of Hydrology 257, 256–270.
        https://doi.org/10.1016/S0022-1694(01)00555-8

    .. [3]  Verstraeten, G., Poesen, J., Demarée, G., Salles, C., 2006, Long-term
        (105 years) variability in rain erosivity as derived from 10-min rainfall
        depth data for Ukkel (Brussels, Belgium): Implications for assessing soil
        erosion rates. Journal Geophysysical Research, 111, D22109.
        https://doi.org/10.1029/2006JD007169
    """
    rain_energy = 0.1112 * ((rain * 6.0) ** 0.31) * rain
    return rain_energy.sum()


def maximum_intensity_matlab_clone(df):
    """Maximum rain intensity for 30-min interval (Matlab clone).

    The implementation is a direct Python-translation of the original Matlab
    implementation by Verstraeten.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with rainfall time series. Needs to contain the following columns:

        - *datetime* (pandas.Timestamp): Time stamp
        - *rain_mm* (float): Rain in mm
        - *event_rain_cum* (float): Cumulative rain in mm

    Returns
    -------
    maxprecip_30min : float
        Maximal 30-minute intensity during event (in mm/h).
    """
    if np.isnan(df["rain_mm"]).any():
        raise Exception(
            "Matlab intensity method does not support Nan values in rain" "time series."
        )

    current_year = df["datetime"].dt.year.unique()
    if not len(current_year) == 1:
        raise RFactorInputError("Data should all be in the same year.")

    df["minutes_since"] = (
        df["datetime"] - pd.Timestamp(f"{current_year[0]}-01-01")
    ).dt.total_seconds().values / 60

    timestamps = df["minutes_since"].values
    rain = df["rain_mm"].values
    rain_cum = df["event_rain_cum"].values

    maxprecip_30min = 0.0

    if timestamps[-1] - timestamps[0] <= 30:
        maxprecip_30min = rain[0] * 2  # *2 to mimick matlab

    for idx in range(len(df) - 1):
        eind_30min = timestamps[idx] + 20
        begin_rain = rain_cum[idx] - rain[idx]

        eind_rain = np.interp(eind_30min, timestamps, rain_cum)
        precip_30min = eind_rain - begin_rain

        if precip_30min > maxprecip_30min:
            maxprecip_30min = precip_30min

    return maxprecip_30min * 2


def maximum_intensity(df):
    """Maximum rain intensity for 30-min interval (Pandas rolling) expressed as mm/hour

    The implementation uses a rolling window of the chosen interval to derive the
    maximal intensity.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with rainfall time series. Needs to contain the following columns:

        - *datetime* (pandas.Timestamp): Timestamp
        - *rain_mm* (float): Rain in mm

    Returns
    -------
    maxprecip_30min : float
        Maximal 30-minute intensity during event (in mm/h).
    """
    # formula requires mm/hr, intensity is derived on half an hour
    return df.rolling("30min", on="datetime")["rain_mm"].sum().max() * 2


def _compute_erosivity(
    rain,
    intensity_method,
    event_split=TIME_BETWEEN_EVENTS,
    event_threshold=MIN_CUMUL_EVENT,
):
    """Calculate erosivity according to Verstraeten G. for a single year/station combi

    Parameters
    ----------
    rain : pd.DataFrame
        DataFrame with rainfall time series. Need to contain the following columns:

        - *datetime* (pd.Timestamp): Time stamp
        - *rain_mm* (float): Rain in mm
    intensity_method : Callable
        Function to derive the maximal rain intensity (over 30min)
    event_split : str
        Time interval to split into individual rain events
    event_threshold : float
        Minimal cumulative rain of an event to take into account for erosivity
        derivationevent_rain_cum

    Returns
    -------
    events : pd.DataFrame
        DataFrame with erosivity output for each event.

        - *datetime* (pd.Timestamp): Time stamp
        - *event_rain_cum* (float): Cumulative rain for each event
        - *max_30min_intensity* (float): Maximal 30min intensity for each event
        - *event_energy* (float): Rain energy per unit depth for each event
        - *erosivity* (float): Erosivity for each event
        - *all_events_cum* (float): Cumulative rain over all events together
        - *erosivity_cum* (float): Cumulative erosivity over all events together

    """
    if len(rain["datetime"].dt.year.unique()) != 1:  # data of a single year
        raise RFactorInputError("DataFrame should contain data of a single year.")

    # mark start of each rain event
    rain = rain[rain["rain_mm"] > 0.0]  # Only keep measurements with rain
    rain["event_start"] = False
    rain.loc[rain["datetime"].diff() >= event_split, "event_start"] = True
    rain.loc[rain.index[0], "event_start"] = True

    # add an event identifier
    rain["event_idx"] = rain["event_start"].cumsum()

    # add cumulative rain for each event
    rain["event_rain_cum"] = rain.groupby("event_idx")["rain_mm"].cumsum()

    # add rain energy for each event
    rain["event_energy"] = rain.groupby("event_idx")["rain_mm"].transform(
        rain_energy_per_unit_depth
    )

    # calculate the maximal rain intensity in 30minutes interval
    max_intensity_event = (
        rain.groupby("event_idx")[["datetime", "rain_mm", "event_rain_cum"]]
        .apply(intensity_method)
        .rename("max_30min_intensity")
        .reset_index()
    )
    rain = pd.merge(rain, max_intensity_event, how="left")

    # derive event summary
    columns = ["datetime", "event_rain_cum", "max_30min_intensity", "event_energy"]
    rain_events = rain.groupby("event_idx")[columns].agg(
        {
            "datetime": "first",
            "event_rain_cum": "last",
            "max_30min_intensity": "last",
            "event_energy": "last",
        }
    )

    # calculate the erosivity
    rain_events["erosivity"] = (
        rain_events["event_energy"] * rain_events["max_30min_intensity"]
    )

    # cumulative rain over all events
    rain_events["all_event_rain_cum"] = (
        rain_events["event_rain_cum"].shift(1, fill_value=0.0).cumsum()
    )

    # remove events below threshold
    events = rain_events[
        round(rain_events["event_rain_cum"], 2) > event_threshold
    ].copy()

    # add cumulative erosivity
    events["erosivity_cum"] = events["erosivity"].cumsum()

    return events


def _apply_rfactor(name, group, intensity_method):
    """Wrapper helper function for parallel execution of erosivity on groups"""
    df = _compute_erosivity(group, intensity_method)
    df[["station", "year"]] = name
    return df


def compute_erosivity(rain, intensity_method=maximum_intensity):
    """Calculate erosivity according to Verstraeten G. for each year/station combination

    Parameters
    ----------
    rain : pandas.DataFrame
        DataFrame with rainfall time series. Need to contain the following columns:

        - *datetime* (pandas.Timestamp): Time stamp
        - *rain_mm* (float): Rain in mm
        - *station* (str): Measurement station identifier

    intensity_method : Callable, default maximum_intensity
        Function to derive the maximal rain intensity (over 30min).

    Returns
    -------
    all_erosivity: pandas.DataFrame
        See :func:`rfactor.rfactor._compute_erosivity`, added with

        - *tag* (str): unique tag for year, station-couple.
    """
    if not {"station", "rain_mm", "datetime"}.issubset(rain.columns):
        raise RFactorKeyError(
            "DataFrame should contain 'datetime', 'rain_mm' and 'station' columns."
        )
    if not pd.core.dtypes.common.is_datetime64_any_dtype(rain["datetime"]):
        raise RFactorTypeError(
            "The 'datetime' column needs to be of a datetime data type."
        )
    if not pd.core.dtypes.common.is_string_dtype(rain["station"]):
        raise RFactorTypeError(
            "The 'station' column needs to be of a str/object data type."
        )
    if not pd.core.dtypes.common.is_float_dtype(rain["rain_mm"]):
        raise RFactorTypeError("The 'rain_mm' column needs to be of a float type.")

    rain["year"] = rain["datetime"].dt.year
    if "tag" not in rain.columns:
        rain["tag"] = rain["station"].astype(str) + "_" + rain["year"].astype(str)

    fun_with_method = partial(_apply_rfactor, intensity_method=intensity_method)
    grouped = rain.groupby(["station", "year"])
    results = Parallel(n_jobs=mp.cpu_count() - 1)(
        delayed(fun_with_method)(name, group) for name, group in grouped
    )
    all_erosivity = pd.concat(results)

    # couple tag
    all_erosivity = all_erosivity.merge(
        rain[["station", "year", "tag"]].drop_duplicates(), on=["station", "year"]
    )
    all_erosivity.index = all_erosivity["datetime"]

    return all_erosivity
