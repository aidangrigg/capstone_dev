# Datastream

NOTE: This software is built specifically for Linux. If using Windows, try the "Unicorn LSL" software that can be used through the [Unicorn Suite](https://www.gtec.at/product/unicorn-suite/).

(TODO: proper description)

## Building

### Dependencies

#### Nix

(TODO: write proper nix build script)
Run `nix develop` in this directory

#### Other distros

(TODO: list required deps)

### Instructions

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
