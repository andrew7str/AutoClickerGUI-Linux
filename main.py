import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import threading
import json
from pynput import mouse
from Xlib import display
from recorder import Recorder
from player import Player
from background_player import BackgroundPlayer
from settings_manager import SettingsManager
from window_selector import WindowSelector
from settings_window import SettingsWindow
from hotkey_listener import HotkeyListener
from edit_window import EditEventWindow
from add_event_dialog import AddEventDialog # Added for AddEventDialog

class AutoClickerGUI(ttk.Window):
    def __init__(self):
        super().__init__() # Initialize Tkinter first

        # Load settings before applying the theme
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()
        theme_name = self.settings.get("theme", "litera")
        self.style.theme_use(theme_name) # Apply the theme after initialization
        
        self.title("Auto Clicker")
        self.geometry("450x700") # Increased size for better layout

        # Core components
        self.recorder = None
        self.recorded_events = []
        self.recorder_thread = None
        self.player_thread = None
        self.player = None # Added for interruptible playback
        self.target_window = None # For background clicking

        # Hotkeys (COMMENTED OUT FOR DEBUGGING)
        self.hotkey_listener = self.setup_hotkey_listener()
        self.hotkey_listener.start()

        self.create_menu()
        self.create_widgets()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_target_window(self):
        dialog = WindowSelector(self)
        self.wait_window(dialog)
        
        if dialog.selected_window:
            self.target_window = dialog.selected_window
            window_name = self.target_window.get_wm_name() or self.target_window.get_icccm_name() or "Unknown"
            self.target_window_label.config(text=f"Target: {window_name} ({self.target_window.id})")
            self.status_bar.config(text="Status: Target window selected.")
        else:
            self.status_bar.config(text="Status: No target window selected.")

    def setup_hotkey_listener(self):
        callbacks = {
            "record": lambda: self.after(0, self.start_recording),
            "stop": lambda: self.after(0, self.smart_stop), # Changed
            "play": lambda: self.after(0, self.play_macro),
        }
        return HotkeyListener(
            hotkeys=self.settings.get("hotkeys", {}),
            callbacks=callbacks
        )

    def smart_stop(self):
        """Stops the current action, whether it's recording or playing."""
        if self.player_thread and self.player_thread.is_alive():
            self.stop_playback()
        elif self.recorder and self.recorder_thread: # Check recorder thread too
            self.stop_recording()
        else:
            print("Nothing to stop.")

    def on_closing(self):
        print("Closing application and stopping listeners...")
        if self.hotkey_listener: # COMMENTED OUT FOR DEBUGGING
            self.hotkey_listener.stop()
        self.destroy()

    def create_menu(self):
        menubar = tk.Menu(self) # tk.Menu is used for base Tkinter menu widgets
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
        old_theme = self.settings.get("theme")
        new_theme = new_settings.get("theme")

        self.settings = new_settings
        self.settings_manager.save_settings(self.settings)
        self.hotkey_listener.update_hotkeys(self.settings.get("hotkeys", {})) # COMMENTED OUT FOR DEBUGGING
        
        self.status_bar.config(text="Status: Settings saved.")

        if old_theme != new_theme:
            messagebox.showinfo("Theme Changed", "A restart is required to apply the new theme.", parent=self)
        else:
            messagebox.showinfo("Settings", "Hotkey settings have been updated.", parent=self)

    def create_widgets(self):
        # --- Control Buttons ---
        control_frame = ttk.Frame(self, padding="10")
        control_frame.pack(fill=X)
        self.record_button = ttk.Button(control_frame, text="Record", command=self.start_recording, bootstyle=(SUCCESS, OUTLINE))
        self.record_button.pack(side=LEFT, expand=True, fill=X, padx=5)
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_recording, state=DISABLED, bootstyle=DANGER)
        self.stop_button.pack(side=LEFT, expand=True, fill=X, padx=5)
        self.play_button = ttk.Button(control_frame, text="Play", command=self.play_macro, state=DISABLED, bootstyle=(PRIMARY, OUTLINE))
        self.play_button.pack(side=LEFT, expand=True, fill=X, padx=5)

        # --- Playback Options ---
        options_frame = ttk.Labelframe(self, text="Playback Options", padding="10")
        options_frame.pack(fill=X, padx=10, pady=5)
        
        # Repetitions and Speed
        ttk.Label(options_frame, text="Repetitions:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.repeat_var = ttk.StringVar(value="1")
        self.repeat_spinbox = ttk.Spinbox(options_frame, from_=1, to=1000, textvariable=self.repeat_var, width=5)
        self.repeat_spinbox.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(options_frame, text="Speed (x):").grid(row=0, column=2, padx=(10, 5), sticky="w")
        self.speed_var = ttk.StringVar(value="1.0")
        self.speed_spinbox = ttk.Spinbox(options_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.speed_var, width=5)
        self.speed_spinbox.grid(row=0, column=3, padx=5, sticky="w")

        # Target Window Selection
        self.select_target_button = ttk.Button(options_frame, text="Select Target Window", command=self.select_target_window, bootstyle=INFO)
        self.select_target_button.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        
        self.target_window_label = ttk.Label(options_frame, text="Target: None")
        self.target_window_label.grid(row=1, column=2, columnspan=2, pady=(10, 0), padx=10, sticky="w")

        # Background mode
        self.background_mode_var = tk.BooleanVar()
        self.background_mode_check = ttk.Checkbutton(options_frame, text="Enable Background Mode", variable=self.background_mode_var)
        self.background_mode_check.grid(row=2, column=0, columnspan=2, pady=(10,0), sticky="w")

        self.replay_var = tk.BooleanVar()
        self.replay_check = ttk.Checkbutton(options_frame, text="Replay Indefinitely", variable=self.replay_var)
        self.replay_check.grid(row=2, column=2, columnspan=2, pady=(10, 0), sticky="w")



        # --- Action List ---
        list_frame = ttk.Frame(self, padding="10")
        list_frame.pack(fill=BOTH, expand=True)
        self.action_listbox = tk.Listbox(list_frame, selectmode=SINGLE)
        self.action_listbox.bind("<Double-1>", self.open_event_editor)
        self.action_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.action_listbox.yview, bootstyle="round")
        scrollbar.pack(side=RIGHT, fill=Y)
        self.action_listbox.config(yscrollcommand=scrollbar.set)

        # --- Edit & Add Frame ---
        edit_add_frame = ttk.Labelframe(self, text="Edit Macro", padding=(10)) # Fixed LabelFrame here
        edit_add_frame.pack(fill=X, padx=10, pady=5)
        self.delete_button = ttk.Button(edit_add_frame, text="Delete Selected Action", command=self.delete_selected_action, bootstyle=(DANGER, OUTLINE))
        self.delete_button.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.add_click_button = ttk.Button(edit_add_frame, text="Add Click...", command=self.add_click_event, bootstyle=OUTLINE) # Added
        self.add_click_button.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.add_key_button = ttk.Button(edit_add_frame, text="Add Key Press...", command=self.add_key_event, bootstyle=OUTLINE) # Added
        self.add_key_button.pack(side=LEFT, fill=X, expand=True, padx=(5, 0))
        
        # --- Status Bar ---
        self.status_bar = ttk.Label(self, text="Status: Ready", relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)
    
    def _get_selected_index(self):
        indices = self.action_listbox.curselection()
        return indices[0] if indices else None

    def _insert_event_at_selection(self, event): # Added/Re-added
        index = self._get_selected_index()
        if index is None:
            self.recorded_events.append(event)
            self.action_listbox.insert(END, self._format_event_for_display(event))
        else:
            self.recorded_events.insert(index, event)
            self.action_listbox.insert(index, self._format_event_for_display(event))
        
        if self.recorded_events:
            self.play_button.config(state=NORMAL)
        self.status_bar.config(text=f"Status: Added new {event['type']} event.")

    def add_click_event(self): # Added/Re-added
        dialog = AddEventDialog(self, title="Add Click Event", event_type='click')
        if dialog.result:
            self._insert_event_at_selection(dialog.result)

    def add_key_event(self): # Added/Re-added
        dialog = AddEventDialog(self, title="Add Key Press Event", event_type='key_press')
        if dialog.result:
            self._insert_event_at_selection(dialog.result)

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
            self.play_button.config(state=DISABLED)

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
            self.action_listbox.delete(0, END)
            for event in self.recorded_events:
                self.action_listbox.insert(END, self._format_event_for_display(event))
            self.play_button.config(state=NORMAL if self.recorded_events else DISABLED)
            self.status_bar.config(text=f"Status: Macro loaded from {filepath}")
        except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
            messagebox.showerror("Error", f"Failed to load macro: {e}")
            self.status_bar.config(text="Status: Error loading macro")

    def handle_action(self, event):
        self.after(0, self.add_action_to_gui, event)

    def add_action_to_gui(self, event):
        self.recorded_events.append(event)
        self.action_listbox.insert(END, self._format_event_for_display(event))
    
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
        self.record_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        self.play_button.config(state=DISABLED)
        self.action_listbox.delete(0, END)
        self.recorded_events = []
        self.recorder = Recorder(action_callback=self.handle_action)
        self.recorder_thread = threading.Thread(target=self.recorder.start, daemon=True)
        self.recorder_thread.start()

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
            self.recorder = None
            self.status_bar.config(text="Status: Stopped")
            self.record_button.config(state=NORMAL)
            self.stop_button.config(state=DISABLED)
            if self.recorded_events:
                self.play_button.config(state=NORMAL)
        else:
            print("Not currently recording.")

    def stop_playback(self): # Re-added for interruptible playback
        """Stops the playback thread."""
        if self.player:
            self.player.stop()
        
        # GUI updates are handled by on_playback_complete or immediately
        self.status_bar.config(text="Status: Playback stopped by user.")
        self.play_button.config(state=NORMAL)
        self.record_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED, command=self.stop_recording)
        self.player = None
        self.player_thread = None

    def on_playback_complete(self):
        print("on_playback_complete called") # Diagnostic print
        self.status_bar.config(text="Status: Finished playing")
        self.play_button.config(state=NORMAL)
        self.record_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED, command=self.stop_recording) # Added
        self.player_thread = None
        self.player = None

    def safe_playback_complete(self):
        print("safe_playback_complete called") # Diagnostic print
        self.after(0, self.on_playback_complete)

    def play_macro(self):
        if self.player_thread and self.player_thread.is_alive():
            print("Already playing a macro.")
            return
        if not self.recorded_events:
            messagebox.showinfo("Info", "No macro to play.")
            return

        if self.background_mode_var.get():
            if not self.target_window:
                messagebox.showerror("Error", "No target window selected for background mode.")
                return
            
            try:
                if self.replay_var.get():
                    repetitions = 999999 # A large number to simulate infinity
                else:
                    repetitions = int(self.repeat_var.get())
                speed = float(self.speed_var.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid input for Repetitions or Speed.")
                return

            self.status_bar.config(text="Status: Playing in background...")
            self.play_button.config(state=DISABLED)
            self.record_button.config(state=DISABLED)
            self.stop_button.config(state=NORMAL, command=self.stop_playback)

            self.player = BackgroundPlayer(self.target_window, self.recorded_events)
            self.player_thread = threading.Thread(
                target=self.player.play,
                kwargs={"repetitions": repetitions, "speed_multiplier": speed, "on_complete_callback": self.safe_playback_complete},
                daemon=True
            )
            self.player_thread.start()

        else:
            try:
                if self.replay_var.get():
                    repetitions = 999999 # A large number to simulate infinity
                else:
                    repetitions = int(self.repeat_var.get())
                speed = float(self.speed_var.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid input for Repetitions or Speed.")
                return
            self.status_bar.config(text="Status: Playing...")
            self.play_button.config(state=DISABLED)
            self.record_button.config(state=DISABLED)
            self.stop_button.config(state=NORMAL, command=self.stop_playback) # Added
            self.player = Player(self.recorded_events)
            self.player_thread = threading.Thread(
                target=self.player.play,
                kwargs={"repetitions": repetitions, "speed_multiplier": speed, "on_complete_callback": self.safe_playback_complete},
                daemon=True
            )
            self.player_thread.start()

if __name__ == "__main__":
    print("Main app starting...") # Diagnostic print
    app = AutoClickerGUI()
    print("AutoClickerGUI initialized.") # Diagnostic print
    app.mainloop()
    print("Main app exiting.") # Diagnostic print