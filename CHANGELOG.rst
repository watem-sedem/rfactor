=========
Changelog
=========

Version 0.1.4
=============
 - Updates to documentation
 - Adding extra function for loading rainfall files ``load_rain_file_flanders``
 - Code refactoring: moving rain-related functionalities into separate module
 - Bug fix in ``maximum_intensity_interpolate``

Version 0.1.3
=============
 - New ``energy functions`` from McGregor (1995) and Brown & Foster (1987)  implemented.
 - Enable to feed custom energy functions to ``compute_erosivity``.
 - Name changes in available intensity functions.
 - Updates to documentation.
 - Add support for Python 3.10, 3.11 and 3.12

Version 0.1.2
=============
 - Small updates to documentation
 - Improved warning/errors
 - Added lightweight ```compute_diagnostics`` that computes diagnostics for input
   rainfall timeseries, see 1f0a7f5.
 - Fix pandas warnings:
   - Use pandas assign to create new columns.
   - Use pandas concat instead of pandas append.

Version 0.1.1
=============
 - Cleaned up data-files avaible in repo.
 - Included test for ``maximum_intensity_matlab_clone`` function and updated
   tests.

Version 0.1.0
=============
 - Matlab code is translated to Python.
 - Two major bugs in the Matlab code are fixed.
 - Added Matlab code legacy.

Version 0.0.2
=============
New version that avoids the need to define an independent file providing the
links to all input data files needed to analyse the R-factor.

Previous functionalities are preserved, and work in the same way:

 - Compute the erosivity and R-factor values based on rainfall input data.
 - Analyse the computed erosivity and R-factor values (for Flanders).

Version 0.0.1
=============
 - Implemented R-factor Python processing functions.
 - Implemented Python wrapper for KULeuven `compute R-factor` Matlab script.
 - Implemented use of Octave to run Matlab scripts.
 - Set-up package.
 - Added examples and test data.
 - Added test
