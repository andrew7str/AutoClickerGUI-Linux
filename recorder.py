import time
from pynput import mouse, keyboard

class Recorder:
    def __init__(self, action_callback):
        self.action_callback = action_callback
        self._events = []
        self._running = False
        self._start_time = None

        self.mouse_listener = mouse.Listener(
            on_click=self.on_click
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press
        )

    def start(self):
        self._events = []
        self._running = True
        self._start_time = time.time()
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop(self):
        if self._running:
            self._running = False
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            # The listeners need to be joined by the thread that started them.
            # We will handle the thread management in the main GUI file.
            return self._events

    def _add_event(self, event_type, **kwargs):
        if not self._running:
            return
            
        current_time = time.time()
        delay = current_time - self._start_time
        self._start_time = current_time

        event = {"time": delay, "type": event_type, **kwargs}
        self._events.append(event)
        
        # Use the callback to notify the GUI
        self.action_callback(event)

    def on_click(self, x, y, button, pressed):
        if pressed:
            self._add_event(
                "click",
                x=x,
                y=y,
                button=str(button) # Convert button object to string
            )

    def on_press(self, key):
        # Handle special keys and regular keys
        try:
            # For character keys
            key_char = key.char
            self._add_event("key_press", key=key_char)
        except AttributeError:
            # For special keys (e.g., shift, ctrl, space)
            key_str = str(key)
            self._add_event("key_press", key=key_str)

if __name__ == '__main__':
    # Example usage for testing the recorder directly
    def print_action(action):
        print(action)

    print("Starting recorder in 3 seconds...")
    time.sleep(3)
    
    recorder = Recorder(action_callback=print_action)
    recorder.start()
    
    print("Recorder started. Click and type to see events. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        events = recorder.stop()
        print("\nRecorder stopped.")
        print("\nRecorded events:")
        for e in events:
            print(e)
