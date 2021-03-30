import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from .conftest import erosivitydata, fmap_rainfall_one_file, fmap_erosivity_one_file
from rfactor.rfactor import compute_rfactor
from rfactor.process import load_erosivity_data


@pytest.mark.matlabbased
def test_rfactor():
    """test computation of r-factor

    Test the computation of the R-factor with as inputdata a non-zero rainfall
    time series.
    """
    fname = "KMI_6414_2004"

    compute_rfactor(fmap_rainfall_one_file, "matlab")

    f_test = Path("results") / (fname + "new cumdistr salles.txt")
    df_test = load_erosivity_data(f_test, 2004)
    f_val = fmap_erosivity_one_file / (fname + "new cumdistr salles.txt")
    df_val = load_erosivity_data(f_val, 2004)

    np.testing.assert_allclose(
        df_val["cumEI30"], df_test["cumEI30"], rtol=1e-03, atol=1e-03
    )
    np.testing.assert_allclose(df_val["day"], df_test["day"], rtol=1e-03, atol=1e-03)


@pytest.mark.parametrize(
    "exclude_stations,rfactor",
    [
        (["KMI_6447", "KMI_FS3"], 1263.2720860927154),
        (
            [
                "KMI_6447",
                "KMI_FS3",
                "KMI_6455",
                "KMI_6459",
                "KMI_6472",
                "KMI_6494",
                "KMI_6484",
            ],
            1235.2283858267717,
        ),
    ],
)
def test_flanders(exclude_stations, rfactor):
    """Test the aggregation functions of EI30 to compute an R-value. Pull all
    EI30 data from all years and stations, except the stations defined in the
    test function parameters.

    Parameters
    ----------
    exclude_stations: list
        List of stations (strings) to exclude from analysis.
    rfactor: float
        Aggregated R-value computed for all years and all stations, except the
        ones listed in 'exlude_stations'
    """
    stations = [
        station for station in erosivitydata.stations if station not in exclude_stations
    ]
    df_R = erosivitydata.load_R(stations)

    np.testing.assert_allclose(np.mean(df_R["value"]), rfactor, atol=1e-2)


@pytest.mark.parametrize(
    "timeseries,rfactor",
    [
        (range(1898, 2003, 1), 958.1058095238096),
        (range(2003, 2020, 1), 1313.013125),
        (range(1898, 2020, 1), 1005.0357024793389),
        (range(1996, 2020, 1), 1260.6330434782608),
        (range(1990, 2020, 1), 1244.8975862068964),
        (range(1990, 2001, 1), 1094.6436363636365),
        (range(2000, 2020, 1), 1302.7794736842104),
    ],
)
def test_ukkel(timeseries, rfactor):
    """Test the aggregation functions of EI30 to compute an R-value for the
    station in Ukkel (Brussels, KMI_6447 and KMI_FS3). Pull all
    EI30 data from the years defined in timeseries,

    Parameters
    ----------
    timeseries: list
        List of years (int) to include in the analysis.
    rfactor: float
        Aggregated R-value computed for all years and all stations, except the
        ones listed in 'exlude_stations'
    """
    df_R = erosivitydata.load_R(["KMI_6447", "KMI_FS3"], timeseries)

    np.testing.assert_allclose(np.mean(df_R["value"]), rfactor, atol=1e-2)
