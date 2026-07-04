import keyboard
import queue
import threading
import win32com.client
import pythoncom
import time
import psutil
from datetime import datetime
import ctypes
import config
from pywinauto import Application # Directly extracts URL strings from chromium address bars

key_queue = queue.Queue()
word_buffer = []
modifiers = {'ctrl': False, 'shift': False, 'alt': False, 'windows': False}
last_window = ""

def speech_worker():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Rate = config.SETTINGS['voice_rate']
    while True:
        text = key_queue.get()
        if text is None: break
        speaker.Speak(text, 1)
        key_queue.task_done()

threading.Thread(target=speech_worker, daemon=True).start()

def speak(text):
    key_queue.put(text)

def clean_title(full_title):
    """Filters out files, search queries, and formats down to the pure app/tab name."""
    # Check our clean rule dictionary first
    for key, clean_name in config.CLEANUP_RULES.items():
        if key.lower() in full_title.lower():
            return clean_name
            
    # Fallback cleanup for standard windows (grabs the root app name after the last dash)
    if " - " in full_title:
        return full_title.split(" - ")[-1]
        
    return full_title

def check_active_window():
    global last_window
    while True:
        try:
            time.sleep(config.SETTINGS['window_check_delay'])
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            full_title = buff.value
            
            if full_title and full_title != last_window:
                last_window = full_title
                
                # Filter out system menus like the task switcher overlay itself
                if any(x in full_title.lower() for x in ["task switching", "task view"]):
                    continue
                    
                final_name = clean_title(full_title)
                speak(final_name) # Speaks ONLY the app/tab name directly
        except Exception:
            pass

threading.Thread(target=check_active_window, daemon=True).start()

def on_key_event(event):
    global word_buffer, modifiers

    clean_name = event.name.replace('right ', '').replace('left ', '')
    
    if clean_name in modifiers:
        modifiers[clean_name] = (event.event_type == 'down')
        return

    if event.event_type == 'down':
        # Check macro combos
        active_mods = [m for m, pressed in modifiers.items() if pressed]
        if active_mods:
            combo = "+".join(active_mods) + "+" + clean_name
            if combo in config.ACTION_MAP:
                speak(config.ACTION_MAP[combo])
            return

        # Word typing logic
        if len(clean_name) == 1:
            word_buffer.append(clean_name)
        elif clean_name == 'space':
            word = "".join(word_buffer)
            if word: speak(word)
            word_buffer = []
        elif clean_name == 'enter':
            word = "".join(word_buffer)
            if word: speak(word)
            word_buffer = []
        elif clean_name == 'backspace':
            # Silently pop letters from typing buffer without speaking anything
            if word_buffer:
                word_buffer.pop()
        elif clean_name in config.NAV_KEYS:
            speak(clean_name)

print("Minimalist Audio Guide Engine Running...")
keyboard.hook(on_key_event)
keyboard.wait()