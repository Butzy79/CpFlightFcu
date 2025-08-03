import os
import tkinter as tk
from tkinter import ttk

from lib.aircraft_loader import AircraftLoader
from lib.loop_controller import LoopController

CONFIG_AIRCRAFT_DIR = "config/aircraft"
CONFIG_DIR = "config"

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("CpFlight Control (CFC)")
        self.root.geometry("800x400")
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
        print("Updating status labels", self.loop_controller.sim_status)
        if self.loop_controller.sim_status:
            self.aircraft_ready_label.config(text="Aircraft ready!", foreground="green")
        else:
            self.aircraft_ready_label.config(text="Aircraft NOT ready", foreground="red")

        if self.loop_controller.fcu_status:
            self.fcu_ready_label.config(text="FCU ready!", foreground="green")
        else:
            self.fcu_ready_label.config(text="FCU NOT ready", foreground="red")


    def _build_gui(self):
        # Main layout frames
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame, width=150)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Left Panel - Aircraft selection
        ttk.Label(left_frame, text="Aircraft Config").pack(anchor="w")

        self.file_var = tk.StringVar()
        options = [self._format_filename(f) for f in self.aircraft_files]
        self.file_menu = ttk.Combobox(left_frame, textvariable=self.file_var, values=options, state="readonly", width=20)
        self.file_menu.pack(anchor="w", pady=5)

        self.load_button = ttk.Button(left_frame, text="LOAD", command=self._on_load)
        self.load_button.pack(anchor="w", pady=5)
        # Bind selection change event to re-enable LOAD button
        self.file_menu.bind("<<ComboboxSelected>>", self._on_file_change)

        # Start/Stop Buttons
        self.start_button = ttk.Button(left_frame, text="START", command=self._on_start, state="disabled")
        self.start_button.pack(anchor="w", pady=(20,5))

        self.stop_button = ttk.Button(left_frame, text="STOP", command=self._on_stop, state="disabled")
        self.stop_button.pack(anchor="w", pady=5)

        # FPS selection
        ttk.Label(left_frame, text="Frame per second (s)").pack(anchor="w", pady=(10, 0))
        self.fps_var = tk.StringVar(value="5")
        self.fps_menu = ttk.Combobox(left_frame, textvariable=self.fps_var, values=["0.5", "1", "2", "5", "10", "30", "60"], state="readonly", width=5)
        self.fps_menu.pack(anchor="w")

        # Right Panel - Aircraft data boxes
        # VARS frame
        # Right Panel - Aircraft status display
        self.status_frame = ttk.LabelFrame(right_frame, text="Aircraft Status", width=220, height=300)
        self.status_frame.pack_propagate(False)
        self.status_frame.pack(fill="both", pady=(0, 10))

        self.aircraft_ready_label = ttk.Label(self.status_frame, text="Aircraft NOT ready", foreground="red",
                                              font=("Helvetica", 16, "bold"))
        self.aircraft_ready_label.pack(anchor="center", pady=10)

        self.fcu_ready_label = ttk.Label(self.status_frame, text="FCU NOT ready", foreground="red",
                                         font=("Helvetica", 16, "bold"))
        self.fcu_ready_label.pack(anchor="center", pady=10)


        self.status_bar = ttk.Label(self.root, text="Ready", anchor="w", relief="sunken")
        self.status_bar.pack(side="bottom", fill="x")

        if options:
            self.file_var.set(options[0])
            self._on_load()

    def _schedule_status_update(self):
        self._update_status_labels()
        self.root.after(5000, self._schedule_status_update)

    def _get_interval(self):
        # transform FPS in interval seconds
        try:
            return 1 / float(self.fps_var.get())
        except ValueError:
            return 1.0

    def _on_file_change(self, event):
        # When user changes selection, enable the LOAD button again
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
        self.load_button.config(state="disabled")  # disable after loading

    def _on_start(self):
        if not self.current_config or not self.current_cpflight_config:
            return

        success, msg_err = self.loop_controller.start(self.current_config, self.current_cpflight_config)
        if not success:
            self.status_bar.config(text=msg_err)
            return
        self.status_bar.config(text="Sim connected")

        # Disable controls
        self.file_menu.config(state="disabled")
        self.fps_menu.config(state="disabled")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self._schedule_status_update()

    def _on_stop(self):
        self.loop_controller.stop()
        if hasattr(self, "status_update_job"):
            self.root.after_cancel(self.status_update_job)

        # Enable controls
        self.file_menu.config(state="readonly")
        self.fps_menu.config(state="readonly")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
