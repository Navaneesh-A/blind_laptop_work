import keyboard
import time

print("Tracking started. Do your usual actions for 2-3 minutes, then press ESC to save.")

actions_log = []
start_time = time.time()

def on_key(event):
    if event.event_type == 'down':
        timestamp = round(time.time() - start_time, 2)
        actions_log.append(f"{timestamp}: {event.name}\n")

keyboard.hook(on_key)
keyboard.wait('esc')  # Press Escape when you are done

# Save everything you did to a text file
with open("my_workflow.txt", "w") as f:
    f.writelines(actions_log)

print("Tracking complete! 'my_workflow.txt' has been saved.")