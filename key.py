import keyboard
import pyttsx3
import queue
import threading
import time

key_queue = queue.Queue()

def speech_worker():
    """Dynamically processes keypresses avoiding Windows COM freezes."""
    while True:
        key_name = key_queue.get()
        if key_name is None:
            break
        try:
            # Re-initializing locally ensures Windows wakes up the engine every time
            engine = pyttsx3.init('sapi5')
            engine.setProperty('rate', 220)
            engine.say(key_name)
            engine.runAndWait()
            # Explicitly teardown to free the audio layer
            del engine 
        except Exception:
            pass
        finally:
            key_queue.task_done()

# Start background worker
threading.Thread(target=speech_worker, daemon=True).start()

def on_key(event):
    if event.event_type == 'down':
        print(f"Heard: {event.name}")
        key_queue.put(event.name)

print("Listening on all windows... Type anything.")
keyboard.hook(on_key)
keyboard.wait()