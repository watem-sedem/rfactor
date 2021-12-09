[![image](https://zenodo.org/badge/364504726.svg)](https://zenodo.org/badge/latestdoi/364504726)

R-factor
========

The R-factor is a measure used in erosion and (overland) sediment
modelling to quantify the effect of rainfall on soil erosion. It is
typically defined in the context of the RUSLE equation, in which gross
erosion for an agricultural parcel is estimated.

Specifically, the R-factor is a measure for the total erosivity of a
number of rainfall events within a defined timeframe (year, month,
number of days). The factor is computed by calculating the erosivity for
every rainfall event in a timeseries, and taking the sum of the
erosivity of all events in one year. These yearly values can be used to
compute an average value, the R-factor, presenting the rainfall
erosivity for a given period. An in-depth explanation of the formula's
is given here \<rfactor\>.

The implemented formula's in this code are developed in a context of
rainfall in Belgium (Verstraeten et al., 2006). Yet, the current Python
implementation allows for an easy integration of alternative functions
and relations. An in-depth analysis of the application of this code on
Flanders can be found in in [this
report](https://www.friscris.be/nl/publications/herziening-van-de-neerslagerosiviteitsfactor-r-voor-de-vlaamse-erosiemodellering(9d4e2953-6c93-48d0-a1c2-d66d03c749aa).html).

__Note__

>
> In the earlier versions (\<0.1.0) of the R-factor package, Matlab was
> used for the core computations. Since version 0.1.0, a faster Python
> implementation is provided. Using the version 0.0.x will provide other
> results compared to version \>0.1.0, as explained in the [package documentation](https://cn-ws.github.io/rfactor/).

Get started
-----------
This package makes use of `Python` (and a limited number of dependencies
such as Pandas and Numpy). Make sure to check out the installation instructions, and follow the example in
the _Get started section_ of the [package documentation](https://cn-ws.github.io/rfactor/).

Rainfall and erosivity data
---------------------------

Any 10 minute ezqolurion input rainfall should work, but input rainfall data for the initial project
were provided by the Flemish Environment Agency (VMM) and the Royal Meteorological Institute (RMI).
Teh data from the Flemish Environment Agency (VMM) are available via
[waterinfo](https://www.waterinfo.be). The input rainfall data from the
Royal Meteorological Institute (RMI) are not shared in this project.
Please contact the RMI if you would like to obtain the a copy of the RMI
rainfall input data.

The erosivity data calculated with the rainfall input data are provided
by the partners of this project, and are used as test data for analysing
the R-factor for Flanders.

Documentation
-------------

The documentation can be found on the [R-factor documentation
page](https://cn-ws.github.io/rfactor/index.html).

License
-------

This project is licensed under the GNU Lesser Public License v3.0, see
[LICENSE](./LICENSE) for more information.

Contact
-------

We encourage user to submit question, suggestions and bug reports via
the issues platform on GitHub. In case of other questions, one can mail
to <cn-ws@omgeving.vlaanderen.be>

Powered by
----------

![image](docs/_static/png/DepartementOmgeving_logo.png)

![image](docs/_static/png/KULeuven_logo.png)

![image](docs/_static/png/VMM_logo.png)

![image](docs/_static/png/fluves_logo.png)

Note
----

This project has been set up using PyScaffold 3.2.3. For details and
usage information on PyScaffold see <https://pyscaffold.org/>.
