# exg-lsl

A helper script to connect to the NCBCI 4ch EEG headset using Bluetooth, and exposing the data over Lab Streaming Layer.

## Setup

### Nix (recommended if using Linux)

0. Install the [nix](https://nixos.org/) package manager.
1. Run `nix develop`.

### Windows

1. Install Python 3.12 (or any other compatible version of python)
2. (Optionally) create and activate a python virtual environment `python -m venv .venv && ./.venv/Scripts/activate` (rather than installing packages globally)
3. Install required dependencies: `pip install numpy scipy pylsl pyqtgraph pyside6`

## Running

Run the project using `python main.py`. A GUI should launch showing a simple interface that can be used to connect to the EEG headset.

