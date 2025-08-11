import os
import tkinter as tk
from tkinter import ttk

from lib.aircraft_loader import AircraftLoader
from lib.loop_controller import LoopController

CONFIG_AIRCRAFT_DIR = "config/aircraft"
CONFIG_DIR = "config"

class MainWindow:
    def __init__(self, root, ver):
        self.root = root
        self.version = ver
        self.root.title(f"CpFlight Control (CFC) - {ver}")
        root.iconbitmap("resources/butzy.ico")
        self.root.resizable(False, False)

        self.current_config = None
        self.current_cpflight_config = None

        self.aircraft_files = self._scan_aircraft_files()
        self.aircraft = AircraftLoader()
        self.loop_controller = LoopController(self._get_interval, self.aircraft)

        self._build_gui()

    def _scan_aircraft_files(self):
        return [f for f in os.listdir(CONFIG_AIRCRAFT_DIR) if f.endswith(".json")]

    def _format_filename(self, filename):
        return filename.replace("_", " ").replace(".json", "")

    def _update_status_labels(self):
        if self.loop_controller.sim_status:
            self.aircraft_ready_label.config(text="Aircraft ready!", foreground="green")
        else:
            self.aircraft_ready_label.config(text="Aircraft NOT ready", foreground="red")

        if self.loop_controller.fcu_status:
            self.fcu_ready_label.config(text="FCU ready!", foreground="green")
        else:
            self.fcu_ready_label.config(text="FCU NOT ready", foreground="red")

    def _build_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        main_frame.grid_columnconfigure(0, weight=0)  # Sinistra
        main_frame.grid_columnconfigure(1, weight=1)  # Destra

        left_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        left_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        ttk.Label(left_frame, text="Aircraft Config").grid(row=0, column=0, sticky="w")
        self.file_var = tk.StringVar()
        options = [self._format_filename(f) for f in self.aircraft_files]
        self.file_menu = ttk.Combobox(left_frame, textvariable=self.file_var, values=options, state="readonly", width=20)
        self.file_menu.grid(row=1, column=0, pady=5, sticky="w")

        self.load_button = ttk.Button(left_frame, text="LOAD", command=self._on_load)
        self.load_button.grid(row=2, column=0, pady=(0, 10), sticky="w")
        self.file_menu.bind("<<ComboboxSelected>>", self._on_file_change)

        self.start_button = ttk.Button(left_frame, text="START", command=self._on_start, state="disabled")
        self.start_button.grid(row=3, column=0, pady=(10, 5), sticky="we")

        self.stop_button = ttk.Button(left_frame, text="STOP", command=self._on_stop, state="disabled")
        self.stop_button.grid(row=4, column=0, pady=5, sticky="we")

        # ttk.Label(left_frame, text="Frames per second").grid(row=5, column=0, pady=(15, 0), sticky="w")
        self.fps_var = tk.StringVar(value="5")
        self.fps_menu = ttk.Combobox(left_frame, textvariable=self.fps_var, values=["0.5", "1", "2", "5", "10", "30", "60"], state="readonly", width=5)
        # self.fps_menu.grid(row=6, column=0, pady=5, sticky="w")

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)

        self.status_frame = ttk.LabelFrame(right_frame, text="Aircraft Status", padding=20)
        self.status_frame.grid(row=0, column=0, sticky="nsew")

        self.aircraft_ready_label = ttk.Label(
            self.status_frame,
            text="Aircraft NOT ready",
            foreground="red",
            font=("Helvetica", 18, "bold")
        )
        self.aircraft_ready_label.pack(anchor="center", pady=20)

        self.fcu_ready_label = ttk.Label(
            self.status_frame,
            text="FCU NOT ready",
            foreground="red",
            font=("Helvetica", 18, "bold")
        )
        self.fcu_ready_label.pack(anchor="center", pady=20)

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", anchor="w", relief="sunken", padding=5)
        self.status_bar.grid(row=1, column=0, sticky="we")

        if options:
            self.file_var.set(options[0])
            self._on_load()

    def _schedule_status_update(self):
        self._update_status_labels()
        self.status_update_job = self.root.after(5000, self._schedule_status_update)

    def _get_interval(self):
        try:
            return 1 / float(self.fps_var.get())
        except ValueError:
            return 1.0

    def _on_file_change(self, event):
        self.load_button.config(state="normal")

    def _on_load(self):
        selected = self.file_var.get()
        mapping = {self._format_filename(f): f for f in self.aircraft_files}
        filename = mapping.get(selected)
        if not filename:
            return

        filepath = os.path.join(CONFIG_AIRCRAFT_DIR, filename)
        self.current_config = self.aircraft.load_json_config(filepath)
        filepathcpflight = os.path.join(CONFIG_DIR, "cpflight.json")
        self.current_cpflight_config = self.aircraft.load_json_config(filepathcpflight)

        self.start_button.config(state="normal")
        self.load_button.config(state="disabled")

    def _on_start(self):
        if not self.current_config or not self.current_cpflight_config:
            return

        success, msg_err = self.loop_controller.start(self.current_config, self.current_cpflight_config)
        if not success:
            self.status_bar.config(text=msg_err)
            return
        self.status_bar.config(text="Sim connected")

        self.file_menu.config(state="disabled")
        self.fps_menu.config(state="disabled")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self._schedule_status_update()

    def _on_stop(self):
        self.loop_controller.stop()
        self._update_status_labels()
        if hasattr(self, "status_update_job"):
            self.root.after_cancel(self.status_update_job)

        self.file_menu.config(state="readonly")
        self.fps_menu.config(state="readonly")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
