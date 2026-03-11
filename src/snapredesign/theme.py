import customtkinter as ctk

BG = "#060a12"
PANEL = "#0c1320"
PANEL_2 = "#10192a"
CARD = "#121d31"
CARD_ALT = "#16243a"
BORDER = "#19f0ff"
ACCENT = "#ff2bd6"
ACCENT_2 = "#7a5cff"
TEXT = "#ecf7ff"
MUTED = "#7c8aa5"
SUCCESS = "#31ffb3"
WARNING = "#ffd166"
TRACK = "#1a2133"
DIM_BORDER = "#22324a"


def setup_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def title_font(size=22):
    return ctk.CTkFont(family="Segoe UI", size=size, weight="bold")


def body_font(size=13):
    return ctk.CTkFont(family="Segoe UI", size=size)


def mono_font(size=12):
    return ctk.CTkFont(family="Consolas", size=size)


def apply_window_geometry(window, width_ratio=0.9, height_ratio=0.85, min_width=960, min_height=720):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    width = min(max(min_width, int(screen_width * width_ratio)), max(720, screen_width - 80))
    height = min(max(min_height, int(screen_height * height_ratio)), max(540, screen_height - 100))

    x = max(20, (screen_width - width) // 2)
    y = max(20, (screen_height - height) // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")
    window.minsize(min(width, min_width), min(height, min_height))
