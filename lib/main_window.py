import os
import tkinter as tk
from tkinter import ttk
from lib.aircraft_loader import load_aircraft_config
from lib.loop_controller import LoopController

CONFIG_DIR = "config/aircraft"

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("CpFlight Control (CFC)")
        self.root.geometry("800x400")
        self.root.resizable(False, False)

        self.current_config = None
        self.aircraft_files = self._scan_aircraft_files()

        self.loop_controller = LoopController(self._get_interval)

        self._build_gui()

    def _scan_aircraft_files(self):
        return [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]

    def _format_filename(self, filename):
        return filename.replace("_", " ").replace(".json", "")

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
        self.fps_var = tk.StringVar(value="10")
        self.fps_menu = ttk.Combobox(left_frame, textvariable=self.fps_var, values=["0.5", "1", "5", "10", "30", "60"], state="readonly", width=5)
        self.fps_menu.pack(anchor="w")

        # Right Panel - Aircraft data boxes
        # VARS frame
        aircraft_frame_width = 220
        aircraft_frame_height = 300

        self.vars_frame = ttk.LabelFrame(right_frame, text="Aircraft VARs", width=aircraft_frame_width, height=aircraft_frame_height)
        self.vars_frame.pack_propagate(False)  # Fix size
        self.vars_frame.pack(fill="both", pady=(0, 10))


        self.speed_label_var = ttk.Label(self.vars_frame, text="Speed: N/A")
        self.speed_label_var.pack(anchor="w", padx=5, pady=5)

        # INFO frame (placeholder)
        self.values_frame = ttk.LabelFrame(right_frame, text="Aircraft VALUES", width=aircraft_frame_width, height=aircraft_frame_height)
        self.values_frame.pack_propagate(False)  # Fix size
        self.values_frame.pack_forget()

        # values labels aircraft
        self.speed_label_val = ttk.Label(self.values_frame, text="Speed: N/A")
        self.speed_label_val.pack(anchor="w", padx=5, pady=5)
        self.heading_label_val = ttk.Label(self.values_frame, text="Heading: N/A")
        self.heading_label_val.pack(anchor="w", padx=5, pady=5)


        if options:
            self.file_var.set(options[0])
            self._on_load()

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

        filepath = os.path.join(CONFIG_DIR, filename)
        self.current_config = load_aircraft_config(filepath)

        tx_val = self.current_config.get("speed", {}).get("tx", None)
        self.speed_label_var.config(text=f"Speed: {tx_val}" if tx_val else "Speed: N/A")

        self.start_button.config(state="normal")
        self.load_button.config(state="disabled")  # disable after loading

    def _on_start(self):
        if not self.current_config:
            return

        self.loop_controller.start()

        # Disable controls
        self.file_menu.config(state="disabled")
        self.fps_menu.config(state="disabled")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        # Show VALUES, hide VARs
        self.vars_frame.pack_forget()
        self.values_frame.pack(fill="both", pady=(0, 10))

    def _on_stop(self):
        self.loop_controller.stop()

        # Enable controls
        self.file_menu.config(state="readonly")
        self.fps_menu.config(state="readonly")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

        # Show VARs, hide VALUES
        self.values_frame.pack_forget()
        self.vars_frame.pack(fill="both", pady=(0, 10))
