import threading
from PIL import Image
import pystray
from pystray import MenuItem as item

from snapredesign.main import run_pipeline


def open_outputs(icon, item):
    import os
    os.startfile("outputs")


def run_snip(icon, item):
    threading.Thread(target=run_pipeline).start()


def quit_app(icon, item):
    icon.stop()


def create_icon():

    image = Image.new("RGB", (64, 64), (40, 40, 40))

    menu = pystray.Menu(
        item("Snip + Redesign (Ctrl+Shift+S)", run_snip),
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