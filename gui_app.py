#!/usr/bin/env python3
"""Intelligent Data Analyst - Desktop GUI Entry Point.

Usage:
    python gui_app.py
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding (skip when running as PyInstaller .exe without console)
if sys.platform == "win32" and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
# Handle PyInstaller bundle
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys._MEIPASS)
sys.path.insert(0, str(PROJECT_ROOT))

from gui.app import DataAnalystApp


def main():
    app = DataAnalystApp()
    app.mainloop()


if __name__ == "__main__":
    main()
