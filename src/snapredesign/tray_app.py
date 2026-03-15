import os
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from snapredesign.style_state import save_style_state


def build_icon():
    image = Image.new("RGB", (64, 64), "#0b1020")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((6, 6, 58, 58), radius=10, outline="#1ef2ff", width=3)
    draw.line((18, 44, 30, 20, 45, 20), fill="#ff2bd6", width=5)
    draw.line((19, 45, 44, 45), fill="#7a5cff", width=4)
    draw.line((46, 10, 54, 10), fill="#1ef2ff", width=2)
    draw.line((54, 10, 54, 18), fill="#1ef2ff", width=2)

    return image


def open_outputs(icon, menu_item):
    output_dir = os.path.abspath("outputs")
    os.makedirs(output_dir, exist_ok=True)
    os.startfile(output_dir)


def run_snip(icon, menu_item):
    from snapredesign.main import start_pipeline
    start_pipeline()


def show_history(icon, menu_item):
    from snapredesign.main import _app_root
    from snapredesign.history_gallery import open_gallery
    open_gallery(master=_app_root)


def open_style_window(icon, menu_item):
    from snapredesign.main import _app_root
    from snapredesign.style_ui import choose_style

    style = choose_style(master=_app_root)
    if style is not None:
        save_style_state(style)


def quit_app(icon, menu_item):
    icon.stop()
    from snapredesign.main import _app_root
    if _app_root is not None:
        _app_root.after(0, _app_root.destroy)


def create_icon():
    menu = pystray.Menu(
        item("Snip + Redesign (Ctrl+Shift+S)", run_snip, default=True),
        item("History Gallery", show_history),
        item("Open Outputs", open_outputs),
        item("Open Prompt Lab", open_style_window),
        item("Quit", quit_app),
    )

    return pystray.Icon(
        "SnapRedesign",
        build_icon(),
        "SnapRedesign",
        menu
    )
