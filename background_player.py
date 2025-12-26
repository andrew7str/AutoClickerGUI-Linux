from Xlib import display, X
from Xlib.protocol import event as xevent
import time

class BackgroundPlayer:
    def __init__(self, window, events):
        self.window = window
        self.events = events
        self.stop_requested = False
        self.display = display.Display()

    def stop(self):
        """Signals the player to stop playback."""
        self.stop_requested = True

    def play(self, repetitions=1, speed_multiplier=1.0, on_complete_callback=None):
        """
        Plays the recorded events in the background on the target window.
        """
        print(f"Starting background playback... (Repetitions: {repetitions}, Speed: {speed_multiplier}x)")
        self.stop_requested = False

        if speed_multiplier <= 0:
            speed_multiplier = 1.0

        for i in range(repetitions):
            if self.stop_requested:
                break
            
            print(f"Repetition {i + 1}/{repetitions}")
            for event in self.events:
                if self.stop_requested:
                    break

                delay = event['time'] / speed_multiplier
                end_time = time.time() + delay
                while time.time() < end_time:
                    if self.stop_requested:
                        break
                    time.sleep(0.01)

                if self.stop_requested:
                    break

                if event['type'] == 'click':
                    self.send_click(event['x'], event['y'], event['button'])

        if self.stop_requested:
            print("Background playback stopped by user.")
        else:
            print("Background playback finished.")
        
        if on_complete_callback:
            on_complete_callback()

    def send_click(self, x, y, button_str):
        # This is the core of the background clicking logic
        # We need to create and send a ButtonPress and ButtonRelease event
        
        button_code = self._get_button_code(button_str)
        if not button_code:
            return

        # Create the events
        press_event = self._create_button_event(X.ButtonPress, x, y, button_code)
        release_event = self._create_button_event(X.ButtonRelease, x, y, button_code)

        # Send the events
        self.window.send_event(press_event, propagate=True)
        self.display.flush()
        
        time.sleep(0.05) # Small delay between press and release
        
        self.window.send_event(release_event, propagate=True)
        self.display.flush()


    def _create_button_event(self, event_type, x, y, button_code):
        root = self.display.screen().root
        
        event_class = None
        if event_type == X.ButtonPress:
            event_class = xevent.ButtonPress
        elif event_type == X.ButtonRelease:
            event_class = xevent.ButtonRelease
        else:
            return None # Should not happen

        return event_class(
            time=int(time.time()),
            root=root,
            window=self.window,
            child=0,
            root_x=x,
            root_y=y,
            event_x=x,
            event_y=y,
            state=0, # or the appropriate modifier mask
            same_screen=1,
            detail=button_code
        )

    def _get_button_code(self, button_str):
        if 'left' in button_str:
            return 1 # X11 button code for left
        elif 'right' in button_str:
            return 3 # X11 button code for right
        elif 'middle' in button_str:
            return 2 # X11 button code for middle
        return None

if __name__ == '__main__':
    # This file is not meant to be run directly.
    # It is a module to be used by main.py.
    pass
