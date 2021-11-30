## Problem

_Check Erlang's formula. Propose a method to calculate what must be the maximum
traffic offered to a system in which we have N serving devices, and it is
required that the probability of loss does not exceed a given value._

## Solution

A naive method of checking Erlang's formula for a given number of serving
devices and a given packet blocking probability involves calculating the maximum
traffic offered to the server (using a formula and a numerical method) and
running a simulation in which the previously calculated traffic is a parameter
and checking whether the simulation-calculated probability is close to the given
one.

The simulator allows modifying the simulation parameters in its configuration
file.

## TODO

* Making simulation independent of formula-calculated max traffic value.

---

## Requirements

`python >= 3.6`
`pip`
`numpy`
`matplotlib`

## Setup

### Install system requirements

* _Linux (Debian / Ubuntu):_

```commandline
sudo apt update
sudo apt install python3 python3-pip
```

* _Windows_

https://www.python.org/downloads/

This will install Python as well as `pip`.

### Install Python requirements

1. Make sure Python and `pip` are installed and added to `PATH` system variable.
2. Open terminal or command prompt and in the project directory type:

```commandline
pip3 install -r requirements.txt
```

---

### Usage

First, change the parameters in the [config/config.json](config/config.json)
file.

You can also create your own json file with all needed parameters, for example:

```json
{
  "mi_values": [0.2, 0.4, 0.6, 0.8, 1],
  "server_counts": [5, 7, 9, 11, 13],
  "blocking_probabilities": [0.1, 0.2, 0.3, 0.4, 0.5],
  "simulation_repetitions": 10,
  "time_limit": 10,
  "events_limit": 10000,
  "seed": 123,
  "show_plots": true
}
```

* `mi_values` - values for mean service rate for system parameter
* `server_counts` - values for server count parameter
* `blocking_probabilities` - values for blocking probability parameter
* `simulation_repetitions` - count of simulation repetitions
* `time_limit` - time limit for each simulation
* `events_limit` - events limit for each simulation
* `seed` - seed to use for rng initialization
* `show_plots` - generate plots for significant data

To run the simulator, use `main` script from `simulation` module:

```commandline
python3 -m simulator.main
```
