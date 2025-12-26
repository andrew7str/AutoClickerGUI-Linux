import json
import os

class SettingsManager:
    def __init__(self, filename="settings.json"):
        self.filepath = filename
        self.default_settings = {
            "theme": "litera",
            "hotkeys": {
                "record": "Key.f1",
                "stop": "Key.f2",
                "play": "Key.f3"
            }
        }

    def load_settings(self):
        """
        Loads settings from the JSON file.
        If the file doesn't exist or is corrupted, returns default settings.
        """
        if not os.path.exists(self.filepath):
            return self.default_settings
        
        try:
            with open(self.filepath, 'r') as f:
                settings = json.load(f)
                # Basic validation to ensure keys exist
                if "hotkeys" not in settings or any(k not in settings["hotkeys"] for k in self.default_settings["hotkeys"]):
                    return self.default_settings
                return settings
        except (json.JSONDecodeError, TypeError):
            return self.default_settings

    def save_settings(self, settings):
        """
        Saves the provided settings dictionary to the JSON file.
        """
        try:
            with open(self.filepath, 'w') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

if __name__ == '__main__':
    # Example usage
    manager = SettingsManager()

    # Load settings
    current_settings = manager.load_settings()
    print(f"Loaded settings: {current_settings}")

    # Modify and save settings
    current_settings["hotkeys"]["record"] = "Key.f5"
    print(f"Saving new settings: {current_settings}")
    manager.save_settings(current_settings)

    # Verify saved settings
    reloaded_settings = manager.load_settings()
    print(f"Re-loaded settings: {reloaded_settings}")

    # Reset to default
    manager.save_settings(manager.default_settings)
    print("Reset settings to default.")
