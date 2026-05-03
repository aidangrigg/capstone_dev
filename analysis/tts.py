import os
from time import sleep

instructions = [
    ("Hello, and welcome to the experiment", 0.0),
    ("Please look forward and relax to compute a baseline", 3 * 60),
    ("Please try to increase the brightness in the scene", 3 * 60),
    ("Please try to decrease the volume of the wind in the scene", 3 * 60),
    ("Please try to increase the brightness and decrease the volume of the wind in the scene", 3 * 60),
    ("Please rest for 30 seconds...", 30),
    ("Please try to increase the brightness in the scene", 3 * 60),
    ("Please try to decrease the volume of the wind in the scene", 3 * 60),
    ("Please try to increase the brightness and decrease the volume of the wind in the scene", 3 * 60),
    ("Please rest for 30 seconds...", 30),
    ("Please try to increase the brightness in the scene", 3 * 60),
    ("Please try to decrease the volume of the wind in the scene", 3 * 60),
    ("Please try to increase the brightness and decrease the volume of the wind in the scene", 3 * 60),
    ("Done!", 0),
]

def speak(words: str) -> None:
    os.system(f"espeak-ng \"{words}\"")


for words, t in instructions:
    print(words)
    print(t)
    speak(words)
    sleep(t)

