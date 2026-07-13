# Brainground experiment runner

The following software is a helper script that can be used to assist in performing a neurofeedback training experiment using Brainground, and is configured using a JSON text file. The software has 3 main purposes:
- Giving the participant instructions using text to speech.
- When giving instructions to the participant, sending command instructions to the Unity project using a websocket server (to adjust the active feedback within the scenario, or to start/stop computing a baseline)
- Creating an LSL marker stream with timestamps of the given instructions/training blocks.

### Nix (recommended if using Linux)

0. Install the [nix](https://nixos.org/) package manager.
1. Run `nix develop`.

### Windows

1. Install Python 3.12 (or any other compatible version of python)
2. (Optionally) create and activate a python virtual environment `python -m venv .venv && ./.venv/Scripts/activate` (rather than installing packages globally)
3. Install required dependencies: `pip install ...`

## Running

Run the project using `python main.py -i cfg/example.json`. The software can be configured by changing parameters within the JSON file (`cfg/example.json` contains an example experiment, copy and edit this).
