import pytest
import numpy as np
from pathlib import Path
from .conftest import erosivitydata, fmap_rainfall_one_file, fmap_erosivity_one_file
from rfactor.rfactor import compute_rfactor
from rfactor.process import load_erosivity_data

@pytest.mark.parametrize(
    "debug,engine",
    [(True,"octave"),
     (False,"octave")],
)
@pytest.mark.externaldepedent
def test_rfactor(debug,engine):
    """test computation of r-factor

    Test the computation of the R-factor with as inputdata a non-zero rainfall
    time series.

    Parameters
    ----------
    debug: bool
        See :func:`rfactor.rfactor.compute_rfactor`
    engine: str
        See :func:`rfactor.rfactor.compute_rfactor`

    """

    fname = "KMI_6414_2004"
    compute_rfactor(fmap_rainfall_one_file, "results", engine=engine,debug=debug)
    f_test = Path(__file__).parent /".." / "src"/ "rfactor" / Path("results") / (fname + "new cumdistr salles.txt")
    df_test = load_erosivity_data(f_test, 2004)
    f_val = fmap_erosivity_one_file / (fname + "new cumdistr salles.txt")
    df_val = load_erosivity_data(f_val, 2004)

    np.testing.assert_allclose(
        df_val["cumEI30"], df_test["cumEI30"], rtol=1e-03, atol=1e-03
    )
    np.testing.assert_allclose(df_val["day"], df_test["day"], rtol=1e-03, atol=1e-03)


@pytest.mark.parametrize(
    "lst_exclude_stations,rfactor",
    [
        (["KMI_6447", "KMI_FS3"], 1171.538046511628),
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
            1137.910242587601,
        ),
    ],
)
def test_flanders(lst_exclude_stations, rfactor):
    """Test the aggregation functions of EI30 to compute an R-value. Pull all
    EI30 data from all years and stations, except the lst_stations defined in the
    test function parameters.

    Parameters
    ----------
    lst_exclude_stations: list
        List of stations (strings) to exclude from analysis.
    rfactor: float
        Aggregated R-value computed for all years and all lst_stations, except the
        ones listed in 'lst_exclude_stations'
    """
    lst_stations = [
        station for station in erosivitydata.stations if station not in lst_exclude_stations
    ]
    df_R = erosivitydata.load_R(lst_stations)

    np.testing.assert_allclose(np.mean(df_R["value"]), rfactor, atol=1e-2)


@pytest.mark.parametrize(
    "timeseries,rfactor",
    [
        (range(1898, 2003, 1), 958.1058095238096),
        (range(2003, 2021, 1), 1277.1105882352942),
        (range(1898, 2021, 1), 1002.5572950819673),
        (range(1996, 2021, 1), 1237.3845833333332),
        (range(1991, 2021, 1), 1239.4468965517242),
        (range(1990, 2001, 1), 1094.6436363636365),
        (range(2000, 2021, 1), 1272.774),
    ],
)
def test_ukkel(lst_timeseries, rfactor):
    """Test the aggregation functions of EI30 to compute an R-value for the
    station in Ukkel (Brussels, KMI_6447 and KMI_FS3). Pull all
    EI30 data from the years defined in timeseries,

    Parameters
    ----------
    lst_timeseries: list
        List of years (int) to include in the analysis.
    rfactor: float
        Aggregated R-value computed for all years and all stations, except the
        ones listed in 'exlude_stations'
    """
    df_R = erosivitydata.load_R(["KMI_6447", "KMI_FS3"], lst_timeseries)

    np.testing.assert_allclose(np.mean(df_R["value"]), rfactor, atol=1e-2)
