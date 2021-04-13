.. _getstarted:

Get started
============

The R-factor scripts can be used to:

1. Compute the :math:`EI_{30}` values for a number of stations and years.
2. Use the computed :math:`EI_{30}` values to compute an R-value.

The :math:`EI_{30}` values are computed by using a matlab script that requires
a folder as input. In this folder, non-zero rainfall timeseries are stored
in separate text files (extension: ``.txt``) files per station and year.
The processing of the EI30 is done with Python

.. note::
A Python script to compute the EI30 values is in the making to avoid the need
to install matlab.

Prepare input files
-------------------

The input files are defined by text files (extension: ``.txt``) that
hold non-zero rainfall timeseries. The data are split per station and
per year with a specific datafile tag:

-  KMI\_6414\_2004.txt
-  KMI\_6414\_2005.txt
-  ...
-  KMI\_6434\_2003.txt
-  KMI\_6434\_2004.txt
-  ...

The content of each of this file is a **non-zero** rainfall timeseries
(no header, space delimited, see for example **TO DO: LINK**):

::

     9390 1.00
     9470 0.20
     9480 0.50
     10770 0.10
     ... ...

with the first column being the timestamp from the start of the year
(minutes) , and second the rainfall depth (in mm). An overview of the
present datafiles for the analysis is saved in a ``files.csv`` file
(example in **TO DO:LINK**). This file can be used to remove specific
files from the analysis (column ``consider``):

+----------+-------------------+------------+
| source   | datafile          | consider   |
+==========+===================+============+
| KMI      | KMI\_6414\_2004   | 0          |
+----------+-------------------+------------+
| KMI      | KMI\_6414\_2005   | 1          |
+----------+-------------------+------------+
| KMI      | KMI\_6414\_2006   | 1          |
+----------+-------------------+------------+
| ...      | ...               | ...        |
+----------+-------------------+------------+

Compute erosivity: EI30
-----------------------

The erosivity (EI30-values) can be computed by navigating to the
**TO DO: LINK** folder (make sure to activating the rfactor environment,
``conda activate rfactor``). In Python, import:

::

    from rfactor.rfactor import compute_rfactor
    from pathlib import Path

And run code:

::

    rainfall_inputdata_folder = Path(r"../../tests/data/test_rainfalldata")
    results_folder = Path(r"results")
    compute_rfactor(rainfall_inputdata_folder,results_folder,"matlab")

The current implementation makes use of a Matlab engine, which requires
Matlab to be installed. Future versions of this package will use Python.
Results are written to the *results\_folder*-folder.

Analyse R-values
----------------

The R-value is determined by the number of years and stations the users
wishes to consider to compute the R value. For example, consider one
wants to compute the R-value for 2018, for Ukkel (stations: KMI\_6447
and KMI\_FS3). In order to do so, consider following steps (in the main
folder):

-  Activate the rfactor environment (``conda activate rfactor``), open
   Python and load the necessary packages:

   ::

       from pathlib import Path
       from rfactor.process import ErosivityData

-  Define the folder path of the rainfall input and erosivity output
   data:

   ::

       fmap_rainfall = Path(r"./tests/data/test_rainfalldata")
       fmap_erosivty = = Path(r"results") # Folder path where results are written to (see above).

-  Define the path for the ``files.csv``-file:

   ::

       txt_files = Path(r"./test/data/files.csv")

-  Create a erosivitydata object, build the data set with the
   *files.csv* file and load the data:

   ::

       erosivitydata = ErosivityData(fmap_rainfall, fmap_erosivity)
       df_files = erosivitydata.build_data_set(txt_files)
       erosivitydata.load_data(df_files)

-  Get the R-value for 2017 and 2018 based on two Ukkel station
   ("KMI\_6447","KMI\_FS3"):

   ::

       df_R=erosivitydata.load_R(["KMI_6447","KMI_FS3"], [2017,2018])

-  Get the EI30-values for 2018 based on two Ukkel station
   ("KMI\_6447","KMI\_FS3"):

   ::

       df_EI30=erosivitydata.load_EI30(["KMI_6447","KMI_FS3"], [2017,2018])

-  The dataframe ``df_R`` and ``df_EI30`` holds the R-values and
   EI30-values for each station and year (for which data are available).
   From this, basic numpy or pandas operators can be used to compute
   statistics.

.. note::

If no values are reported for EI30 in ``df_EI30`` for a
specific year for a station, this implies no calculations were done for
that year. In ``df_R`` a ``nan`` value will be reported when no
calculations were done for that specific year.