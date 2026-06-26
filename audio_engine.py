import numpy as np
import pygame

pygame.mixer.init(frequency=44100, size=-16, channels=2)

STANDARD_TUNING = [
    64, 59, 55, 50, 45, 40
]

def midi_to_freq(note):
    return 440 * (2 ** ((note - 69) / 12))


# guitar types
GUITAR_PROFILES = {

    "clean": {
        "harmonics": [1.0, 0.5, 0.25, 0.12],
        "decay": 6.0,
        "noise": 0.01,
        "distortion": 1.0
    },

    "jazz": {
        "harmonics": [1.0, 0.35, 0.15],
        "decay": 8.0,
        "noise": 0.005,
        "distortion": 0.8
    },

    "overdrive": {
        "harmonics": [1.0, 0.8, 0.6, 0.4, 0.3],
        "decay": 4.5,
        "noise": 0.02,
        "distortion": 2.5
    },

    "metal": {
        "harmonics": [1.0, 1.2, 0.9, 0.7, 0.5],
        "decay": 3.5,
        "noise": 0.03,
        "distortion": 4.0
    }
}


CURRENT_PROFILE = "clean"


def set_guitar_type(name):
    global CURRENT_PROFILE
    if name in GUITAR_PROFILES:
        CURRENT_PROFILE = name


# sound
def create_guitar_tone(freq, duration=0.35):

    profile = GUITAR_PROFILES[CURRENT_PROFILE]

    sample_rate = 44100

    t = np.linspace(
        0,
        duration,
        int(sample_rate * duration),
        False
    )

    wave = np.zeros_like(t)

    # harmonics
    for i, amp in enumerate(profile["harmonics"], 1):
        wave += amp * np.sin(2 * np.pi * freq * i * t)

    # soft distortion (waveshaping)
    wave = np.tanh(wave * profile["distortion"])

    # decay envelope
    envelope = np.exp(-profile["decay"] * t)
    wave *= envelope

    # noise (pick attack realism)
    wave += np.random.normal(0, profile["noise"], len(wave))

    # normalize
    wave /= np.max(np.abs(wave) + 1e-6)

    audio = (wave * 32767).astype(np.int16)

    stereo = np.column_stack((audio, audio))

    return pygame.sndarray.make_sound(stereo)


def play_fret(string_index, fret, duration=0.35):

    midi_note = STANDARD_TUNING[string_index] + int(fret)
    freq = midi_to_freq(midi_note)

    sound = create_guitar_tone(freq, duration)
    sound.play()