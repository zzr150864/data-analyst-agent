"""Main application window for the Intelligent Data Analyst GUI."""

import os
import sys
import queue
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Handle PyInstaller bundle: files extracted to sys._MEIPASS
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys._MEIPASS)
sys.path.insert(0, str(PROJECT_ROOT))

from gui.styles import apply_styles, COLORS, FONTS
from gui.widgets import FileSelector, TaskInput, ConfigBar, OutputNotebook, StatusBar
from gui.worker import AnalysisWorker
from session import session
from agents.orchestrator import DataAnalystOrchestrator
from utils.file_utils import validate_file_path, ensure_output_dir


class DataAnalystApp(tk.Tk):
    """Main GUI window for the Intelligent Data Analyst."""

    def __init__(self):
        super().__init__()
        self.title("Intelligent Data Analyst - Multi-Agent System")
        self.geometry("1200x820")
        self.minsize(900, 650)
        self.configure(bg=COLORS["bg"])

        # State
        self._worker: Optional[AnalysisWorker] = None
        self._poll_id = None
        self._result_text = ""

        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self._build_ui()
        apply_styles(self)

    def _build_ui(self):
        # --- Title ---
        title_bar = ttk.Frame(self)
        title_bar.pack(fill=tk.X, padx=24, pady=(20, 4))
        ttk.Label(title_bar, text="Intelligent Data Analyst",
                  style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(title_bar, text="Multi-Agent AI System",
                  style="Small.TLabel").pack(side=tk.LEFT, padx=(12, 0))

        # --- File Selector ---
        self.file_selector = FileSelector(self, on_select=self._on_file_selected)
        self.file_selector.pack(fill=tk.X, padx=24, pady=(12, 6))

        # --- Task Input ---
        self.task_input = TaskInput(self)
        self.task_input.pack(fill=tk.X, padx=24, pady=(0, 6))

        # --- Config Bar ---
        self.config_bar = ConfigBar(self)
        self.config_bar.pack(fill=tk.X, padx=24, pady=(0, 8))

        # --- Control Bar ---
        ctrl = ttk.Frame(self)
        ctrl.pack(fill=tk.X, padx=24, pady=(0, 8))

        self.run_btn = ttk.Button(ctrl, text="Start Analysis",
                                  style="Primary.TButton",
                                  command=self._start_analysis)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ttk.Button(ctrl, text="Stop", style="Secondary.TButton",
                                   command=self._stop_analysis,
                                   state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        self.status_bar = StatusBar(ctrl)
        self.status_bar.pack(side=tk.RIGHT)

        # --- Output Notebook ---
        self.output = OutputNotebook(self)
        self.output.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 12))

        # --- Bottom Bar ---
        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, padx=24, pady=(0, 16))

        ttk.Button(bottom, text="Open Outputs Folder", style="Secondary.TButton",
                   command=self._open_outputs).pack(side=tk.LEFT)
        ttk.Button(bottom, text="Clear Session", style="Secondary.TButton",
                   command=self._clear_session).pack(side=tk.LEFT, padx=(8, 0))

        version_lbl = tk.Label(bottom, text="v1.0 | hello-agents",
                              font=("Microsoft YaHei UI", 8),
                              fg=COLORS["text_light"], bg=COLORS["bg"])
        version_lbl.pack(side=tk.RIGHT)

    # ── Event handlers ──────────────────────────────────────────

    def _on_file_selected(self, path: str):
        self.output.append_log(f"File selected: {path}")
        try:
            validate_file_path(path)
        except Exception as e:
            self.output.append_log(f"ERROR: {e}")

    def _start_analysis(self):
        file_path = self.file_selector.path
        task = self.task_input.value

        if not file_path:
            messagebox.showwarning("Missing Input", "Please select a data file.")
            return
        if not task:
            messagebox.showwarning("Missing Input", "Please describe the analysis task.")
            return
        try:
            validate_file_path(file_path)
        except Exception as e:
            messagebox.showerror("Invalid File", str(e))
            return

        # Build full task
        ensure_output_dir()
        session.reset()

        chart_fmt = self.config_bar.chart_format
        report_fmt = (
            "Markdown and HTML" if self.config_bar.report_format == "both"
            else self.config_bar.report_format.upper()
        )
        full_task = (
            f"Analyze the data file at '{file_path}'. "
            f"Step 1: use collect_and_inspect_data with file_path='{file_path}' to load it. "
            f"Step 2: use analyze_data to perform this analysis: {task}. "
            f"Step 3: use create_visualizations to create charts in {chart_fmt} format for: {task}. "
            f"Step 4: use generate_report to produce a {report_fmt} report with all findings. "
        )

        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_bar.set_status("Running...")
        self.status_bar.set_progress(0)
        self.output.append_log(f"Task: {task}")
        self.output.append_log(f"File: {file_path}")

        # Factory creates orchestrator with progress callback in worker thread
        def make_orchestrator(on_progress):
            return DataAnalystOrchestrator(on_progress=on_progress)

        self._worker = AnalysisWorker(make_orchestrator, full_task)
        self._worker.start()
        self._poll_queue()

    def _stop_analysis(self):
        if self._worker:
            self._worker.cancel()
        self._reset_ui()
        self.output.append_log("Analysis stopped.")

    def _poll_queue(self):
        if self._worker is None:
            return

        try:
            while True:
                msg = self._worker.queue.get_nowait()
                self._handle_message(msg)
        except queue.Empty:
            pass

        if self._worker.is_alive():
            self._poll_id = self.after(100, self._poll_queue)
        else:
            # Wait for final completion message
            self._drain_queue()
            if self._worker.is_cancelled():
                self._reset_ui()
            self._worker = None

    def _drain_queue(self):
        """Drain any remaining messages from the worker queue."""
        if self._worker is None:
            return
        try:
            while True:
                msg = self._worker.queue.get_nowait()
                self._handle_message(msg)
        except queue.Empty:
            pass

    def _handle_message(self, msg: dict):
        msg_type = msg.get("type")

        if msg_type == "log":
            self.output.append_log(msg.get("text", ""))

        elif msg_type == "progress":
            self.status_bar.set_progress(msg.get("value", 0))

        elif msg_type == "complete":
            self.status_bar.set_status("Complete")
            self.status_bar.set_progress(100)
            self._result_text = msg.get("result", "")
            self.output.append_log("Analysis complete!")
            self._reset_ui()

            # Load results
            if session.report_paths:
                report_path = session.report_paths[-1]
                try:
                    with open(report_path, "r", encoding="utf-8") as f:
                        self.output.set_report(f.read())
                except Exception:
                    self.output.set_report(self._result_text)

            if session.chart_paths:
                self.output.load_charts(session.chart_paths)

            # Show summary
            self.output.append_log(f"Charts: {len(session.chart_paths)} generated")
            self.output.append_log(f"Reports: {len(session.report_paths)} generated")
            for p in session.chart_paths:
                self.output.append_log(f"  Chart: {p}")
            for p in session.report_paths:
                self.output.append_log(f"  Report: {p}")

        elif msg_type == "error":
            self.output.append_log(f"ERROR: {msg.get('message', 'Unknown')}")
            self.status_bar.set_status("Error")
            self._reset_ui()
            messagebox.showerror("Analysis Error",
                                msg.get("message", "An unknown error occurred."))

    def _reset_ui(self):
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        if self._poll_id:
            self.after_cancel(self._poll_id)
            self._poll_id = None

    def _open_outputs(self):
        output_dir = PROJECT_ROOT / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        os.startfile(str(output_dir))

    def _clear_session(self):
        session.reset()
        self.output.log_text.configure(state=tk.NORMAL)
        self.output.log_text.delete("1.0", tk.END)
        self.output.log_text.configure(state=tk.DISABLED)
        self.output.report_text.configure(state=tk.NORMAL)
        self.output.report_text.delete("1.0", tk.END)
        self.output.report_text.configure(state=tk.DISABLED)
        for child in self.output.chart_inner.winfo_children():
            child.destroy()
        self.output._thumbnails.clear()
        self.status_bar.set_status("Ready")
        self.status_bar.set_progress(0)
        self.output.append_log("Session cleared.")
