import os
from time import sleep
from pylsl import StreamInfo, StreamOutlet, cf_string

instructions = [
    ("Hello, and welcome to the experiment", 0.0),
    ("Please look forward and relax to compute a baseline", 3 * 60),
    ("Please try to increase the brightness in the scene", 5 * 60),
    ("Please rest for 30 seconds...", 30),
    ("Please try to decrease the volume of the wind in the scene", 5 * 60),
    ("Please rest for 30 seconds...", 30),
    ("Please try to increase the brightness and decrease the volume of the wind in the scene", 5 * 60),
    ("Done!", 0),
]


info = StreamInfo('ExperimentMarkers', 'marker', 1, 0, cf_string, 'exp_markers_001')
outlet = StreamOutlet(info)

def speak(words: str) -> None:
    os.system(f"espeak-ng \"{words}\"")

input("Press enter to begin...")

for i, (words, t) in enumerate(instructions):
    print(words, t)
    outlet.push_sample([f"instruction_{i}_start"])

    speak(words)
    sleep(t)

