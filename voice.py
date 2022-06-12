import time
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import os
import keyboard

LISTENER_COUNT = 1
ACTION_COOLDOWN = 1.5

NEXT_WORDS = ["next", "nest"]
BACK_WORDS = ["back", "beck", "fact"]


mic = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    mic.put(bytes(indata))

with sd.RawInputStream(samplerate=16000, blocksize = 8000, dtype='int16',
                        channels=1, callback=callback):

    model = Model("vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, 16000)

    got_partial = False
    
    last_action = time.time()
    while True:
        data = mic.get()

        if rec.AcceptWaveform(data):
            res = rec.Result()[14:-3]
            # We've already got the partial data
            continue
        else:
            res = rec.PartialResult()[17:-3]
        
        if res == "":
            continue

        print('[Rec:]', res)
        if any(next_word in res for next_word in NEXT_WORDS):
            if time.time() - last_action >= ACTION_COOLDOWN:
                keyboard.send("right")
                last_action = time.time()
        elif any(back_word in res for back_word in BACK_WORDS):
            if time.time() - last_action >= ACTION_COOLDOWN:
                keyboard.send("left")
                last_action = time.time()
