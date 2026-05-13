"""Custom tkinter widgets for the data analyst GUI."""

import os
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import threading
from typing import List
from PIL import Image, ImageTk


class FileSelector(ttk.Frame):
    """File selection row: Entry + Browse button."""

    def __init__(self, parent, on_select=None):
        super().__init__(parent, style="Card.TFrame")
        self.on_select = on_select
        self._var = tk.StringVar()

        ttk.Label(self, text="Data File:", style="Heading.TLabel").pack(
            side=tk.LEFT, padx=(12, 8))

        self.entry = ttk.Entry(self, textvariable=self._var, font=("Consolas", 10),
                               width=60)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), pady=10)

        self.btn = ttk.Button(self, text="Browse...", style="Secondary.TButton",
                              command=self._browse)
        self.btn.pack(side=tk.LEFT, padx=(0, 12), pady=10)

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("Data Files", "*.csv;*.xlsx;*.xls"),
                       ("CSV Files", "*.csv"),
                       ("Excel Files", "*.xlsx;*.xls"),
                       ("All Files", "*.*")],
        )
        if path:
            self._var.set(path)
            if self.on_select:
                self.on_select(path)

    @property
    def path(self) -> str:
        return self._var.get()


class TaskInput(ttk.Frame):
    """Multi-line task description input."""

    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame")

        ttk.Label(self, text="Analysis Task:", style="Heading.TLabel").pack(
            anchor=tk.W, padx=12, pady=(10, 4))

        self.text = tk.Text(self, height=4, wrap=tk.WORD, font=("Microsoft YaHei UI", 10),
                            bg="#FFFFFF", fg="#2C3E50", relief="solid",
                            borderwidth=1, padx=10, pady=8)
        self.text.pack(fill=tk.X, padx=12, pady=(0, 10))

        # Placeholder
        self._placeholder = "Describe what you want to analyze, e.g.: Analyze sales trends by region, identify the most profitable product categories, and create visualization charts"
        self.text.insert("1.0", self._placeholder)
        self.text.bind("<FocusIn>", self._on_focus_in)
        self.text.bind("<FocusOut>", self._on_focus_out)
        self.text.config(fg="#B0B8C1")

    def _on_focus_in(self, event):
        if self.text.get("1.0", "end-1c") == self._placeholder:
            self.text.delete("1.0", tk.END)
            self.text.config(fg="#2C3E50")

    def _on_focus_out(self, event):
        if not self.text.get("1.0", "end-1c").strip():
            self.text.insert("1.0", self._placeholder)
            self.text.config(fg="#B0B8C1")

    @property
    def value(self) -> str:
        text = self.text.get("1.0", "end-1c").strip()
        if text == self._placeholder:
            return ""
        return text


class ConfigBar(ttk.Frame):
    """Chart format + report format selectors."""

    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame")

        ttk.Label(self, text="Chart Format:", style="Body.TLabel").pack(
            side=tk.LEFT, padx=(12, 4), pady=10)
        self.chart_var = tk.StringVar(value="png")
        self.chart_menu = ttk.OptionMenu(
            self, self.chart_var, "png", "png", "html",
            command=lambda _: None,
        )
        self.chart_menu.pack(side=tk.LEFT, padx=(0, 20), pady=10)

        ttk.Label(self, text="Report Format:", style="Body.TLabel").pack(
            side=tk.LEFT, padx=(0, 4), pady=10)
        self.report_var = tk.StringVar(value="both")
        self.report_menu = ttk.OptionMenu(
            self, self.report_var, "both", "both", "md", "html",
            command=lambda _: None,
        )
        self.report_menu.pack(side=tk.LEFT, padx=(0, 12), pady=10)

    @property
    def chart_format(self) -> str:
        return self.chart_var.get()

    @property
    def report_format(self) -> str:
        return self.report_var.get()


