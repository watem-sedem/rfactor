import pytest
import numpy as np
from .conftest import erosivitydata, fmap_rainfall
from rfactor.rfactor import compute_rfactor


@pytest.mark.matlabbased
def test_rfactor():

    compute_rfactor(fmap_rainfall, "matlab")


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

    df_R = erosivitydata.load_R(["KMI_6447", "KMI_FS3"], timeseries)

    np.testing.assert_allclose(np.mean(df_R["value"]), rfactor, atol=1e-2)
