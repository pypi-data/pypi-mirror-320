# PINNs SIRD

This package provides a Python implementation of the SIRD model using Physics-Informed Neural Networks (PINNs).

This package is based on the paper "Euler iteration augmented physics-informed neural networks for time-varying parameter estimation of the epidemic compartmental model" by Xi'an Li et al. (2022)

The main function is run_sird(data_path), which could be used to train a pinns-compartment model based on Adams-Bashforth 3rd order method.

## Installation

You can install the package directly from PyPI:

```bash
pip install pinns_sird


## Accessing Demo Data

The package includes a demo dataset located in the `data` folder. To load the data:

```python
from pinns_sird import load_demo_data

demo_data = load_demo_data()
print(demo_data.head())
```
