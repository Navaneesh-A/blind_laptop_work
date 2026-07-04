import keyboard
import queue
import threading
import win32com.client
import pythoncom  # <--- Added this import

key_queue = queue.Queue()

def speech_worker():
    # Correct initialization for background thread COM routing
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Rate = 5  # Speed: 1 to 10

    while True:
        key_name = key_queue.get()
        if key_name is None:
            break
        
        # Asynchronous speak flag (1) guarantees zero delay/lag
        speaker.Speak(key_name, 1) 
        key_queue.task_done()

# Start background audio thread
threading.Thread(target=speech_worker, daemon=True).start()

def on_key(event):
    if event.event_type == 'down':
        print(f"Fast Heard: {event.name}")
        key_queue.put(event.name)

print("Ultra-fast engine ready. Start typing...")
keyboard.hook(on_key)
keyboard.wait()