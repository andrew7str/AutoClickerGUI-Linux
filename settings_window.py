import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class SettingsWindow(ttk.Toplevel):
    def __init__(self, master, current_settings, on_save_callback):
        super().__init__(master)
        self.title("Settings")
        self.transient(master)
        self.grab_set()

        self.current_settings = current_settings
        self.on_save = on_save_callback

        # Variable for the theme
        self.theme_var = ttk.StringVar(value=current_settings.get("theme", "litera"))

        self.hotkey_vars = {
            action: ttk.StringVar(value=key)
            for action, key in current_settings.get("hotkeys", {}).items()
        }

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=BOTH, expand=True)

        # --- Theme Selection ---
        theme_frame = ttk.Labelframe(frame, text="Appearance", padding=10)
        theme_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        ttk.Label(theme_frame, text="Theme:").pack(side=LEFT, padx=5)
        
        theme_combo = ttk.Combobox(
            theme_frame, 
            textvariable=self.theme_var, 
            values=self.master.style.theme_names(),
            state="readonly"
        )
        theme_combo.pack(side=LEFT, expand=True, fill=X, padx=5)


        # --- Hotkey Settings ---
        hotkey_frame = ttk.Labelframe(frame, text="Hotkeys", padding=10)
        hotkey_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        ttk.Label(hotkey_frame, text="Click on a field, then press the desired key.").grid(row=0, column=0, columnspan=2, pady=(0, 10))

        row = 1
        for action, var in self.hotkey_vars.items():
            ttk.Label(hotkey_frame, text=f"{action.capitalize()} Hotkey:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(hotkey_frame, textvariable=var, state="readonly")
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            
            entry.bind("<Button-1>", lambda e, v=var, en=entry: self.set_focus_and_bind(v, en))
            row += 1

        # --- Buttons ---
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        save_button = ttk.Button(button_frame, text="Save", command=self.save_and_close, bootstyle=SUCCESS)
        save_button.pack(side=LEFT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy, bootstyle=DANGER)
        cancel_button.pack(side=LEFT, padx=5)

    def set_focus_and_bind(self, var, entry):
        var.set("Press a key...")
        entry.focus()
        entry.bind("<KeyPress>", lambda e, v=var, en=entry: self.capture_key(e, v, en), add="+")

    def capture_key(self, event, var, entry):
        if event.keysym and event.keysym not in ('Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R'):
            key_name = event.keysym
            if len(key_name) == 1:
                key_str = key_name
            else:
                pynput_map = {
                    'BackSpace': 'Key.backspace', 'Tab': 'Key.tab', 'Return': 'Key.enter',
                    'Escape': 'Key.esc', 'space': 'Key.space', 'Delete': 'Key.delete',
                    'Up': 'Key.up', 'Down': 'Key.down', 'Left': 'Key.left', 'Right': 'Key.right',
                }
                if key_name in pynput_map:
                    key_str = pynput_map[key_name]
                elif 'F' in key_name and key_name[1:].isdigit():
                    key_str = f"Key.{key_name.lower()}"
                else:
                    key_str = key_name
            var.set(key_str)
        
        entry.unbind("<KeyPress>")
        self.focus()
        return "break"

    def save_and_close(self):
        new_hotkeys = {action: var.get() for action, var in self.hotkey_vars.items()}
        self.current_settings["hotkeys"] = new_hotkeys
        self.current_settings["theme"] = self.theme_var.get()
        
        if self.on_save:
            self.on_save(self.current_settings)
        
        self.destroy()

if __name__ == '__main__':
    # Example usage requires a themed window now
    root = ttk.Window(themename="superhero")
    root.title("Main App")

    def on_settings_saved(settings):
        print("Settings were saved:", settings)

    test_settings = {
        "theme": "superhero",
        "hotkeys": {
            "record": "Key.f1",
            "stop": "Key.f2",
            "play": "Key.f3"
        }
    }

    def open_settings():
        SettingsWindow(root, test_settings, on_settings_saved)

    ttk.Button(root, text="Open Settings", command=open_settings).pack(pady=20, padx=20)

    root.mainloop()
