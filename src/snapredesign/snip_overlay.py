import tkinter as tk
from PIL import ImageGrab
import tempfile


CYAN = "#19f0ff"
MAGENTA = "#ff2bd6"
BG = "black"
HUD_LINE = "#123040"


def snip_screen():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.22)
    root.configure(bg=BG)
    root.title("SnapRedesign Capture")

    canvas = tk.Canvas(
        root,
        bg=BG,
        highlightthickness=0,
        cursor="cross"
    )
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = 0
    start_y = 0
    rect = None
    corner_lines = []
    coords = {}

    def draw_scanlines():
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        for y in range(0, height, 6):
            canvas.create_line(
                0, y, width, y,
                fill=HUD_LINE,
                width=1,
                tags="scanline"
            )

    def draw_hud_text():
        canvas.create_text(
            28, 24,
            anchor="nw",
            text="SNAPREDESIGN // DRAG TO CAPTURE",
            fill=CYAN,
            font=("Consolas", 16, "bold"),
            tags="hud"
        )
        canvas.create_text(
            28, 50,
            anchor="nw",
            text="LMB = select region    ESC = cancel",
            fill=MAGENTA,
            font=("Consolas", 11),
            tags="hud"
        )

        canvas.create_text(
            18, 120,
            anchor="nw",
            text="S\nN\nA\nP",
            fill=CYAN,
            font=("Consolas", 16, "bold"),
            justify="center",
            tags="hud"
        )

    def redraw_background():
        canvas.delete("scanline")
        canvas.delete("hud")
        draw_scanlines()
        draw_hud_text()

    def clear_corner_lines():
        nonlocal corner_lines
        for line_id in corner_lines:
            canvas.delete(line_id)
        corner_lines = []

    def draw_corner_guides(x1, y1, x2, y2):
        nonlocal corner_lines
        clear_corner_lines()

        corner_len = 18

        corner_lines.append(canvas.create_line(x1, y1, x1 + corner_len, y1, fill=CYAN, width=3))
        corner_lines.append(canvas.create_line(x1, y1, x1, y1 + corner_len, fill=CYAN, width=3))

        corner_lines.append(canvas.create_line(x2, y1, x2 - corner_len, y1, fill=CYAN, width=3))
        corner_lines.append(canvas.create_line(x2, y1, x2, y1 + corner_len, fill=CYAN, width=3))

        corner_lines.append(canvas.create_line(x1, y2, x1 + corner_len, y2, fill=CYAN, width=3))
        corner_lines.append(canvas.create_line(x1, y2, x1, y2 - corner_len, fill=CYAN, width=3))

        corner_lines.append(canvas.create_line(x2, y2, x2 - corner_len, y2, fill=CYAN, width=3))
        corner_lines.append(canvas.create_line(x2, y2, x2, y2 - corner_len, fill=CYAN, width=3))

    def update_measurement_label(x1, y1, x2, y2):
        canvas.delete("measure")
        width = max(0, x2 - x1)
        height = max(0, y2 - y1)

        canvas.create_text(
            x1,
            max(20, y1 - 12),
            anchor="sw",
            text=f"{width} x {height}",
            fill=MAGENTA,
            font=("Consolas", 11, "bold"),
            tags="measure"
        )

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect

        start_x = event.x
        start_y = event.y

        canvas.delete("selection")
        canvas.delete("measure")
        clear_corner_lines()

        rect = canvas.create_rectangle(
            start_x,
            start_y,
            start_x,
            start_y,
            outline=MAGENTA,
            width=2,
            dash=(10, 5),
            tags="selection"
        )

    def on_mouse_drag(event):
        if rect is None:
            return

        x1 = min(start_x, event.x)
        y1 = min(start_y, event.y)
        x2 = max(start_x, event.x)
        y2 = max(start_y, event.y)

        canvas.coords(rect, x1, y1, x2, y2)
        draw_corner_guides(x1, y1, x2, y2)
        update_measurement_label(x1, y1, x2, y2)

    def on_mouse_up(event):
        x1 = min(start_x, event.x)
        y1 = min(start_y, event.y)
        x2 = max(start_x, event.x)
        y2 = max(start_y, event.y)

        if abs(x2 - x1) < 2 or abs(y2 - y1) < 2:
            return

        coords["x1"] = x1
        coords["y1"] = y1
        coords["x2"] = x2
        coords["y2"] = y2
        root.destroy()

    def on_escape(event):
        coords.clear()
        root.destroy()

    redraw_background()
    root.update_idletasks()

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    root.bind("<Escape>", on_escape)

    root.mainloop()

    if not coords:
        return None

    img = ImageGrab.grab(
        bbox=(coords["x1"], coords["y1"], coords["x2"], coords["y2"])
    )

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(temp.name)

    return temp.name