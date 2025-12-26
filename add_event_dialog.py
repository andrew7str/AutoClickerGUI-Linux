import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

class AddEventDialog(ttk.Toplevel):
    def __init__(self, parent, title, event_type):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.wait_visibility() # Ensure the window is fully mapped before grabbing
        self.grab_set()

        self.event_type = event_type
        self.entries = {}
        self.result = None

        master_frame = ttk.Frame(self, padding=15)
        master_frame.pack(fill=BOTH, expand=True)

        self.body(master_frame)
        self.buttonbox(master_frame)

        self.wait_window()

    def body(self, master):
        fields = []
        if self.event_type == 'click':
            fields = [("Time (s)", "0.5"), ("X", "100"), ("Y", "100"), ("Button", "Button.left")]
        elif self.event_type == 'key_press':
            fields = [("Time (s)", "0.2"), ("Key", "a")]

        for i, (label, default_val) in enumerate(fields):
            ttk.Label(master, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(master)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            entry.insert(0, default_val)
            self.entries[label.split(' ')[0].lower()] = entry
        
        master.columnconfigure(1, weight=1)
        return self.entries[fields[0][0].split(' ')[0].lower()]

    def buttonbox(self, master):
        button_frame = ttk.Frame(master, padding=(0, 10, 0, 0))
        button_frame.grid(row=len(self.entries), column=0, columnspan=2, sticky="e")

        ok_button = ttk.Button(button_frame, text="OK", command=self.handle_ok, bootstyle=SUCCESS)
        ok_button.pack(side=LEFT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.handle_cancel, bootstyle=DANGER)
        cancel_button.pack(side=LEFT)

    def handle_ok(self, event=None):
        if not self.validate():
            return
        self.apply()
        self.destroy()

    def handle_cancel(self, event=None):
        self.destroy()

    def validate(self):
        try:
            if self.event_type == 'click':
                float(self.entries['time'].get())
                int(self.entries['x'].get())
                int(self.entries['y'].get())
            elif self.event_type == 'key_press':
                float(self.entries['time'].get())
            return True
        except ValueError:
            messagebox.showwarning("Bad input", "Please check your input values (e.g., time and coordinates must be numbers).", parent=self)
            return False

    def apply(self):
        self.result = {"type": self.event_type}
        if self.event_type == 'click':
            self.result['time'] = float(self.entries['time'].get())
            self.result['x'] = int(self.entries['x'].get())
            self.result['y'] = int(self.entries['y'].get())
            self.result['button'] = self.entries['button'].get()
        elif self.event_type == 'key_press':
            self.result['time'] = float(self.entries['time'].get())
            self.result['key'] = self.entries['key'].get()
