import pandas as pd
import pytest

from rfactor.valid import valid_column, valid_const_freq, valid_freq


def test_valid_rainfall_timeseries():
    """Test subfunctionalities of valid_rainfall_timeseries decorator"""
    idx = pd.date_range("2018-01-01 03:30", periods=2, freq="1S")
    val = [0.06, 0.08]

    df = pd.DataFrame(columns=["datetime", "rain_mm"])
    df["datetime"] = idx
    df.index = df["datetime"]
    df["rain_mm"] = val

    with pytest.raises(KeyError) as excinfo:
        valid_column(df, {"datetime", "rain"})
    assert "should contain" in str(excinfo.value)

    freq = df.index.freq
    with pytest.raises(IOError) as excinfo:
        valid_freq(freq)
    assert "Please define a frequency for your input timeseries" in str(excinfo.value)

    df.index.freq = "1S"
    freq = df.index.freq

    with pytest.raises(IOError) as excinfo:
        valid_freq(freq)
    assert "The R-factor package cannot process sub-minute " in str(excinfo.value)

    with pytest.raises(IOError) as excinfo:
        valid_freq(freq, req_freq=10)
    assert "Rainfall resolution should be equal to 10 minutes" in str(excinfo.value)

    idx = pd.DatetimeIndex(["2018-01-01 03:30", "2018-01-01 03:31", "2018-01-01 03:33"])
    val = [0.06, 0.08, 0.0]
    df = pd.DataFrame(columns=["datetime", "rain_mm"])
    df["datetime"] = idx
    df["rain"] = val
    with pytest.raises(IOError) as excinfo:
        valid_const_freq(df)
    assert "Timeseries resolution is not a strict constant" in str(excinfo.value)
