import tkinter as tk
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from snapredesign.theme import (
    setup_theme,
    apply_window_geometry,
    BG,
    PANEL,
    PANEL_2,
    CARD,
    CARD_ALT,
    BORDER,
    ACCENT,
    TEXT,
    MUTED,
    DIM_BORDER,
    title_font,
    body_font,
    mono_font,
)


def draw_hud_panel(canvas, x, y, w, h, cut=18, fill=PANEL, outline=BORDER, width=2, tag="hud"):
    points = [
        x + cut, y,
        x + w, y,
        x + w, y + h - cut,
        x + w - cut, y + h,
        x, y + h,
        x, y + cut,
    ]
    canvas.create_polygon(points, fill=fill, outline=outline, width=width, tags=tag)


def draw_scanlines(canvas, width, height, spacing=6, color="#0d1824"):
    canvas.delete("scanline")
    for y in range(0, height, spacing):
        canvas.create_line(0, y, width, y, fill=color, width=1, tags="scanline")


def _gallery_columns(width):
    if width >= 1500:
        return 5
    if width >= 1180:
        return 4
    if width >= 860:
        return 3
    return 2


def open_gallery(master=None):
    output_dir = Path("outputs")
    if not output_dir.exists():
        print("No outputs folder found.")
        return

    image_files = sorted(
        [f for f in output_dir.iterdir() if f.suffix.lower() in [".png", ".jpg", ".jpeg"]],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )

    if not image_files:
        print("No images found in outputs.")
        return

    setup_theme()

    root = ctk.CTkToplevel(master)
    root.title("SnapRedesign // History Gallery")
    apply_window_geometry(root, width_ratio=0.9, height_ratio=0.88, min_width=1040, min_height=760)
    root.configure(fg_color=BG)
    root.lift()
    root.focus_force()

    bg = tk.Canvas(root, bg=BG, highlightthickness=0)
    bg.pack(fill="both", expand=True)

    shell = ctk.CTkFrame(bg, fg_color="transparent")
    shell.place(relx=0.03, rely=0.04, relwidth=0.94, relheight=0.92)
    shell.grid_rowconfigure(1, weight=1)
    shell.grid_columnconfigure(0, weight=1)

    def redraw(event=None):
        bg.delete("bg")
        w = bg.winfo_width()
        h = bg.winfo_height()
        draw_hud_panel(bg, 16, 16, w - 32, h - 32, cut=26, fill=PANEL, outline=BORDER, width=2, tag="bg")
        draw_scanlines(bg, w, h, spacing=6, color="#0d1824")

    bg.bind("<Configure>", redraw)

    header = ctk.CTkFrame(
        shell,
        fg_color=PANEL_2,
        border_width=2,
        border_color=BORDER,
        corner_radius=22,
    )
    header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        header,
        text="HISTORY GALLERY",
        text_color=ACCENT,
        font=title_font(28),
    ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))

    ctk.CTkLabel(
        header,
        text=f"{len(image_files)} archived outputs // responsive grid view",
        text_color=MUTED,
        font=body_font(13),
    ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 18))

    summary = ctk.CTkFrame(
        header,
        fg_color=BG,
        border_width=1,
        border_color=DIM_BORDER,
        corner_radius=14,
    )
    summary.grid(row=0, column=1, rowspan=2, sticky="e", padx=20)

    ctk.CTkLabel(
        summary,
        text="ARCHIVE COUNT",
        text_color=BORDER,
        font=mono_font(11),
    ).pack(anchor="w", padx=14, pady=(10, 2))
    ctk.CTkLabel(
        summary,
        text=str(len(image_files)),
        text_color=TEXT,
        font=title_font(22),
    ).pack(anchor="w", padx=14, pady=(0, 10))

    gallery = ctk.CTkScrollableFrame(
        shell,
        fg_color=PANEL,
        border_width=2,
        border_color=DIM_BORDER,
        corner_radius=22,
    )
    gallery.grid(row=1, column=0, sticky="nsew")

    root.image_refs = []
    layout_job = {"id": None}

    def render_gallery():
        layout_job["id"] = None

        if not gallery.winfo_exists():
            return

        available_width = gallery.winfo_width()
        if available_width <= 1:
            root.after(60, render_gallery)
            return

        for child in gallery.winfo_children():
            child.destroy()

        columns = _gallery_columns(available_width)
        for column in range(6):
            gallery.grid_columnconfigure(column, weight=0, uniform="")
        for column in range(columns):
            gallery.grid_columnconfigure(column, weight=1, uniform="gallery")

        gap = 14
        card_width = max(210, (available_width - (gap * (columns + 1))) // columns)
        thumb_size = (card_width - 26, max(160, card_width - 40))

        root.image_refs = []

        for index, img_path in enumerate(image_files):
            row = index // columns
            column = index % columns

            card = ctk.CTkFrame(
                gallery,
                fg_color=CARD if index % 2 == 0 else CARD_ALT,
                border_width=1,
                border_color=DIM_BORDER,
                corner_radius=18,
            )
            card.grid(row=row, column=column, sticky="nsew", padx=gap // 2, pady=gap // 2)

            try:
                stat = img_path.stat()
                captured_at = datetime.fromtimestamp(stat.st_mtime).strftime("%b %d  %H:%M")

                with Image.open(img_path) as opened_image:
                    img = opened_image.convert("RGB")
                img.thumbnail(thumb_size)

                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                root.image_refs.append(ctk_img)

                ctk.CTkLabel(
                    card,
                    text="OUTPUT ARCHIVE",
                    text_color=ACCENT if index == 0 else BORDER,
                    font=mono_font(11),
                ).pack(anchor="w", padx=12, pady=(12, 6))

                img_label = ctk.CTkLabel(card, text="", image=ctk_img)
                img_label.pack(padx=12, pady=(0, 10))

                ctk.CTkLabel(
                    card,
                    text=img_path.name,
                    text_color=TEXT,
                    font=body_font(12),
                    wraplength=max(160, card_width - 30),
                    justify="left",
                ).pack(anchor="w", padx=12, pady=(0, 4))

                ctk.CTkLabel(
                    card,
                    text=f"{max(1, stat.st_size // 1024)} KB  //  {captured_at}",
                    text_color=MUTED,
                    font=body_font(11),
                ).pack(anchor="w", padx=12, pady=(0, 12))

            except Exception as exc:
                ctk.CTkLabel(
                    card,
                    text=f"Error loading:\n{img_path.name}\n{exc}",
                    text_color="#ff6b6b",
                    font=body_font(12),
                    justify="left",
                ).pack(padx=12, pady=12)

    def schedule_render(event=None):
        if layout_job["id"] is not None:
            root.after_cancel(layout_job["id"])
        layout_job["id"] = root.after(80, render_gallery)

    root.bind("<Configure>", redraw)
    gallery.bind("<Configure>", schedule_render)

    redraw()
    render_gallery()
    return root


if __name__ == "__main__":
    open_gallery()
