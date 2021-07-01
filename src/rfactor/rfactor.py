import numpy as np
import pandas as pd

from joblib import Parallel, delayed
import multiprocessing as mp


TIME_BETWEEN_EVENTS = "6 hours"
MIN_CUMUL_EVENT = 1.27


def rain_energy_per_unit_depth(rain):
    """Calculate rain energy per unit depth according to Salles/Verstraeten

    # TODO -> check the factor 6 -> linked to 10min interval? Is this requirement?

    Parameters
    ----------
    rain : np.ndarray
        Rain (mm)

    Notes
    -----
    The rain energy per unit depth :math:`e_r` for an application for Flanders/Belgium,
    is defined by [1]_ [2]_ [3]_:

    .. math::

        e_r = 11.12i_r^{0.31}

    with

     - :math:`i_r` the rain intensity for every 10-min increment (mm :math:`\\text{h}^{-1}` ).

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
    """Maximum rain intensity for 30min interval (Matlab clone)

    The implementation is a direct Python-translation of the original Matlab
    implementation by Verstraeten.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with rainfall time series. Needs to contain the following columns:

        - *datetime* (pd.Timestamp): Time stamp
        - *rain_mm* (float): Rain in mm
        - *event_rain_cum* (float): Cumulative rain in mm

    Returns
    -------
    intensity : float
        maximal intensity in a 30minute interval
    """
    current_year = df["datetime"].dt.year.unique()
    if not len(current_year) == 1:
        raise Exception("Data should all be in the same year.")

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


def maximum_intensity(df, interval="30Min"):
    """Maximum rain intensity for 30min interval (Pandas rolling)

    The implementation uses a rolling window of the chosen interval to derive the
    maximal intensity.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with rainfall time series. Need to contain the following columns:

        - *datetime* (pd.Timestamp): Time stamp
        - *rain_mm* (float): Rain in mm
    interval : str
        Frequency str, e.g. '30Min'

    Returns
    -------
    intensity : float
        maximal intensity in a 30minute interval
    """
    # formula requires mm/hr, intensity is on half an hour
    return df.rolling(interval, on="datetime")["rain_mm"].sum().max() * 2


def compute_rfactor(
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
        derivation

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
    assert "datetime" in rain.columns
    assert "rain_mm" in rain.columns
    assert len(rain["datetime"].dt.year.unique()) == 1  # data of a single year
    # ?TODO -> if the enforcement of a single year required for this implementation
    # ?TODO -> check if we should enforce 10' interval as input? asfreq?

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
    # ?TODO - should we do this after or before exclusion of events below threshold?
    rain_events["all_event_rain_cum"] = (
        rain_events["event_rain_cum"].shift(1, fill_value=0.0).cumsum()
    )

    # remove events below threshold
    events = rain_events[rain_events["event_rain_cum"] > event_threshold].copy()

    # add cumulative erosivity
    events["erosivity_cum"] = events["erosivity"].cumsum()

    return events


def _apply_rfactor(name, group):
    """Wrapper helper function for parallel execution of erosivity on groups"""
    df = compute_rfactor(group, maximum_intensity)
    df[["station", "year"]] = name
    return df


def compute_rfactor_parallel(rain):
    """Calculate erosivity according to Verstraeten G. for each year/station combination

    Parameters
    ----------
    rain : pd.DataFrame
        DataFrame with rainfall time series. Need to contain the following columns:

        - *datetime* (pd.Timestamp): Time stamp
        - *rain_mm* (float): Rain in mm
        - *station* (str): Measurement station identifier
    """
    grouped = rain.groupby(["station", rain["datetime"].dt.year])
    results = Parallel(n_jobs=mp.cpu_count() - 1)(
        delayed(_apply_rfactor)(name, group) for name, group in grouped
    )
    all_erosivity = pd.concat(results)

    return all_erosivity
