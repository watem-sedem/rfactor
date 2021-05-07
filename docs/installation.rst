.. _installation:

Installation
============

Python is used to implemented the functionalities in this package, whereas
Matlab or Octave is used to run the core code. Do note the use of Octave is
free of charge, but slower than the Matlab solution.

Install
-------

Make sure you have Python, via
`Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_, is installed.
The Python dependencies are handled in the ``environment.yml`` file, so
anybody can recreate the required environment:

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

Core
----

The core code makes use Matlab files. You can choose to either use Matlab (1)
or Octave (2) to run the core code. Do note that the use of Matlab requires a
license (free trail/student edition available) whereas the use of Octave is
free. Yet, a big downside of the use of Octave is that it is much slower in
code execution.

Matlab
~~~~~~
Make sure to pick-up the
latest version of
`Matlab <https://nl.mathworks.com/products/matlab.html?requestedDomain=>`__

.. _octave:
Alternative: Octave
~~~~~~~~~~~~~~~~~~~
Pick up the latest version of Octave from the
`website <https://www.gnu.org/software/octave/index>`__. After installing
Octave, install ``oct2py`` via conda

::

    conda install -c conda-forge oct2py

And make sure to define the path to your the ``OCTAVE_EXECUTABLE`` in a
``.env``-file. The latter you can do by creating a ``.env``-file in your
current working directory, and defining the executable location,
e.g. (local installation):

::

    OCTAVE_EXECUTABLE=C://Users//YOURUSERNAME//AppData//Local//Programs//GNU Octave//Octave-6.2.0//mingw64//bin//octave-cli-6.2.0.exe

for a windows-based system. Make sure to check where Octave is installed on
your computer! The ```python-dotenv``-package (installed with the installation
of the rfactor package) will use the ``.env``-file to check your installation.

An alternative is to add the path reference under the name OCTAVE_EXECUTABLE
to your path (windows: add via
`environmental variables <https://www.computerhope.com/issues/ch000549.htm>`_, linux: via
`adjusting the .bashrc-file <https://linuxize.com/post/how-to-add-directory-to-path-in-linux/>`_)

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

Run the test suite using the ``pytest`` package (from within the main
package folder, in the ``rfactor`` environment!):

::

    pytest tests/

documentation with sphinx
~~~~~~~~~~~~~~~~~~~~~~~~~

Build the documentation locally with sphinx (from within the main
package folder, in the ``rfactor`` environment!):

::

    python setup.py build_sphinx

which will create the docs in the ``build`` folder. This directory is
left out of version control.