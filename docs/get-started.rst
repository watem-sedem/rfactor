.. _getstarted:

Get started
============

The R-factor scripts can be used to:

1. Compute the erosivity :math:`EI_{30}` values for a number of stations and
   years.
2. Use the computed :math:`EI_{30}` values to compute an R-value.


From 10' rain data to EI for a single station/year
--------------------------------------------------

The input of the erosivity algorithm is a rainfall time series with a 10'
resolution as a Pandas DataFrame, e.g.

+-----+---------------------+-----------+-----------+
| idx | datetime            | rain_mm   | station   |
+=====+=====================+===========+===========+
|  0  | 2018-01-01 02:10:00 |      0.27 |      P01  |
+-----+---------------------+-----------+-----------+
|  1  | 2018-01-01 02:20:00 |      0.02 |      P01  |
+-----+---------------------+-----------+-----------+
|  2  | 2018-01-01 03:10:00 |      0.48 |      P01  |
+-----+---------------------+-----------+-----------+
| ... | ...                 | ...       |      ...  |
+-----+---------------------+-----------+-----------+

The data can be derived from any source and contain more columns (e.g. the
measurement station identifier), but the ``datetime``, ``rain_mm`` and
``station`` are required to apply the erosivity algorithm. The data can
contain both data of a single year/station  as multiple years/stations (see
further to calculate multiple stations together. Make sure that the
``station`` column is present also for the single station case.

Erosivity (EI30-values) for a single station/year combination can be computed
(make sure to activating the conda environment, ``conda activate rfactor``).
The :func:`rfactor.compute_erosivity` function applies the algorithm to a
DataFrame containing data for a single station/year, e.g. for the data in
DataFrame ``df_rain``.

.. code-block:: python

    from rfactor import compute_erosivity, maximum_intensity
    erosivity = compute_erosivity(df_rain, maximum_intensity)

.. note::

    The :func:`rfactor.rfactor.maximum_intensity` is the default method to
    derive the maximum 30min interval rain intensity of an event, but the user
    can provide a custom function as well or the original Matlab
    implementation version
    :func:`rfactor.rfactor.maximum_intensity_matlab_clone` can be used to
    compare with the corrected Matlab implementation.

The output is a DataFrame with the intermediate results and the cumulative
erosivity of each of the defined events:

+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|   event_idx | datetime            |   ...  |   all_event_rain_cum |   erosivity_cum | station | year |
+=============+=====================+========+======================+=================+=========+======+
|           2 | 2018-01-01 14:30:00 |   ...  |                 1.08 |         5.01878 |   P01   | 2018 |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|           3 | 2018-01-02 16:30:00 |   ...  |                12.37 |         8.00847 |   P01   | 2018 |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|           4 | 2018-01-04 09:10:00 |   ...  |                20.13 |         8.33275 |   P01   | 2018 |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|           5 | 2018-01-05 02:20:00 |   ...  |                22.47 |         8.61462 |   P01   | 2018 |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|         ... | ...                 |   ...  |                ...   |        ...      |   ...   | ...  |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+


As the "erosivity_cum" column contains the cumulative erosity over the events,
the last value is the R-factor of the year/station:

.. code-block:: python

    erosivity["erosivity_cum"].iloc[-1]

Other relevant derived statistics, such as the monthly and biweekly based
R-factor can be calculated using the existing Pandas functionalities:

.. code-block:: python

    erosivity.resample("M", on="datetime")["erosivity"].sum()  # Monthly value
    erosivity.resample("SM", on="datetime")["erosivity"].sum()  # Biweekly value


Calculating multiple station/year combinations
----------------------------------------------

When data are available from multiple stations over multiple years in a single
DataFrame, the :func:`rfactor.compute_erosivity` function applies the
erosivity algorithm on each year/station combination in the input rain
DataFrame. To do so, an additional column with the ``station`` name is
required:

+-----+---------------------+-----------+---------+
|     | datetime            | rain_mm   | station |
+=====+=====================+===========+=========+
|  0  | 2018-01-01 02:10:00 |      0.27 |   P01   |
+-----+---------------------+-----------+---------+
|  1  | 2018-01-01 02:20:00 |      0.02 |   P01   |
+-----+---------------------+-----------+---------+
|  2  | 2018-01-01 03:10:00 |      0.48 |   P01   |
+-----+---------------------+-----------+---------+
| ... |       ...           |     ...   |   ...   |
+-----+---------------------+-----------+---------+
|  10 | 2019-01-01 01:10:00 |      0.52 |   P01   |
+-----+---------------------+-----------+---------+
|  11 | 2019-01-01 01:20:00 |      0.20 |   P01   |
+-----+---------------------+-----------+---------+
| ... |       ...           |     ...   |   ...   |
+-----+---------------------+-----------+---------+
| 123 | 2018-01-01 00:10:00 |      0.02 |   P02   |
+-----+---------------------+-----------+---------+
| 124 | 2018-01-01 00:20:00 |      0.32 |   P02   |
+-----+---------------------+-----------+---------+
| ... |       ...           |     ...   |   ...   |
+-----+---------------------+-----------+---------+


.. code-block:: python

    from rfactor import compute_erosivity, maximum_intensity
    erosivity = compute_erosivity(df_rain)

The output is very similar to the previous section, but the data contains now
multiple years and/or stations:

+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|   event_idx | datetime            |   ...  |   all_event_rain_cum |   erosivity_cum | station | year |
+=============+=====================+========+======================+=================+=========+======+
|           2 | 2018-01-01 14:30:00 |   ...  |                 1.08 |         5.01878 |   P01   | 2018 |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|           3 | 2018-01-02 16:30:00 |   ...  |                12.37 |         8.00847 |   P01   | 2018 |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|         ... | ...                 |   ...  |                ...   |        ...      |   ...   | ...  |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|           1 | 2019-01-04 09:10:00 |   ...  |                20.13 |         8.33275 |   P01   | 2019 |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|           2 | 2019-01-05 02:20:00 |   ...  |                22.47 |         8.61462 |   P01   | 2019 |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+
|         ... | ...                 |   ...  |                ...   |        ...      |   ...   | ...  |
+-------------+---------------------+--------+----------------------+-----------------+---------+------+

To derive the R-factor for each year/station in the data set, one can use the
existing Pandas functionalities:

.. code-block:: python

    erosivity.groupby(["station", "year"])["erosivity_cum"].last().reset_index()


File handling
-------------

This package provides a number of processing functions in the
:mod:`rfactor.process` module to enable compatibility of the input formar with
the required data format defined in this package (see previous section).
Currently, next processing functions are implemented:

- :func:`rfactor.process.load_rain_file_matlab_legacy`: This is the processing
  function used to process the ``Matlab KU-Leuven`` file legacy.
- :func:`rfactor.process.load_rain_file_csv_vmm`: This is the processing
  function used to process the ``VMM CSV`` file legacy.

Both file-formats can be loaded with the defined processing function, i.e.

.. code-block:: python

    from pathlib import Path
    from rfactor.process import load_rain_file_matlab_legacy,
                                    load_rain_file_csv_vmm
    # Load a Matlab-file
    fname = Path("/PATH/TO/YOUR/RAINFALL/DATA/FOLDER/P01_001_2018.txt")
    from_matlab = load_rain_file_matlab_legacy(fname)

    # Load a VMM CSV
    fname = Path("/PATH/TO/YOUR/RAINFALL/DATA/FOLDER/P01_001.CSV")
    from_vmm = load_rain_file_csv_vmm(fname)

Or a folder containing multiple files can be loaded:

.. code-block:: python

    from pathlib import Path
    from rfactor.process import load_rain_file_matlab_legacy,
                                    load_rain_file_csv_vmm, load_rain_folder

    # Load an entire set of Matlab-legacy files
    folder = Path("/PATH/FOLDER/CONTAINING/MATLABFORMAT/FILES")
    from_matlab = load_rain_folder(folder, load_rain_file_matlab_legacy)

    # Load an entire set of VMM CSV-legacy files
    folder = Path("/PATH/FOLDER/CONTAINING/VMMCSVFORMAT/FILES")
    from_matlab = load_rain_file_csv_vmm(folder, load_rain_file_matlab_legacy)

.. note::

    Do not forget to use a :py:class:`pathlib.Path` defined file name or
    folder name.

In the next subsections, the specifics for every file-legacy format are
explained.

Matlab KU-Leuven legacy
~~~~~~~~~~~~~~~~~~~~~~~

The input files are defined by text files (extension: ``.txt``) that
hold non-zero rainfall timeseries. The data are split per station and
per year with a specific datafile tag (format: **SOURCE\_STATION\_YEAR.txt**):

-  KMI\_6414\_2004.txt
-  KMI\_6414\_2005.txt
-  ...
-  KMI\_6434\_2003.txt
-  KMI\_6434\_2004.txt
-  ...

The content of each of this file is a **non-zero** rainfall timeseries
(no header, space delimited):

::

     9390 1.00
     9470 0.20
     9480 0.50
     10770 0.10
     ... ...

with the first column being the timestamp from the start of the year
(minutes) , and second the rainfall depth (in mm).

VMM CSV legacy
~~~~~~~~~~~~~~

Starting from 2018, a new input format is defined and used for the analysis of
flanders. The reason for this is two-folded:

1. The new format is compatible with the VMM output from VMM's WISKI-system.
2. The format allows to compute timeseries coverage (see ``diagnostics`` in
   :func:`rfactor.process.load_rain_file`). This was not possible with the
   Matlab-format as required to be a **non-zero**-timeseries.

The input files are defined by text files (extension: ``.CSV``) that hold
rainfall timeseries. The data are split per station with a specific datafile
tag (format: **IDENTIFIER_STATION.CSV**):

-  KMI\_6414.CSV
-  KMI\_6434.CSV
-  ...
-  P07\_006.CSV
-  ...

The content of each of this file is a rainfall timeseries (comma delimited):

::

    Date/Time,Value [millimeter]
    01/01/2019 00:00,"0"
    01/01/2019 00:05,"0.03"
    01/01/2019 00:10,"0.04"
    01/01/2019 00:15,"0"
    01/01/2019 00:20,"0"
    01/01/2019 00:25,"---"
    01/01/2019 00:30,"0"

     ... ...

Output erosivity
~~~~~~~~~~~~~~~~

To export the resulting DataFrame with erosivity values into the legacy output format:

.. code-block:: python

    from pathlib import Path
    from rfactor.process import load_rain_folder, load_rain_file
    # Works both on a single station/year as multiple station/year combinations
    write_erosivity_data(erosivity, Path("/PATH/TO/YOUR/EROSIVITY/OUTPUT"))



Analyse R-values
----------------

The R-value is determined by the number of years and stations the users wishes
to consider to compute the R value. By using Pandas DataFrame to store the
erosivity, all funtionalities for slicing/filtering/plotting/... are available
directly.

For example, consider one wants to compute the R-value for 2017 and 2018, for
Ukkel (stations: KMI\_6447 and KMI\_FS3):

.. code-block:: python

    erosivity_selected = erosivity[(erosivity["year"].isin([2017, 2018])) &
                       (erosivity["station"].isin(['KMI\_6447', 'KMI\_FS3']))]
