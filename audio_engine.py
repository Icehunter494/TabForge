import os
import ctypes
import time

BASE_DIR = os.path.dirname(__file__)
DLL_DIR = os.path.join(BASE_DIR, "fluidsynth")

#force adds dlls
os.add_dll_directory(DLL_DIR)

# force-load dll
ctypes.CDLL(os.path.join(DLL_DIR, "libfluidsynth.dll"))

import fluidsynth

STANDARD_TUNING = [64, 59, 55, 50, 45, 40]

fs = fluidsynth.Synth()
fs.start(driver="dsound")

SOUNDFONT_PATH = os.path.join(BASE_DIR, "soundfonts", "guitar.sf2")

sfid = fs.sfload(SOUNDFONT_PATH)
fs.program_select(0, sfid, 0, 24)


def play_fret(string_index, fret, duration=0.3):

    midi_note = STANDARD_TUNING[string_index] + fret

    fs.noteon(0, midi_note, 100)

    time.sleep(duration)

    fs.noteoff(0, midi_note)