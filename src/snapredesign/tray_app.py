import threading
from PIL import Image
import pystray
from pystray import MenuItem as item


def open_outputs(icon, item):
    import os
    os.startfile("outputs")


def run_snip(icon, item):
    from snapredesign.main import run_pipeline   # moved import here
    threading.Thread(target=run_pipeline).start()


def show_history(icon, item):
    from snapredesign.history_gallery import open_gallery
    open_gallery()


def open_style_window(icon, item):
    from snapredesign.style_ui import choose_style
    choose_style()


def quit_app(icon, item):
    icon.stop()


def create_icon():

    image = Image.new("RGB", (64, 64), (40, 40, 40))

    menu = pystray.Menu(
        item("Snip + Redesign (Ctrl+Shift+S)", run_snip),
        item("History Gallery", show_history),
        item("Open Outputs", open_outputs),
        item("Choose Style", open_style_window),
        item("Quit", quit_app),
    )

    icon = pystray.Icon(
        "SnapRedesign",
        image,
        "SnapRedesign",
        menu
    )

    return icon