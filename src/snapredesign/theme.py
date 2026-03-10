import customtkinter as ctk

BG = "#060a12"
PANEL = "#0c1320"
PANEL_2 = "#10192a"
CARD = "#121d31"
BORDER = "#19f0ff"
ACCENT = "#ff2bd6"
ACCENT_2 = "#7a5cff"
TEXT = "#ecf7ff"
MUTED = "#7c8aa5"
SUCCESS = "#31ffb3"
WARNING = "#ffd166"


def setup_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def title_font(size=22):
    return ctk.CTkFont(family="Segoe UI", size=size, weight="bold")


def body_font(size=13):
    return ctk.CTkFont(family="Segoe UI", size=size)


def mono_font(size=12):
    return ctk.CTkFont(family="Consolas", size=size)