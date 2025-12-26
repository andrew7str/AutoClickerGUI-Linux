import threading
from pynput import keyboard

def get_key_str(key):
    """Converts a pynput key object to a string representation."""
    if hasattr(key, 'char') and key.char is not None:
        return key.char
    # For special keys, str(key) gives 'Key.f1', etc.
    elif isinstance(key, keyboard.Key):
        return str(key)
    return None # Return None for unsupported types

class HotkeyListener(threading.Thread):
    def __init__(self, hotkeys, callbacks):
        """
        :param hotkeys: A dictionary mapping actions to key strings, e.g., {"record": "Key.f1"}.
        :param callbacks: A dictionary mapping actions to functions, e.g., {"record": on_record}.
        """
        super().__init__(daemon=True)
        self.hotkeys = hotkeys
        self.callbacks = callbacks
        self._listener = None

    def run(self):
        """Starts the keyboard listener."""
        # Create and start the listener within the thread
        with keyboard.Listener(on_press=self.on_press) as listener:
            self._listener = listener
            listener.join()  # This blocks until the listener is stopped

    def on_press(self, key):
        """Callback function for key presses."""
        key_str = get_key_str(key)
        for action, hotkey in self.hotkeys.items():
            if key_str == hotkey and action in self.callbacks:
                self.callbacks[action]()

    def stop(self):
        """Stops the keyboard listener."""
        if self._listener:
            self._listener.stop()

    def update_hotkeys(self, new_hotkeys):
        """Updates the hotkeys on the fly."""
        self.hotkeys = new_hotkeys

if __name__ == '__main__':
    # Example Usage
    import time

    def on_record():
        print("Record action triggered!")

    def on_stop():
        print("Stop action triggered!")

    def on_play():
        print("Play action triggered!")

    # Define hotkeys and their corresponding callbacks
    hotkey_config = {"record": "Key.f1", "stop": "Key.f2", "play": "Key.f3"}
    callback_map = {"record": on_record, "stop": on_stop, "play": on_play}

    # Create and start the listener
    hotkey_thread = HotkeyListener(hotkeys=hotkey_config, callbacks=callback_map)
    hotkey_thread.start()

    print("Hotkey listener started. Press F1, F2, or F3.")
    print("Press Ctrl+C to stop the main thread.")

    try:
        # Keep the main thread alive to see the output
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        hotkey_thread.stop()
        print("\nHotkey listener stopped.")
