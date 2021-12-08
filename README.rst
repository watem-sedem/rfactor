.. image:: https://zenodo.org/badge/364504726.svg
   :target: https://zenodo.org/badge/latestdoi/364504726

R-factor
========

The :math:`R`-factor is a measure used in erosion and (overland) sediment
modelling to quantify the effect of rainfall on soil erosion. It is typically
defined in the context of the RUSLE equation, in which gross erosion for an
agricultural parcel is estimated.

Specifically, the :math:`R`-factor is a measure for the total erosivity of a
number of rainfall events within a defined timeframe (year, month, number of
days). The factor is computed by calculating the erosivity for every rainfall
event in a timeseries, and taking the sum of the erosivity of all events in
one year. These yearly values can be used to compute an average value, the
R-factor, presenting the rainfall erosivity for a given period. An in-depth
explanation of the formula's is given :ref:`here <rfactor>`.


This code is developed as a function of an analysis of rainfall
erosivity in Flanders. The results found in the example notebooks
are also found in `this report <https://www.friscris.be/nl/publications/herziening-van-de-neerslagerosiviteitsfactor-r-voor-de-vlaamse-erosiemodellering(9d4e2953-6c93-48d0-a1c2-d66d03c749aa).html>`_).

Get started
-----------
This package makes use of ``Python`` (and a limited number of
dependencies such as Pandas and Numpy). The installation
(see :ref:`here <installation>`) is managed by making use of
`Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_. Make sure
tocheck out the installation instructions, and follow the example in the
:ref:`Get started <getstarted>` page.

Data & application to Flanders
------------------------------
Input rainfall data are provided by the Flemish Environment Agency (VMM),
which are also available via `waterinfo <https://www.waterinfo.be>`_. The
input rainfall data from the Royal Meteorological Institute
(RMI) are not shared in this project. Please contact the RMI if you would like
to obtain the a copy of the RMI rainfall input data.

The erosivity data calculated with the rainfall input data are provided by the
partners of this project, and are used as test data for analysing the R-factor
for Flanders.

Documentation
-------------
The documentation can be found on the
`R-factor documentation page <https://cn-ws.github.io/rfactor/index.html>`_.

License
-------
This project is licensed under GNU Lesser Public License v3.0, see
:ref:`here <license>` for more information.

Contact
-------
We encourage users to submit questions, suggestions and bug reports via the
issues platform on GitHub. In case of other questions, one can mail
to cn-ws@omgeving.vlaanderen.be

Powered by
----------

.. image:: ../docs/_static/png/DepartementOmgeving_logo.png


.. image:: ../docs/_static/png/KULeuven_logo.png


.. image:: ../docs/_static/png/VMM_logo.png


.. image:: ../docs/_static/png/fluves_logo.png

Note
----
This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
