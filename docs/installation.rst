.. _installation:

Installation
============

Python is used in this package.

We strongly recommend to make use of the seperate ``rfactor`` Python
environment to install the dependencies (by using ``tox`` or ``conda``,
see :ref:`here <installfromsource>`), so it does not
interfere with other Python installation on your machine.

.. note::

    Matlab or Octave were previously used to run the core rfactor code.
    See :ref:`codelegacy` for more information on the conversion towards a
    Python environment.

.. _installfromsource:

Install from source
-------------------

To install from source, ``git clone`` the repository somewhere on your local
machine and install the code from source.

Make sure to setup a new environment  in either conda or venv (using tox):

Using conda
^^^^^^^^^^^

Make sure you have Python, via
`Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_, installed.
The Python dependencies are handled in the ``environment.yml`` file, so
anybody can recreate the required environment:

::

    conda env create -f environment.yml
    conda activate rfactor

If you which to install the dependencies in a conda environment or your choice,
check out the dependencies in the ``environment.yml``-file.

With your ``rfactor`` environment activated (``conda activate rfactor``),
install the rfactor package:

::

    pip install -e .

Or for development purposes of this package, run following code to install
developer dependencies as well (using pip):

::

    pip install -e .[develop]

Using venv
^^^^^^^^^^

Make sure to have `tox <https://tox.readthedocs.io/en/latest/>`_ available.
Run the ``dev`` tox command, which will create a ``venv`` with a development
install of the package and it will register the environment as a ipykernel
(for usage inside jupyter notebook):

::

    tox -e dev

Development
-----------

Want to contribute code or functionalities to the ``rfactor`` package? Great
and welcome on board! Check out the :ref:`dev-guidelines` to get you up and
running.
