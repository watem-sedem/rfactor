

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
to run the R-factor scripts. Make sure you have Python installed with the 
latest version of [Numpy](https://numpy.org/) and [Pandas](https://pandas.pydata.org/). 
It is advised to install Python via [Anaconda](https://www.anaconda.com/products/individual) 
or [Miniconda](https://docs.conda.io/en/latest/miniconda.html). 
If you make use of Miniconda, make sure to install numpy (in terminal 
``conda install -c anaconda numpy``), pandas (``conda install pandas``) and 
jupyter lab (``conda install -c conda-forge jupyterlab``).  

Finally, to make sure the Python rfactor scripts can be used in the analysis 
notebooks (*docs/notebooks/analysis.ipybn*), run following command in the main 
folder of this package:

    python setup.py install
    
## Get started

### Prepare input files

Example

### Run scripts (Matlab)

The matlab R-factor script of KULeuven can be run by navigating to the src (for example, *C:\Users\\$USERNAME\GitHub\rfactor\rfactor\src\rfactor*) directory and running the script:

    matlab -nodisplay -r "main('C:\Users\$USERNAME\GitHub\rfactor\rfactor\docs\data\example_inputdata')"

The results of the calculations will be located in the results folder (*C:\Users\\$USERNAME\GitHub\rfactor\src\rfactor\results*)

### Run analysis (Jupyter notebooks and Python)

Explain steps jupyter notebook

## Powered by

- KU Leuven
- VMM
- VPO

## License

## Authors

Gert Verstraeten (KULeuven)  
Johan Van de Wauw (Fluves)  
Sacha Gobeyn (Fluves)  
  