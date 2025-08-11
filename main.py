import re
import tkinter as tk
from lib.main_window import MainWindow
from lib.settings_manager import SettingsManager

import logging

logging.basicConfig(
    level=logging.CRITICAL,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def get_latest_release_version(changelog_path='CHANGELOG.md'):
    with open(changelog_path, 'r') as file:
        content = file.read()

    versions = re.findall(r'\[\d+\.\d+\.\d+\]', content)

    if not versions:
        return None

    latest_version = versions[0].strip('[]')
    return latest_version

def on_close(root, settings):
    # Save geometry before exit
    app._on_stop()
    geo = root.geometry()  # Format: "400x400+100+100"
    parts = geo.split("+")
    size = parts[0].split("x")
    x = int(parts[1])
    y = int(parts[2])
    width = int(size[0])
    height = int(size[1])
    settings.update_window_position(x, y)
    settings.update_window_size(width, height)
    settings.save_settings()
    root.destroy()

if __name__ == "__main__":
    settings = SettingsManager()
    version = get_latest_release_version()
    root = tk.Tk()
    root.geometry(settings.get_window_geometry())
    root.resizable(False, False)
    app = MainWindow(root, version)
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, settings))
    root.mainloop()