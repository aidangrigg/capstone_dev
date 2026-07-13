# Brainground

![An image showing a VR headset with EEG electrodes attached at F3 and F4 positions](./docs/images/vr-headset-photo.png "VR Headset") ![An image showing a unity scenario with a beach environment](./docs/images/vr-environment.png "VR beach environment")

Brainground is a closed-loop, multi-protocol neurofeedback training environment for virtual reality. It supports custom, user-configurable neurofeedback training protocols, and displays the feedback through the use of an immersive and relaxing beach scenario. The development of this project was in fullfillment of the requirements outlined by 41030 Engineering Capstone at the University of Technology Sydney.

## Project structure

This project is broken up into several programs, instructions for each can be found in the `README.md` in their individual directory. The following is brief description of what each program does:
1. `unicorn-lsl/`: Grabs data from the g.tec Unicorn Hybrid Black over bluetooth and streams it using the LSL. Is also able to record a stream to a file, and replay the stream as if it was in real-time to make it easier to test other components.
2. `exg-lsl/`: Grabs data from a custom 4 channel EEG device and outputs an LSL stream. Connection to the EEG device is done over Bluetooth Low Energy and controlled through a simple GUI.
3. `processing/`: Pulls in EEG data from an LSL stream, filters and processes it, and then outputs a neurofeedback score to a web socket server. Parameters related to the neurofeedback metric are configurable through the GUI. The GUI also displays various graphs to visually inspect the live data.
4. `lsl_subscriber/`: Contains random helper scripts to help debug and visualise LSL streams.
4. `analysis/`: Contains all the code used to analyse the data collected for the project. Also, contains the script that controlled the TTS during the experiment.

## Architecture