class OutputNotebook(ttk.Frame):
    """Tabbed output panel: Log / Report / Charts."""

    def __init__(self, parent):
        super().__init__(parent)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Tab 1: Log
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="  Log  ")
        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD, font=("Consolas", 9),
                                bg="#1E1E2E", fg="#CDD6F4", relief="flat",
                                borderwidth=0, padx=12, pady=8, state=tk.DISABLED)
        log_scroll = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._log_tags()

        # Tab 2: Report
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="  Report  ")
        self.report_text = tk.Text(self.report_frame, wrap=tk.WORD,
                                   font=("Microsoft YaHei UI", 10),
                                   bg="#FFFFFF", fg="#2C3E50",
                                   relief="flat", borderwidth=0,
                                   padx=16, pady=12, state=tk.DISABLED)
        report_scroll = ttk.Scrollbar(self.report_frame, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scroll.set)
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        report_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Tab 3: Charts
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="  Charts  ")
        self.chart_canvas = tk.Canvas(self.chart_frame, bg="#F5F7FA",
                                      highlightthickness=0)
        chart_scroll_v = ttk.Scrollbar(self.chart_frame, orient=tk.VERTICAL,
                                       command=self.chart_canvas.yview)
        chart_scroll_h = ttk.Scrollbar(self.chart_frame, orient=tk.HORIZONTAL,
                                       command=self.chart_canvas.xview)
        self.chart_canvas.configure(
            yscrollcommand=chart_scroll_v.set,
            xscrollcommand=chart_scroll_h.set,
        )
        self.chart_inner = ttk.Frame(self.chart_canvas)
        self.chart_canvas_window = self.chart_canvas.create_window(
            (0, 0), window=self.chart_inner, anchor=tk.NW)

        self.chart_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chart_scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        chart_scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

        self.chart_inner.bind("<Configure>", self._on_inner_configure)
        self._thumbnails: List[ImageTk.PhotoImage] = []

    def _log_tags(self):
        self.log_text.tag_configure("timestamp", foreground="#A6ADC8")
        self.log_text.tag_configure("error", foreground="#F38BA8")
        self.log_text.tag_configure("success", foreground="#A6E3A1")

    def _on_inner_configure(self, event):
        self.chart_canvas.configure(scrollregion=self.chart_canvas.bbox("all"))

    def append_log(self, text: str):
        self.log_text.configure(state=tk.NORMAL)
        ts = datetime.now().strftime("[%H:%M:%S] ")
        self.log_text.insert(tk.END, ts, "timestamp")
        tag = None
        if text.startswith("ERROR"):
            tag = "error"
        elif "finished" in text.lower() or "complete" in text.lower():
            tag = "success"
        self.log_text.insert(tk.END, text + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def set_report(self, text: str):
        self.report_text.configure(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert("1.0", text)
        self.report_text.configure(state=tk.DISABLED)
        self.notebook.select(1)  # switch to Report tab

    def load_charts(self, chart_paths: List[str]):
        # Clear existing
        for child in self.chart_inner.winfo_children():
            child.destroy()
        self._thumbnails.clear()

        if not chart_paths:
            lbl = ttk.Label(self.chart_inner, text="No charts generated yet.",
                           style="Body.TLabel")
            lbl.pack(padx=20, pady=40)
            return

        row = 0
        col = 0
        max_cols = 3
        for path in chart_paths:
            if not path.lower().endswith(".png"):
                continue
            try:
                img = Image.open(path)
                img.thumbnail((320, 240), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self._thumbnails.append(photo)

                card = ttk.Frame(self.chart_inner, style="Card.TFrame")
                card.grid(row=row, column=col, padx=8, pady=8, sticky=tk.NSEW)

                lbl_img = ttk.Label(card, image=photo)
                lbl_img.pack(padx=4, pady=(4, 2))

                fname = os.path.basename(path)
                name_lbl = tk.Label(card, text=fname, font=("Microsoft YaHei UI", 9),
                                   fg="#7F8C8D", bg="#FFFFFF", cursor="hand2")
                name_lbl.pack(padx=4, pady=(0, 4))

                # Click to open
                name_lbl.bind("<Button-1>", lambda e, p=path: os.startfile(p))
                lbl_img.bind("<Button-1>", lambda e, p=path: os.startfile(p))

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            except Exception as e:
                lbl = ttk.Label(self.chart_inner,
                               text=f"Error loading {os.path.basename(path)}: {e}",
                               style="Small.TLabel")
                lbl.grid(row=row, column=col, padx=8, pady=8)

        self.notebook.select(2)  # switch to Charts tab


class StatusBar(ttk.Frame):
    """Bottom status bar with progress and text."""

    def __init__(self, parent):
        super().__init__(parent, style="StatusBar.TFrame")

        self.label = tk.Label(self, text="Ready", font=("Microsoft YaHei UI", 9),
                              fg="#FFFFFF", bg=COLORS["primary"])
        self.label.pack(side=tk.LEFT, padx=16, pady=4)

        self.progress = ttk.Progressbar(self, mode="determinate", length=200)
        self.progress.pack(side=tk.RIGHT, padx=16, pady=6)

    def set_status(self, text: str):
        self.label.config(text=text)

    def set_progress(self, value: int):
        self.progress["value"] = value


# Re-import for StatusBar
from gui.styles import COLORS
