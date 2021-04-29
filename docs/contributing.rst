
.. _dev-guidelines:

Contributing to rfactor
=======================
The R-factor project is a project made possible by the Flemish Government
(Department Environment), the Flemish Environment Agency, K.U. Leuven and
Fluves. A special thank you to the Flemish Environment Agency for providing the
input data, and K.U.Leuven for providing and releasing their source code.

Thank you to all partners that decided to host this code and the data as open
source.

How can you contribute?
-----------------------
There are many ways to contribute to this project:

- Ask a question.
- If you believe in this project, share it via social media.
- Propose a new feature.
- Report a bug.
- Improve the documentation.
- Help develop this package.

TO DO: shortly explain how-to.

Code of conduct
---------------
See the `code of conduct <CODE_OF_CONDUCT.rst>`

Development guidelines
=======================

Git lfs
-------

Git lfs, or large file support, is used in this repository to store gis files
in the repository. To use this functionality you need to install git lfs. See
`https://git-lfs.github.com/`_ for instructions and more information.

The .gitattributes-file in the root folder contains the file extensions which
are stored under lfs. For now, only files within the test folder are stored
under lfs.

Documentation
-------------
`Numpy docstring <https://numpydoc.readthedocs.io/en/latest/format.html>`_
formatting is used to define the format of the python docstrings. As Numpy
docstring does not provide default rules on describing a parameter or returned
variable that represents a ``Pandas.DataFrame`` or a ``dict``, we include
these as follows (equivalent for parameters versus returns section):

::

    Returns
    -------
    df_name: pandas.DataFrame
        The DataFrame ...whatever you need to say... and contains the
        following columns:

        - *colunm_name_1* (int): description 1
        - *colunm_name_2* (float): description 2
        - *colunm_name_3* (datetime): description 3

    other_returned_var : float
        Description of a none df variable

Similar for a dictionary:

::

    Returns
    -------
    df_name: dict
        The dict ...whatever you need to say... and contains:

        - *key_1* (int): description 1
        - *key_2* (float): description 2
        - *key_3* (datetime): description 3

    other_returned_var : float
        Description of a none df variable

.. note::

    1. The empty lines are important for sphinx to convert this to a clean
       list.
    2. Detail alert: the format *variable: type* is used as constructor for
       every variable in the documentation (and not *variable : type*).

Naming things
-------------
To provide structure in the naming of methods, functions, classes,... we
propose to conform the following guidelines.

Class, function/methods names follow the standard naming conventions as
defined in the `PEP8`_ guidelines. Additionally, methods/functions start -
whenever possible - with an active verb on the action they perform
(``does_something()``), e.g. ``load_data()``

Variable names follow the `PEP8`_ guidelines, but provide additional context:

- raw textfiles (txt): ``txt_variable``
- dictionary: ``dict_variable``
- list: ``lst_variable``
- numpy array: ``arr_variable``
- pandas: ``df_variable``

.. _PEP8: https://www.python.org/dev/peps/pep-0008/#naming-conventions

Unit testing
------------
Pytest is used to test the functionalities. Two types of tests are defined:

 - `externaldepedent`: these tests are used to test the core Matlab-code with
   Octave (free alternative to Matlab). Check out the
   `installation-page<octave>` to install Octave.

 - Not `externaldepedent`: these tests are used to test the calculated
   R-values based on the computed EI30-values.

The tests can be called in the main folder of this
project, e.g. `~/GitHub/rfactor`::

    pytest pycnws/tests/ -m "externaldepedent"

or::

    pytest pycnws/tests/ -m "not externaldepedent"
