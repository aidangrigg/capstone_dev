# Unicorn LSL

NOTE: This software is built specifically for Linux. If using Windows, try the "Unicorn LSL" software that can be used through the [Unicorn Suite](https://www.gtec.at/product/unicorn-suite/).

## Setup

Using [nix](https://nixos.org/) is the supported method for installing dependencies. The required dependencies can be installed within a dev environment using `nix develop`.

The required dependencies may also be installed manually. Look into `flake.nix` in order to find the required packages needed to run the project.

### Building

`cd` into the `datastream/` directory and run the following commands.

```bash
mkdir build
cd build
cmake ..
make
```

After running these commands (and assuming all the required dependencies are installed), an `unicorn_datastream` executable should be compiled. To check that everything is working correctly, try running `./unicorn-datastream --help`.

## Running

```
Usage: unicorn_datastream [options]
Options:
  --help                   Display this information.
  -i, --input <FILE>       Read data from an input file rather than live
                           recording.
  -o, --output <FILE>      If live recording, will save this data to a
                           a binary file. This binary file can be read using
                           `--input`.
  -d, --device <DEVICE_ID> Selects the accompanying unicorn headset.
  -t, --test_signal        If set, will output a square waveform test signal
                           rather than a live measurement.
```

Example command: `./build/unicorn_datastream -i ./example_data/2025-11-18_1.out`
