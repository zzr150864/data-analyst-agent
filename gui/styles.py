"""ttk styles and color theme for the data analyst GUI."""

import tkinter as tk
from tkinter import ttk

# Color palette
COLORS = {
    "primary": "#4A90D9",
    "primary_dark": "#3A7BC8",
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "bg": "#F5F7FA",
    "bg_card": "#FFFFFF",
    "text": "#2C3E50",
    "text_light": "#7F8C8D",
    "border": "#E0E4E8",
    "accent": "#E8F0FE",
}

FONTS = {
    "heading": ("Microsoft YaHei UI", 14, "bold"),
    "body": ("Microsoft YaHei UI", 10),
    "body_bold": ("Microsoft YaHei UI", 10, "bold"),
    "small": ("Microsoft YaHei UI", 9),
    "code": ("Consolas", 10),
    "title": ("Microsoft YaHei UI", 18, "bold"),
}


def apply_styles(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    style.theme_use("clam")

    # Configure base styles
    style.configure(".", font=FONTS["body"], background=COLORS["bg"])

    # Frame styles
    style.configure("Card.TFrame", background=COLORS["bg_card"], relief="solid",
                    borderwidth=1, bordercolor=COLORS["border"])
    style.configure("Title.TLabel", font=FONTS["title"], foreground=COLORS["text"],
                    background=COLORS["bg"])
    style.configure("Heading.TLabel", font=FONTS["heading"], foreground=COLORS["text"],
                    background=COLORS["bg"])
    style.configure("Body.TLabel", font=FONTS["body"], foreground=COLORS["text"],
                    background=COLORS["bg"])
    style.configure("Small.TLabel", font=FONTS["small"], foreground=COLORS["text_light"],
                    background=COLORS["bg"])

    # Button styles
    style.configure("Primary.TButton", font=FONTS["body_bold"],
                    background=COLORS["primary"], foreground="white",
                    borderwidth=0, padding=(24, 10))
    style.map("Primary.TButton",
              background=[("active", COLORS["primary_dark"]),
                         ("disabled", COLORS["border"])])

    style.configure("Secondary.TButton", font=FONTS["body"],
                    background=COLORS["bg_card"], foreground=COLORS["text"],
                    borderwidth=1, padding=(16, 8))
    style.map("Secondary.TButton",
              background=[("active", COLORS["accent"])])

    # Entry
    style.configure("TEntry", fieldbackground=COLORS["bg_card"],
                    borderwidth=1, relief="solid", padding=8)

    # Notebook (tabs)
    style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", font=FONTS["body_bold"],
                    padding=(20, 10), background=COLORS["bg_card"])
    style.map("TNotebook.Tab",
              background=[("selected", COLORS["primary"])],
              foreground=[("selected", "white")])

    # OptionMenu
    style.configure("TMenubutton", font=FONTS["body"],
                    background=COLORS["bg_card"], padding=(12, 6))

    # Progress bar
    style.configure("TProgressbar", thickness=6, background=COLORS["primary"])

    # Status bar
    style.configure("StatusBar.TFrame", background=COLORS["primary"], height=28)

    return style
