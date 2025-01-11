# utils-tesis

![GitHub Actions](https://github.com/alvarohc777/Tesis/actions/workflows/release_to_pypi.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/utils-tesis.svg)](https://badge.fury.io/py/utils-tesis)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

`utils-tesis` is a Python package that provides a collection of auxiliary functions for various tasks commonly encountered in thesis and research projects. These functions are designed to streamline and simplify common operations, leveraging the power of the NumPy Stack, including NumPy, SciPy, Matplotlib, and Pandas.

## Features

- **NumPy Stack Integration**: Utilize the capabilities of NumPy, SciPy, Matplotlib, and Pandas seamlessly for efficient data manipulation, analysis, and visualization.

- **Convenience Functions**: A set of convenience functions to perform common tasks encountered in thesis and research projects, including:
  - **Loading Signals as Pandas DataFrames**: Easily load and handle signals as Pandas DataFrames for efficient data manipulation.
  - **Fault Detection using Harmonic Distortion**: Detect and analyze faults in signals by examining harmonic distortion.
  - **Signal Windowing**: Apply windowing techniques to signals for better analysis and feature extraction.
  - **Plotting**: Streamlined functions for visualizing signals and analysis results using Matplotlib.
  - **Fourier Transforms**: Perform Fourier transforms on signals to analyze frequency components.
  - **Superimposed Components Analysis**: Identify and analyze superimposed components in signals.

- **Modular Design**: Well-organized modules make it easy to find and use specific functionalities without unnecessary complexity.

## Installation

Install the package using pip:

```bash
pip install utils-tesis
```
## Usage Example

``` python
# test.py

# Import necessary modules from utils_tesis
import utils_tesis.integration as itg
from utils_tesis.signalload import CSV_pandas

# Create a dictionary to store signal information
signal_info = {}
signal_info["window_length"] = 64
signal_info["step"] = 4

# Instantiate a CSV_pandas object to load signals
signals = CSV_pandas()

# Retrieve the list of available signals
signals.relay_list()

# Assign signals to the signal_info dictionary
signal_info["signals"] = signals

# Specify the signal name for analysis
signal_info["signal_name"] = "I: X0023A-R1A"

# Perform integration using img_trip function from the itg module
t, trip = itg.img_trip(signal_info)

# Visualize the results using Matplotlib
import matplotlib.pyplot as plt

# Plot the integrated signal using stem plot
plt.stem(t, trip)
plt.title("Integrated Signal: " + signal_info["signal_name"])
plt.xlabel("Time")
plt.ylabel("Integrated Value")
plt.show()
```

