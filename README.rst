R-factor
========

The :math:`R`-factor is a measure used in erosion and (overland) sediment
modelling to quantify the effect of rainfall on soil erosion. It is typically
defined in the context of the RUSLE equation, in which gross erosion for an
agricultural parcel is estimated (see, for example,
`here <https://docs.fluves.net/cnws-pascal//>`_).

Specifically, the :math:`R`-factor is a measure for the total erosivity of a
number of rainfall events within a defined timeframe (year, month, number of
days). The factor is computed by calculating the erosivity for every rainfall
event in a timeseries, and taking the sum of the erosivity of all events in
one year. These yearly values can be used to compute an average value, the
R-factor, presenting the rainfall erosivity for a given period. An in-depth
explanation of the formula's is given :ref:`here <rfactor>`.

Get started
-----------
This package makes use of ``Python`` (and a limited number of
dependencies such as Pandas and Numpy) and ``Matlab`` or ``Octave``. Python is
used to implemented the functionalities in this package, whereas Matlab or
Octave is used to run the core code. The installation
(see :ref:`here <installation>`) is managed by making use of
`Miniconda <https://docs.conda.io/en/latest/miniconda.html>`__. Make sure to
check out the installation instructions, and follow the example in the
:ref:`Get started <getstarted>` page.

.. note::

    Octave is used in this package as a free alternative if you are unable to
    acquire a license for Matlab. Note that running the rfactor core scripts
    is slower with Octave than with Matlab.

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

License
-------
This project is licensed under the GNU General Public License v3.0, see
:ref:`here <license>` for more information.

Contact
-------
We encourage user to submit question, suggestions and bug reports via the
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