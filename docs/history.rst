.. _history:

History
=======

The first version of the R-factor scripts was developed by
`KU Leuven <https://www.kuleuven.be/english/>`_ (Laboratory for Experimental
Geomorphology, Department of Geography-Geology) in 2001. During 2019-2021 the
scripts were evaluated and translated to Python in order to optimize
performance, code readability and user-friendliness. During this evaluation
phase a number of coding errors were identified and corrected. In the following
section a brief comparison is presented between the Matlab (version 0.0.1) and
Python (version 1.0.0) implementation.

For the comparison the code, both the Matlab code and the reimplementation in
Python are run with rainfall inputdata from Belgium (KMI and VMM,
see :ref:``databelgium`). In the figure below, a comparison is shown between
the matlab code available in version 0.0.1, on the one hand, and 1.0.0, on
the other. For this figure, the cumulative erosivity at the end of the year
were compared for all years of all stations individually. Differences are
explained by a special if-case defined in the Matlab version 0.0.1 in which
the maximum 30-minute intensity was mistakenly multiplied by two. In addition,
in the computation of the maximum 30-minute rainfall intensity, the indices
were defined incorrectly for the first record.

.. image:: _static/png/matlab_comp.png

In the next figure, the comparison is made between the corrected Matlab version
(1.0.0) and the Python reimplementation. Here the minor deviations are related
to decimal precision.

.. image:: _static/png/python_matlab_comp.png

From this, it has been chosen to make use of the Python implementation for
future developments and applications.