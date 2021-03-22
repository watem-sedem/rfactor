

# R-factor

## Aim

Scripts to compute and analyse the R-factor of the RUSLE-equation. The
R-factor is a measure for the total erosivity of a number of rainfall events
within a defined timeframe (year, month, number of days). The factor is
computed by calculating the yearly sum of -for every rainfall event- the sum
of the depth of rainfall (mm) and the kinetic energy, and taking the mean
over all years. For the formula's, we refer to the [CN-WS Pascal model documentation](https://docs.fluves.net/cnws-pascal/watem-sedem.html#rusle-factors)

## Install

Pick-up the latest version of [Matlab](https://nl.mathworks.com/products/matlab.html?requestedDomain=)
to run the R-factor scripts. For Python, setup/update the environment: the dependencies are handled in the conda environment.yml file, so anybody can recreate the required environment using:

    conda env create -f environment.yml
    conda activate rfactor

For development purposes of this package, also run following code to install developer dependencies (using pip):

	pip install -e .[develop]
	
## Get started

### Prepare input files

Example

### Run scripts (Matlab)

The matlab R-factor script of KULeuven can be run by navigating to the src (for example, ``C:\Users\\$USERNAME\GitHub\rfactor\rfactor\src\rfactor``) directory and running the script:

    matlab -nodesktop -r "main('C:\Users\$USERNAME\GitHub\rfactor\rfactor\docs\data\example_inputdata')"

The results of the calculations will be located in the results folder (``C:\Users\\$USERNAME\GitHub\rfactor\src\rfactor\results``)

Get the R-value for 2018 based on two station:

    df_R=data.load_R(["KMI_6447","KMI_FS3"], 2018)

- Define the folder where the seperate (station,year) non-zero rainfall input data are located.
- Define the folder where the matlab results are located (cfr. ``C:\Users\\$USERNAME\GitHub\rfactor\src\rfactor\results``).  
- Define a ``consider.csv file`` that looks like:

  | source        | datafile      | consider  |
  | ------------- |:-------------:| ---------:|
  | KMI	          | KMI_6414_2003 | 0         |
  | KMI	          | KMI_6414_2004 | 1         |
  | KMI	          | KMI_6414_2005 | 1         |
  | ...           | ...           | ...       |

  Make sure the ``datafile`` holds the same names as the rainfall data files used input for the matlab calculations. If a rainfall data file is present in the rainfall input data folder, but is not defined in the ``consider.csv``, the code will exit.

  (Note: the code will also exit if the number of files in the rainfall input data folder are different from the erosivity data folder).   


## Development

When developing this package, following tools are used:

### syntax formatting with black

To ensure a more common code formatting and limit the git diff, make sure to use the black pre-commit hook:

- install [black](https://black.readthedocs.io/en/stable/installation_and_usage.html) (should be ok as part of the develop installation, see earlier)
- install [pre-commit](https://pre-commit.com/#install) (should be ok as part of the develop installation, see earlier)

Install the pre-commit hook:

```
pre-commit install
```

on the main level of the package (location where the file .pre-commit-config.yaml is located)

### unit testing with pytest

Run the test suite using the `pytest` package, from within the main package folder):

```
python setup.py test
```

### documentation with sphinx

Build the documentation locally with sphinx:

```
python setup.py build_sphinx
```

which will create the docs in the `build` folder. This directory is left out of version control.

## Powered by

- KU Leuven
- VMM
- VPO

## License

## Authors

Gert Verstraeten (KULeuven)  
Johan Van de Wauw (Fluves)  
Stijn Van Hoey (Fluves)
Sacha Gobeyn (Fluves)  
