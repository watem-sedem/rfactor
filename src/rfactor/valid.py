from functools import wraps


def valid_column(rain, req_col):
    """Input dataframe has valid required columns

    Parameters
    ----------
    rain: pd.DataFrame
        To test dataframe
    req_col: set
        Required columns in dataframe, e.g. {"datetime", "rain_mm"}
    """
    # test for columns
    if not req_col.issubset(rain.columns):
        raise KeyError(f"DataFrame should contain {req_col}  columns.")


def valid_const_freq(rain):
    """Check if rainfall inputdata has constant frequency

    Parameters
    ----------
    rain: pandas.DataFrame
    """
    # constant frequency
    if len(rain["datetime"].diff().unique()) > 2:
        msg = (
            "Timeseries resolution is not a strict constant, please define "
            "rainfall timeseries with one temporal resolution."
        )
        raise IOError(msg)


def valid_freq(df_freq, req_freq=None):
    """Test for valid frequency of input data

    The frequency of the input data is tested to a defined frequency. Limit
    usage R-factor package to above 1-minute resolution.

    Parameters
    ----------
    df_freq: pandas.DatetimeIndex.freq
        Temporal frequency in the rainfall data
    req_freq: int, default None
        Required frequency (minutes). If None, the req_frequence should at least be
        1 minute.
    """
    # test for frequency
    if df_freq is None:
        msg = "Please define a frequency for your input timeseries."
        raise IOError(msg)

    # if required frequency is zeros, test if the dataframe is at least a one minute
    # resolution.
    if req_freq is None:

        if df_freq.nanos < 1000000000 * 60:
            msg = (
                "The R-factor package cannot process sub-minute rainfall input data, "
                "resample to at least a one minute resolution."
            )
            raise IOError(msg)

    else:
        if df_freq.nanos != 1000000000 * 60 * req_freq:
            msg = (
                f"Rainfall resolution should be equal to {req_freq} minutes, "
                f"resample input rainfall with the resample functionalities available"
                f" in this package."
            )
            raise IOError(msg)


def valid_rainfall_timeseries(
    func=None, req_col={"datetime", "rain_mm"}, req_freq=None
):
    """Customisable decorator to check pandas input rainfall data for functions used in
     this package.

    Parameters
    ----------
    func: callable, default None
    req_col: set
        See :func:`rfactor.process.valid_column`
    req_freq int
        See :func:`rfactor.process.valid_freq`

    Returns
    -------
    decorator: callable
        Return the execution of the actual decorator

    Notes
    -----
    Use super decorator to allow for decorator inputs
    """
    assert callable(func) or func is None

    def _decorator(func):
        """

        Parameters
        ----------
        func: callable
            Input function

        Returns
        -------
        wrapper: callable
            Wrapper function
        """

        @wraps(func)
        def wrapper(rain, **kwargs):
            """

            Parameters
            ----------
            rain: pandas.DataFrame
                Input rainfall dataseries
            kwarg: dict
                Keyword arguments

            Returns
            -------
            func: callable
                Return the execution of the function call
            """
            valid_column(rain, req_col)
            freq = rain.index.freq
            valid_freq(freq, req_freq)
            valid_const_freq(rain)
            return func(rain, **kwargs)

        return wrapper

    return _decorator(func) if callable(func) else _decorator
