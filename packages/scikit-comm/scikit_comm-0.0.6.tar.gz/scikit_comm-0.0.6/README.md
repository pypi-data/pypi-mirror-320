# scikit-comm: simulation toolbox for communication systems

This python package contains a collection of DSP routines and algorithms to perform numerical simulations on simple communication systems. Its functionality is divided into transmitter, channel, and receiver subsystems and - at its current state - contains very limited functionalities.

This project was initially started by [Lutz Molle](https://www.htw-berlin.de/hochschule/personen/person/?eid=12017) and [Markus Nölle](https://www.htw-berlin.de/hochschule/personen/person/?eid=9586) at the [University of Applied Sciences (HTW), Berlin](https://www.htw-berlin.de/).

# Installation

## Installation via pip

The current stable version of this package can be installed via pip using the following command

```python
pip install scikit-comm
```

## Installation from GitLab repository

Further, the current development status can be installed by cloing the repository and installing locally via pip using the following commands

```python
git clone https://gitlab.com/htw-ikt-noelle/scikit-comm.git
cd scikit-comm
```

and then either regular install with 

```python
python -m pip install ./
```

or install in "editable" mode with

```python
python -m pip install -e ./
```

# Sources of information

The documentation can be found at [Readthedocs](https://scikit-comm.readthedocs.io/en/latest/), while the code is hosted at [GitLab](https://gitlab.com/htw-ikt-noelle/scikit-comm).

# General overview and first steps

## The 'signal' object
The 'signal' object can be seen as the 'heart of the toolbox'. It contains all information to describe a modulated data signal. The object can consist of multiple 'dimensions', while each dimension represents in general a two dimensional (or complex) data signal. The structure looks as follows:

```python
def Signal:    
  self.n_dims
  self.samples
  self.center_frequency
  self.sample_rate
  self.bits
  self.symbols
  self.symbol_rate
  self.modulation_info
  self.constellation
```

Many modules and methods take this signal object as input or output variables. Others in contrast take only a subset of the signal attributes (e.g. the sampled signal (sig.samples)) as input or output.

## Package structure

Besides the signal object, there are multiple other modules avaialable, which provide different functionalities for the simulation of a communication system:

| Module                | Description | 
| :---                  | :---        |
|skcomm.channel                |basic function to emulate a transmission channel|
|skcomm.filters | method to filter a discrete signal |
|skcomm.instrument_control | methods to communicate with laboratory equipment | 
|skcomm.pre_distortion |methods to perform identification and pre-distortion of linear systems| 
|skcomm.rx| receiver (dsp) subfunctions| 
|skcomm.tx| transmitter (dsp) subfuntions | 
|skcomm.utils| utility functions (mostly used by other methods) | 
|skcomm.visualizers| methods to visualize the data signal | 