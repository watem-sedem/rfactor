
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14264876.svg)](https://doi.org/10.5281/zenodo.14264876)



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

The aim of this package is to provide an interface for computing the
erosivity and R-factor (in batch). The interface allows to apply commonly used
formulation of the R-factor (i.e. Brown and Foster, 1987 or McGregor et
al, 1995) next to custom user-defined functions. In addition, it allows to
apply custom user-defined input data processing functions, next to the
standard input format.

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
> results compared to version \>0.1.0, as explained in the [package documentation](https://watem-sedem.github.io/rfactor/).

Get started
-----------
This package makes use of `Python` (and a limited number of dependencies
such as Pandas and Numpy). To install:

```
pip install rfactor
```

Make sure to check out the installation instructions and follow the example in
the _Get started section_ of the [package documentation](https://watem-sedem.github.io/rfactor/).

Rainfall and erosivity data
---------------------------

Any 10 minute ezqolurion input rainfall should work, but input rainfall data for the initial project
were provided by the Flemish Environment Agency (VMM) and the Royal Meteorological Institute (RMI).
The data from the Flemish Environment Agency (VMM) are available via
[waterinfo](https://www.waterinfo.be). The input rainfall data from the
Royal Meteorological Institute (RMI) are not shared in this project.
Please contact the RMI if you would like to obtain the a copy of the RMI
rainfall input data.

The erosivity data calculated with the rainfall input data are provided
by the partners of this project, and are used as test data for analysing
the R-factor for Flanders.

Code
----
The open-source code can be found on [GitHub](https://github.com/watem-sedem/rfactor).

Documentation
-------------

The documentation can be found on the [R-factor documentation
page](https://watem-sedem.github.io/rfactor/index.html).

License
-------

This project is licensed under the GNU Lesser Public License v3.0, see
[LICENSE](./LICENSE) for more information.

Contact
-------
For technical questions, we refer to the documentation. If you have a
technical issue with running the model, or if you encounter a bug, please
use the issue-tracker on github:
[https://github.com/watem-sedem/rfactor/issues](https://github.com/watem-sedem/rfactor/issues)

If you have questions about the history or concept of the model that are
not answered in the documentation please contact KU Leuven via
https://ees.kuleuven.be/en/geography/modelling/erosion/watem-sedem/contact.

Do you have questions about the application of R-factor in Flanders? Please
contact 'Departement Omgeving' of the Government of Flanders on
cn-ws@omgeving.vlaanderen.be

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

References
----------
Brown, L.C., Foster, G.R., 1987. Storm erosivity using idealized intensity
distributions. Transactions of the ASAE 30, 0379–0386.
McGregor, K.C., Bingner, R.L., Bowie, A.J. and Foster, G.R., 1995. Erosivity
index values for northern Mississippi. Transactions of the ASAE, 38(4),
pp.1039-1047.
