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


def apply_responsive_geometry(
    window,
    width_ratio=0.84,
    height_ratio=0.88,
    min_size=(900, 700),
    max_size=None,
):
    screen_width = max(window.winfo_screenwidth(), 640)
    screen_height = max(window.winfo_screenheight(), 480)

    safe_width = max(640, screen_width - 80)
    safe_height = max(480, screen_height - 80)

    target_width = int(screen_width * width_ratio)
    target_height = int(screen_height * height_ratio)

    width = min(max(min_size[0], target_width), safe_width)
    height = min(max(min_size[1], target_height), safe_height)

    if max_size is not None:
        width = min(width, max_size[0])
        height = min(height, max_size[1])

    min_width = min(min_size[0], width)
    min_height = min(min_size[1], height)

    x = max(20, (screen_width - width) // 2)
    y = max(20, (screen_height - height) // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")
    window.minsize(min_width, min_height)

    return width, height


def title_font(size=22):
    return ctk.CTkFont(family="Segoe UI", size=size, weight="bold")


def body_font(size=13):
    return ctk.CTkFont(family="Segoe UI", size=size)


def mono_font(size=12):
    return ctk.CTkFont(family="Consolas", size=size)
