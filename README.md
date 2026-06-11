# Brainground

(TODO: write a proper description)

## Structure

This project is broken up into several programs, instructions for each can be found in the `README.md` in their individual directory. The following is brief description of what each program does:
1. `unicorn-lsl/`: Grabs data from the g.tec Unicorn Hybrid Black over bluetooth and streams it using the LSL. Is also able to record a stream to a file, and replay the stream as if it was in real-time to make it easier to test other components.
2. `exg-lsl/`: Grabs data from a custom 4 channel EEG device and outputs an LSL stream. Connection to the EEG device is done over Bluetooth Low Energy and controlled through a simple GUI.
3. `processing/`: Pulls in EEG data from an LSL stream, filters and processes it, and then outputs a neurofeedback score to a web socket server. Parameters related to the neurofeedback metric are configurable through the GUI. The GUI also displays various graphs to visually inspect the live data.
4. `lsl_subscriber/`: Contains random helper scripts to help debug and visualise LSL streams.
4. `analysis/`: Contains all the code used to analyse the data collected for the project. Also, contains the script that controlled the TTS during the experiment.

