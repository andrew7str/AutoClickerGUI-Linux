from pynput import mouse, keyboard
import time
import threading

class Player:
    def __init__(self, events):
        self.events = events
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.stop_requested = False

    def stop(self):
        """Signals the player to stop playback."""
        print("Stop requested for player.")
        self.stop_requested = True

    def play(self, repetitions=1, speed_multiplier=1.0, on_complete_callback=None):
        """
        Plays the recorded events. This method is blocking but can be
        interrupted by calling the stop() method from another thread.
        """
        print(f"Starting playback... (Repetitions: {repetitions}, Speed: {speed_multiplier}x)")
        self.stop_requested = False

        if speed_multiplier <= 0:
            print("Warning: Speed multiplier must be positive. Defaulting to 1.0x.")
            speed_multiplier = 1.0

        for i in range(repetitions):
            if self.stop_requested:
                break
            
            print(f"Repetition {i + 1}/{repetitions}")
            for event in self.events:
                if self.stop_requested:
                    break

                # Custom sleep loop to allow for interruption
                delay = event['time'] / speed_multiplier
                end_time = time.time() + delay
                while time.time() < end_time:
                    if self.stop_requested:
                        break
                    time.sleep(0.01)  # Check for stop signal every 10ms

                if self.stop_requested:
                    break

                # Execute the event
                if event['type'] == 'click':
                    self.mouse_controller.position = (event['x'], event['y'])
                    button = self._get_button(event['button'])
                    if button:
                        self.mouse_controller.click(button, 1)

                elif event['type'] == 'key_press':
                    key_to_press = self._get_key(event['key'])
                    self.keyboard_controller.press(key_to_press)
                    self.keyboard_controller.release(key_to_press)
            
            if self.stop_requested:
                break

        if self.stop_requested:
            print("Playback stopped by user.")
        else:
            print("Playback finished.")
            if on_complete_callback:
                on_complete_callback()
    
    def _get_button(self, button_str):
        if 'left' in button_str:
            return mouse.Button.left
        elif 'right' in button_str:
            return mouse.Button.right
        elif 'middle' in button_str:
            return mouse.Button.middle
        return None

    def _get_key(self, key_str):
        if key_str.startswith('Key.'):
            key_name = key_str.split('.')[1]
            if hasattr(keyboard.Key, key_name):
                return getattr(keyboard.Key, key_name)
        return key_str


if __name__ == '__main__':
    # Example usage for testing the interrupt functionality
    sample_events = [
        {'time': 2.0, 'type': 'key_press', 'key': 'a'},
        {'time': 2.0, 'type': 'key_press', 'key': 'b'},
        {'time': 2.0, 'type': 'key_press', 'key': 'c'},
    ]

    player = Player(sample_events)

    # Simulate stopping playback from another thread
    def stop_it_later():
        print("Will send stop signal in 3 seconds...")
        time.sleep(3)
        player.stop()

    playback_thread = threading.Thread(target=player.play)
    stopper_thread = threading.Thread(target=stop_it_later)

    print("Starting playback test. It should stop after 'a' is pressed.")
    playback_thread.start()
    stopper_thread.start()

    playback_thread.join()
    stopper_thread.join()

    print("\nTest finished.")