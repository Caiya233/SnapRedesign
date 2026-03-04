import tkinter as tk
from PIL import ImageGrab
import tempfile


def snip_screen():

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.3)
    root.configure(bg="black")

    canvas = tk.Canvas(root, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = start_y = 0
    rect = None
    coords = {}

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x = event.x
        start_y = event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y,
                                       outline="red", width=2)

    def on_mouse_drag(event):
        canvas.coords(rect, start_x, start_y, event.x, event.y)

    def on_mouse_up(event):
        coords["x1"] = min(start_x, event.x)
        coords["y1"] = min(start_y, event.y)
        coords["x2"] = max(start_x, event.x)
        coords["y2"] = max(start_y, event.y)
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    root.mainloop()

    if not coords:
        return None

    img = ImageGrab.grab(bbox=(coords["x1"], coords["y1"],
                               coords["x2"], coords["y2"]))

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp.name)

    return temp.name