.. _installation:

Installation
============

Install
-------

Make sure you have Python (via Miniconda) installed:
https://docs.conda.io/en/latest/miniconda.html. In addition, pick-up the
latest version of
`Matlab <https://nl.mathworks.com/products/matlab.html?requestedDomain=>`__
to run the R-factor scripts (make sure you can run Matlab under administrator
account).

The Python dependencies are handled in the conda environment.yml file, so
anybody can recreate the required environment using:

::

    conda env create -f environment.yml
    conda activate rfactor

We strongly recommend to make use of the seperate ``rfactor`` environment to
install the dependencies (see two lines above), so it does not interfere with
other Python installation on your machine. If you which to install
the dependencies in your base environment, check out the dependencies in the
``environment.yml``-file.

With your ``rfactor`` environment activated (``conda activate rfactor``),
install the rfactor package:

::

    pip install -e .

Or for development purposes of this package, run following code to
install developer dependencies (using pip):

::

    pip install -e .[develop]

.. note::

A Python version of the Matlab code is being developed, and is expected to
be released in the next version of this code.

Development
-----------

When developing this package, following tools are used:

syntax formatting with black
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To ensure a more common code formatting and limit the git diff, make
sure to use the black pre-commit hook:

-  install
   `black <https://black.readthedocs.io/en/stable/installation_and_usage.html>`__
   (should be ok as part of the develop installation, see earlier)
-  install `pre-commit <https://pre-commit.com/#install>`__ (should be
   ok as part of the develop installation, see earlier)

Install the pre-commit hook:

::

    pre-commit install

on the main level of the package (location where the file
``.pre-commit-config.yaml`` is located)

unit testing with pytest
~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite using the ``pytest`` package, from within the main
package folder):

::

    python setup.py test

documentation with sphinx
~~~~~~~~~~~~~~~~~~~~~~~~~

Build the documentation locally with sphinx:

::

    python setup.py build_sphinx

which will create the docs in the ``build`` folder. This directory is
left out of version control.