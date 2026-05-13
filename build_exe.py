#!/usr/bin/env python3
"""Build Data Analyst .exe with PyInstaller.

Usage:
    pip install pyinstaller   # Requires network
    python build_exe.py
    # Output: dist/DataAnalyst.exe
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def build():
    spec_path = PROJECT_ROOT / "data-analyst.spec"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(PROJECT_ROOT / "dist"),
        "--workpath", str(PROJECT_ROOT / "build"),
        "--noconfirm",
        "--clean",
    ]

    print(f"Building with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    exe = PROJECT_ROOT / "dist" / "DataAnalyst.exe"
    if exe.exists():
        size_mb = exe.stat().st_size / (1024 * 1024)
        print(f"\nBuild successful: {exe} ({size_mb:.1f} MB)")
    else:
        print("\nBuild may have failed. Check console output.")


if __name__ == "__main__":
    build()
