import json
import os

DEFAULT_SETTINGS = {
    "window": {
        "x": 100,
        "y": 100,
        "width": 400,
        "height": 400
    },
    "autostart": True,
}

SETTINGS_PATH = "settings.json"

class SettingsManager:
    def __init__(self):
        self.settings = self._load_settings()

    def _load_settings(self):
        try:
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
        except Exception:
            return DEFAULT_SETTINGS.copy()
        data.setdefault("autostart", DEFAULT_SETTINGS.get("autostart"))
        return data

    def save_settings(self, extra_params):
        self.settings['autostart'] = extra_params.get("autostart", self.settings['autostart'])
        with open(SETTINGS_PATH, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get_window_geometry(self, update_available:bool=False):
        w = self.settings["window"]["width"]
        h = self.settings["window"]["height"] + 20 if not update_available else self.settings["window"]["height"] + 45
        x = self.settings["window"]["x"]
        y = self.settings["window"]["y"]

        return f"{w}x{h}+{x}+{y}"

    def update_window_position(self, x, y):
        self.settings["window"]["x"] = x
        self.settings["window"]["y"] = y

    def update_window_size(self, width, height, update_available):
        self.settings["window"]["width"] = width
        self.settings["window"]["height"] = height if not update_available else height - 20
