import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

class EditEventWindow(ttk.Toplevel):
    def __init__(self, master, event, index, on_save_callback):
        super().__init__(master)
        self.transient(master)

        self.event = event.copy()  # Work on a copy
        self.index = index
        self.on_save = on_save_callback

        self.title(f"Edit Event #{index + 1}")

        self.vars = {}
        self.create_widgets()

        self.wait_visibility() # Ensure the window is fully mapped before grabbing
        self.grab_set()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="15")
        frame.pack(fill=BOTH, expand=True)

        # Create entries for each property in the event
        row = 0
        for key, value in self.event.items():
            ttk.Label(frame, text=f"{key.capitalize()}:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
            
            # Use ttk.StringVar
            var = ttk.StringVar(value=value)
            self.vars[key] = var
            
            entry = ttk.Entry(frame, textvariable=var)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            
            # Disable fields that shouldn't be edited
            if key in ['type']:
                entry.config(state="readonly")
            
            # Disable irrelevant fields based on type
            if self.event['type'] == 'click' and key not in ['type', 'time', 'x', 'y', 'button']:
                 entry.config(state="disabled")
            if self.event['type'] == 'key_press' and key not in ['type', 'time', 'key']:
                 entry.config(state="disabled")

            row += 1
        
        frame.columnconfigure(1, weight=1)

        # --- Buttons ---
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(10, 0))

        save_button = ttk.Button(button_frame, text="Save", command=self.save_and_close, bootstyle=SUCCESS)
        save_button.pack(side=LEFT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy, bootstyle=DANGER)
        cancel_button.pack(side=LEFT, padx=5)

    def save_and_close(self):
        try:
            # Rebuild the event dictionary safely
            updated_event = {'type': self.event['type']}
            
            # All events have a time
            updated_event['time'] = float(self.vars['time'].get())

            if self.event['type'] == 'click':
                updated_event['x'] = int(self.vars['x'].get())
                updated_event['y'] = int(self.vars['y'].get())
                updated_event['button'] = self.vars['button'].get()
            elif self.event['type'] == 'key_press':
                updated_event['key'] = self.vars['key'].get()

            self.on_save(self.index, updated_event)
            self.destroy()

        except ValueError:
            messagebox.showerror("Validation Error", "Invalid input. Please ensure time, x, and y are valid numbers.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)

if __name__ == '__main__':
    # Example usage
    root = ttk.Window(themename="superhero")
    root.title("Main App")

    sample_event = {'time': 0.5, 'type': 'click', 'x': 500, 'y': 500, 'button': 'Button.left', 'key': None}

    def on_event_saved(index, event):
        print(f"Event at index {index} was saved:", event)

    def open_edit_window():
        EditEventWindow(root, sample_event, 0, on_event_saved)

    ttk.Button(root, text="Open Edit Window", command=open_edit_window).pack(pady=20, padx=20)

    root.mainloop()
