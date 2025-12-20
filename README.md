# Brainground

(TODO: write a proper description)

## Structure

This project is broken up into several programs, instructions for each can be found in the `README.md` in their individual directory. The following is brief description of what each program does:
1. `datastream/`: Grabs data from the g.tec Unicorn Hybrid Black over bluetooth and streams it using the LSL. Is also able to record a stream to a file, and replay the stream as if it was in real-time to make it easier to test other components.
2. `processing/`: Pulls in EEG data from an LSL stream, filters and processes it, and then outputs a neurofeedback score to a web socket. Parameters can be controlled through the web socket, or through a QT GUI application. The GUI also displays various graphs to visually inspect the live data.

