import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from Xlib import display, X

class WindowSelector(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Select Target Window")
        self.geometry("400x500")
        self.transient(master)
        self.grab_set()

        self.selected_window = None
        self.windows = self.get_open_windows()

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def get_open_windows(self):
        windows = {}
        d = display.Display()
        root = d.screen().root

        try:
            for window in root.query_tree().children:
                try:
                    attrs = window.get_attributes()
                    if attrs and attrs.map_state == X.IsViewable:
                        name = window.get_wm_name()
                        if not name:
                            name = window.get_icccm_name()
                        
                        if name:
                            windows[name] = window
                except Exception:
                    # Ignore windows that cause errors (e.g., have been destroyed)
                    pass
        except Exception as e:
            print(f"Error getting open windows: {e}")

        return windows

    def create_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Select a window to target:").pack(fill=tk.X, pady=(0, 5))

        self.window_listbox = tk.Listbox(frame)
        self.window_names = list(self.windows.keys())
        for name in self.window_names:
            self.window_listbox.insert(tk.END, name)
        self.window_listbox.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(frame, padding=(0, 10, 0, 0))
        button_frame.pack(fill=tk.X)

        ok_button = ttk.Button(button_frame, text="OK", command=self.on_ok, bootstyle=SUCCESS)
        ok_button.pack(side=tk.RIGHT, padx=(5, 0))

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.on_cancel, bootstyle=DANGER)
        cancel_button.pack(side=tk.RIGHT)

    def on_ok(self):
        selection = self.window_listbox.curselection()
        if selection:
            selected_name = self.window_names[selection[0]]
            self.selected_window = self.windows[selected_name]
        self.destroy()

    def on_cancel(self):
        self.selected_window = None
        self.destroy()

if __name__ == '__main__':
    # For testing the dialog
    root = ttk.Window(themename="superhero")
    
    def open_selector():
        dialog = WindowSelector(root)
        root.wait_window(dialog)
        if dialog.selected_window:
            print(f"Selected window ID: {dialog.selected_window}")
        else:
            print("No window selected.")

    ttk.Button(root, text="Open Window Selector", command=open_selector).pack(pady=20)
    root.mainloop()
