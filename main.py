import tkinter as tk
import requests
from lib.main_window import MainWindow
from lib.settings_manager import SettingsManager
from lib.version import __version__ as version
from packaging import version as pkg_version

import logging

logging.basicConfig(
    level=logging.CRITICAL,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def check_update_api():
    url = "https://api.github.com/repos/Butzy79/CpFlightFcu/releases/latest"
    try:
        resp = requests.get(url, timeout=3)
        if not resp.ok:
            return False, None
        latest = resp.json().get("tag_name", "").lstrip("v")
        return pkg_version.parse(latest) > pkg_version.parse(version), latest
    except Exception:
        return False, None

def on_close(root, settings, update_available):
    # Save geometry before exit
    extra_param = app.on_stop()
    geo = root.geometry()  # Format: "400x400+100+100"
    parts = geo.split("+")
    size = parts[0].split("x")
    x = int(parts[1])
    y = int(parts[2])
    width = int(size[0])
    height = int(size[1])
    settings.update_window_position(x, y)
    settings.update_window_size(width, height, update_available)
    settings.save_settings(extra_param)
    root.destroy()

if __name__ == "__main__":
    update_available, remote_version = check_update_api()
    settings = SettingsManager()
    root = tk.Tk()
    root.geometry(settings.get_window_geometry(update_available))
    root.resizable(False, False)
    app = MainWindow(
        root,
        version,
        update_available,
        remote_version,
        settings=settings,
        on_close_callback=on_close
    )
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, settings, update_available))
    root.mainloop()