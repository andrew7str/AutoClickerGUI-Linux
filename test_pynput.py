from pynput import keyboard
import time

def on_press(key):
    try:
        print(f"Key pressed: {key}, char: {key.char}")
    except AttributeError:
        print(f"Special key pressed: {key}")

def main():
    print("Starting pynput listener test...")
    with keyboard.Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except Exception as e:
            print(f"An exception occurred: {e}")

if __name__ == "__main__":
    main()
