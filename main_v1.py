import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from recorder import Recorder
from player import Player
from settings_manager import SettingsManager
from settings_window import SettingsWindow
from hotkey_listener import HotkeyListener
from edit_window import EditEventWindow

class AutoClickerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto Clicker")
        self.geometry("400x600")

        # Core components
        self.recorder = None
        self.recorded_events = []
        self.recorder_thread = None
        self.player_thread = None

        # Settings and Hotkeys
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()
        self.hotkey_listener = self.setup_hotkey_listener()
        self.hotkey_listener.start()

        self.create_menu()
        self.create_widgets()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_hotkey_listener(self):
        callbacks = {
            "record": lambda: self.after(0, self.start_recording),
            "stop": lambda: self.after(0, self.stop_recording),
            "play": lambda: self.after(0, self.play_macro),
        }
        return HotkeyListener(
            hotkeys=self.settings.get("hotkeys", {}),
            callbacks=callbacks
        )

    def on_closing(self):
        print("Closing application and stopping listeners...")
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        self.destroy()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Macro", command=self.save_macro)
        file_menu.add_command(label="Load Macro", command=self.load_macro)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Settings", command=self.open_settings_window)

    def open_settings_window(self):
        SettingsWindow(self, self.settings, self.on_settings_saved)

    def on_settings_saved(self, new_settings):
        self.settings = new_settings
        self.settings_manager.save_settings(self.settings)
        self.hotkey_listener.update_hotkeys(self.settings.get("hotkeys", {}))
        self.status_bar.config(text="Status: Settings saved.")
        messagebox.showinfo("Settings", "Hotkey settings have been updated.")

    def create_widgets(self):
        # --- Control Buttons ---
        control_frame = ttk.Frame(self, padding="10")
        control_frame.pack(fill=tk.X)
        self.record_button = ttk.Button(control_frame, text="Record", command=self.start_recording)
        self.record_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.play_button = ttk.Button(control_frame, text="Play", command=self.play_macro, state=tk.DISABLED)
        self.play_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        # --- Playback Options ---
        options_frame = ttk.LabelFrame(self, text="Playback Options", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(options_frame, text="Repetitions:").pack(side=tk.LEFT, padx=(0, 5))
        self.repeat_var = tk.StringVar(value="1")
        self.repeat_spinbox = ttk.Spinbox(options_frame, from_=1, to=1000, textvariable=self.repeat_var, width=5)
        self.repeat_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(options_frame, text="Speed (x):").pack(side=tk.LEFT, padx=(10, 5))
        self.speed_var = tk.StringVar(value="1.0")
        self.speed_spinbox = ttk.Spinbox(options_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.speed_var, width=5)
        self.speed_spinbox.pack(side=tk.LEFT, padx=5)

        # --- Action List ---
        list_frame = ttk.Frame(self, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        self.action_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.action_listbox.bind("<Double-1>", self.open_event_editor)
        self.action_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.action_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.action_listbox.config(yscrollcommand=scrollbar.set)

        # --- Edit Frame ---
        edit_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        edit_frame.pack(fill=tk.X)
        self.delete_button = ttk.Button(edit_frame, text="Delete Selected Action", command=self.delete_selected_action)
        self.delete_button.pack(fill=tk.X, expand=True)
        
        # --- Status Bar ---
        self.status_bar = ttk.Label(self, text="Status: Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def open_event_editor(self, _=None):
        selected_indices = self.action_listbox.curselection()
        if not selected_indices:
            return
        index = selected_indices[0]
        event_data = self.recorded_events[index]
        EditEventWindow(self, event_data, index, self.on_event_saved)

    def on_event_saved(self, index, updated_event):
        self.recorded_events[index] = updated_event
        self.action_listbox.delete(index)
        self.action_listbox.insert(index, self._format_event_for_display(updated_event))
        self.status_bar.config(text=f"Status: Event #{index + 1} updated.")

    def delete_selected_action(self):
        selected_indices = self.action_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "No action selected to delete.")
            return
        for index in reversed(selected_indices):
            self.action_listbox.delete(index)
            del self.recorded_events[index]
        self.status_bar.config(text=f"Status: Deleted action(s).")
        if not self.recorded_events:
            self.play_button.config(state=tk.DISABLED)

    def save_macro(self):
        if not self.recorded_events:
            messagebox.showwarning("Warning", "Nothing to save.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not filepath: return
        with open(filepath, 'w') as f:
            json.dump(self.recorded_events, f, indent=4)
        self.status_bar.config(text=f"Status: Macro saved to {filepath}")

    def load_macro(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not filepath: return
        try:
            with open(filepath, 'r') as f:
                loaded_events = json.load(f)
            if not isinstance(loaded_events, list):
                raise TypeError("JSON file does not contain a list of events.")
            self.recorded_events = loaded_events
            self.action_listbox.delete(0, tk.END)
            for event in self.recorded_events:
                self.action_listbox.insert(tk.END, self._format_event_for_display(event))
            self.play_button.config(state=tk.NORMAL if self.recorded_events else tk.DISABLED)
            self.status_bar.config(text=f"Status: Macro loaded from {filepath}")
        except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
            messagebox.showerror("Error", f"Failed to load macro: {e}")
            self.status_bar.config(text="Status: Error loading macro")

    def handle_action(self, event):
        self.after(0, self.add_action_to_gui, event)

    def add_action_to_gui(self, event):
        self.recorded_events.append(event)
        self.action_listbox.insert(tk.END, self._format_event_for_display(event))
    
    def _format_event_for_display(self, event):
        event_str = f"Type: {event.get('type', 'N/A')}, Delay: {event.get('time', 0):.2f}s"
        if event.get('type') == 'click':
            event_str += f", Pos: ({event.get('x', 0)}, {event.get('y', 0)}), Button: {event.get('button', 'N/A')}"
        elif event.get('type') == 'key_press':
            event_str += f", Key: {event.get('key', 'N/A')}"
        return event_str

    def start_recording(self):
        if self.recorder is not None:
             print("Already recording.")
             return 
        self.status_bar.config(text="Status: Recording...")
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.DISABLED)
        self.action_listbox.delete(0, tk.END)
        self.recorded_events = []
        self.recorder = Recorder(action_callback=self.handle_action)
        self.recorder_thread = threading.Thread(target=self.recorder.start, daemon=True)
        self.recorder_thread.start()

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
            self.recorder = None
            self.status_bar.config(text="Status: Stopped")
            self.record_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            if self.recorded_events:
                self.play_button.config(state=tk.NORMAL)
        else:
            print("Not currently recording.")

    def on_playback_complete(self):
        self.status_bar.config(text="Status: Finished playing")
        self.play_button.config(state=tk.NORMAL)
        self.record_button.config(state=tk.NORMAL)
        self.player_thread = None

    def safe_playback_complete(self):
        self.after(0, self.on_playback_complete)

    def play_macro(self):
        if self.player_thread and self.player_thread.is_alive():
            print("Already playing a macro.")
            return
        if not self.recorded_events:
            messagebox.showinfo("Info", "No macro to play.")
            return
        try:
            repetitions = int(self.repeat_var.get())
            speed = float(self.speed_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid input for Repetitions or Speed.")
            return
        self.status_bar.config(text="Status: Playing...")
        self.play_button.config(state=tk.DISABLED)
        self.record_button.config(state=tk.DISABLED)
        player = Player(self.recorded_events)
        self.player_thread = threading.Thread(
            target=player.play,
            kwargs={"repetitions": repetitions, "speed_multiplier": speed, "on_complete_callback": self.safe_playback_complete},
            daemon=True
        )
        self.player_thread.start()

if __name__ == "__main__":
    app = AutoClickerGUI()
    app.mainloop()
