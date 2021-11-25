
.. _contribute:

How can you contribute?
=======================

The R-factor project is a project made possible by the Flemish Government
(Department Environment), the Flemish Environment Agency, K.U. Leuven and
Fluves. A special thank you to the Flemish Environment Agency for providing the
input data, and K.U. Leuven for providing and releasing their source code.

Thank you to all partners that decided to host this code and the data as open
source.

There are many ways to contribute to this project:

- Ask a question.
- If you believe in this project, share it via social media.
- Propose a new feature.
- Report a bug.
- Improve the documentation.
- Help develop this package.

Code of conduct
---------------
See the :ref:`code of conduct <code_conduct>`.

.. _dev-guidelines:

Development guidelines
----------------------


We use a number of development tools to support us in improving the code
quality. No magic bullet or free lunch, but just a set of tools as any
craftman has tools to support him/her doing a better job.

For development purposes using conda, make sure to first run
``pip install -e .[develop]`` environment to prepare the development
environment and install all development tools. (When using ``tox -e dev``
this is already done).

When starting on the development of the ``rfactor`` package, makes sure to
be familiar with the following tools. Do not hesitate to ask the maintainers
when having trouble using these tools.

Pre-commit hooks
^^^^^^^^^^^^^^^^

To ensure a more common code formatting and limit the git diff, make sure to
install the pre-commit hooks. The required dependencies are included in the
development requirements installed when running
``pip install -e .[develop]``.

.. warning::
   Install the ``pre-commit`` hooks before your first git commit to the
   package!

::

    pre-commit install

on the main level of the package (``rfactor`` folder, location where the file
``.pre-commit-config.yaml`` is located).

If you just want to run the hooks on your files to see the effect
(not during a git commit), you can use the command at any time:

::

    pre-commit run --all-files

Unit testing with pytest
^^^^^^^^^^^^^^^^^^^^^^^^

Run the test suite using the ``pytest`` package, from within the main package
folder (`rfactor`):

::

    pytest

Or using tox (i.e. in a separate environment)

::

    tox

You will receive information on the test status and the test coverage of the
unit tests.

Documentation with sphinx
^^^^^^^^^^^^^^^^^^^^^^^^^

Build the documentation locally with Sphinx:

::

    tox -e docs

which will create the docs in the ``docs/_build/html`` folder. The
``docs/_build`` directory itself is left out of version control (and we
rather keep it as such ;-)).

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


Drone CI
^^^^^^^^

Apart from these tools you can run locally, we use drone continuous
integration to run these checks also on our servers. See
https://cloud.drone.io/cn-ws/rfactor/ for the results.

Git lfs
^^^^^^^

Git lfs, or large file support, is used in this repository to store gis files
in the repository. To use this functionality you need to install git lfs. See
`gitlfs`_ for instructions and more information.

The .gitattributes-file in the root folder contains the file extensions which
are stored under lfs. For now, only files within the test folder are stored
under lfs.

.. _gitlfs: https://git-lfs.github.com/

Naming things
^^^^^^^^^^^^^
To provide structure in the naming of methods, functions, classes,... we
ask to conform the following guidelines.

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


Creating a new release
^^^^^^^^^^^^^^^^^^^^^^

For the releases, the setup uses `setuptools-scm <setuptoolsscm>`_.  Basically, by managing the git-tags, the release version is managed as well.

Furthermore, the deployment of the documentation and pypi package is managed using github actions,
the `deploy.yml <deployci>`_ file.

To make a new release:

- ``git checkout master``, ``git pull origin master``
- Update the ``CHANGELOG.rst`` with the changes for this new release
- ``git commit -m 'Update changelog for release  X.X.X' CHANGELOG.rst``
- ``git push origin master``
- Add git tags: ``git tag vX.X.X``
- Push the git tags: ``git push --tags``
- On the `release page <releasepage>`_ draft a new release using the latest git tag
- Copy past the changes from the changelog in the dialog and publish release
- Check if github actions runs the deployment of docs and pypi


.. _releasepage: https://github.com/cn-ws/rfactor/releases
.. _setuptoolsscm: https://www.python.org/dev/peps/pep-0008/#naming-conventions
.. _deployci: https://github.com/fluves/pywaterinfo/blob/master/.github/workflows/deploy.yml
