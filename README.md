

# R-factor

## Aim

Scripts to compute and analyse the R-factor of the RUSLE-equation. The R-factor is a measure for the total erosivity of a number of rainfall events within a defined timeframe (year, month, number of days). The factor is computed by calculating the yearly sum of -for every rainfall event- the sum of the depth of rainfall (mm) and the kinetic energy, and taking the mean over all years. For the formula's, we refer to the [CN-WS Pascal model documentation](https://docs.fluves.net/cnws-pascal/watem-sedem.html#rusle-factors)

## Dependancy

 - Numpy
 - Pandas
 - Matlab

## Tutorial

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
  