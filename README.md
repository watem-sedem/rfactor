

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
to run the R-factor scripts (make sure you can run Matlab under administrator account). For Python, setup/update the environment: the dependencies are handled in the conda environment.yml file, so anybody can recreate the required environment using:

    conda env create -f environment.yml
    conda activate rfactor

To install the package use:

    pip install -e .

Or for development purposes of this package, run following code to install developer dependencies (using pip):

    pip install -e .[develop]
	
## Get started

The R-factor scripts can be used to:

1. Compute the EI30 values for a number of stations and years.
2. Use the computed EI30 values to compute an R-value.

The EI30 values are computed by using a matlab script* that requires a folder 
as input. In this folder, non-zero rainfall timeseries are stored in separate 
text files (extension: `.txt`) files per station and year. The processing of 
the EI30 is done with Python

__Note__: (*) A Python script to compute the EI30 values is in the making to avoid 
the need to install matlab.

### Prepare input files

The input files are defined by text files (extension: `.txt`) that hold 
non-zero rainfall timeseries. The data are split per station and per year with 
a specific datafile tag:

 - KMI_6414_2004.txt
 - KMI_6414_2005.txt
 - ...
 - KMI_6434_2003.txt
 - KMI_6434_2004.txt
 - ...
 
The content of each of this file is a **non-zero** rainfall timeseries
(no header, space delimited, see *./tests/data/test_rainfalldata*):

     9390 1.00
     9470 0.20
     9480 0.50
     10770 0.10
     ... ...  

with the first column being the timestamp from the start of the year (minutes)
, and second the rainfall depth (in mm). An overview of the present datafiles 
for the analysis is saved in a  `files.csv` file 
(example in *./tests/data*). This file can be used to remove specific 
files from the analysis (column `consider`):


   | source       | datafile      | consider  |
  | ------------- |:-------------:| ---------:|
  | KMI	    | KMI_6414_2004 | 0         |
  | KMI	    | KMI_6414_2005 | 1         |
  | KMI	    | KMI_6414_2006 | 1         |
  | ...           | ...           | ...       |


### Compute erosivity: EI30

The erosvity (EI30-values) can be computed by navigating to the 
*./src/rfactor* folder (make sure to activating the rfactor environment, 
``conda activate rfactor``). In Python, import:

    from rfactor.rfactor import compute_rfactor
    from pathlib import Path
    
And run code:

    rainfall_inputdata_folder = Path(r"../../tests/data/test_rainfalldata")
    results_folder = Path(r"results")
    compute_rfactor(rainfall_inputdata_folder,results_folder,"matlab")
    
The current implemenation makes use of a Matlab engine, which requires Matlab
to be installed. Future versions of this package will use Python. Results are 
written to the *results_folder*-folder.

### Analyse R-values

The R-value is determined by the number of years and stations the users wishes
to consider to compute the R value. For example, consider one wants to 
compute the R-value for 2018, for Ukkel (stations: KMI_6447 and KMI_FS3). In 
order to do so, consider following steps (in the main folder):

 - Activate the rfactor environment (``conda activate rfactor``), open Python 
and load the necessary packages:
    
    
        from pathlib import Path
        from rfactor.process import ErosivityData

 - Define the folder path of the rainfall input and erosivity output data:


        fmap_rainfall = Path(r"./tests/data/test_rainfalldata")
        fmap_erosivty = = Path(r"results") # Folder path where results are written to (see above).
 
 - Define the path for the `files.csv`-file:
 
 
        txt_files = Path(r"./test/data/files.csv")
        
 - Create a erosivitydata object, build the data set with the *files.csv* 
file and load the data:  


        erosivitydata = ErosivityData(fmap_rainfall, fmap_erosivity)
        df_files = erosivitydata.build_data_set(txt_files)
        erosivitydata.load_data(df_files)


 - Get the R-value for 2017 and 2018 based on two Ukkel station ("KMI_6447","KMI_FS3"):

    
        df_R=erosivitydata.load_R(["KMI_6447","KMI_FS3"], [2017,2018])

 - Get the EI30-values for 2018 based on two Ukkel station ("KMI_6447","KMI_FS3"):


        df_EI30=erosivitydata.load_EI30(["KMI_6447","KMI_FS3"], [2017,2018])

 - The dataframe ``df_R`` and ``df_EI30`` holds the R-values and EI30-values for each station and
  year (for which data are available). From this, basic numpy or pandas operators 
  can be used to compute statistics. 

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


![alt text](docs/_static/png/DepartementOmgeving_logo.png "Title")

![alt text](docs/_static/png/KULeuven_logo.png "Title")

![alt text](docs/_static/png/VMM_logo.png "Title")

![alt text](docs/_static/png/fluves_logo.png "Title")


## License

## Authors

Niels De Vleeschouwer (Fluves)  
Sacha Gobeyn (Fluves)    
Johan Van de Wauw (Fluves)    
Stijn Van Hoey (Fluves)  
Gert Verstraeten (KULeuven)    
