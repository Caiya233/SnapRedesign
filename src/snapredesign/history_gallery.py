import tkinter as tk
from pathlib import Path
from PIL import Image
import customtkinter as ctk
import json
from tkinter import messagebox

from snapredesign.theme import (
    setup_theme,
    BG, PANEL, PANEL_2, CARD, BORDER, ACCENT, TEXT, MUTED,
    title_font, body_font, mono_font
)


HISTORY_PATH = Path("outputs/history.json")


def draw_hud_panel(canvas, x, y, w, h, cut=18, fill=PANEL, outline=BORDER, width=2, tag="hud"):
    points = [
        x + cut, y,
        x + w, y,
        x + w, y + h - cut,
        x + w - cut, y + h,
        x, y + h,
        x, y + cut
    ]
    canvas.create_polygon(points, fill=fill, outline=outline, width=width, tags=tag)


def draw_scanlines(canvas, width, height, spacing=6, color="#0d1824"):
    canvas.delete("scanline")
    for y in range(0, height, spacing):
        canvas.create_line(0, y, width, y, fill=color, width=1, tags="scanline")


def load_history_metadata():
    if not HISTORY_PATH.exists():
        return {}

    try:
        with open(HISTORY_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}

    if not isinstance(data, list):
        return {}

    metadata = {}
    for entry in data:
        image_name = entry.get("image_name")
        if image_name:
            metadata[image_name] = entry
    return metadata


def open_gallery(master=None):
    output_dir = Path("outputs")
    if not output_dir.exists():
        messagebox.showinfo("SnapRedesign", "No outputs folder found.", parent=master)
        return

    image_files = sorted(
        [f for f in output_dir.iterdir() if f.suffix.lower() in [".png", ".jpg", ".jpeg"]],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    if not image_files:
        messagebox.showinfo("SnapRedesign", "No images found in outputs.", parent=master)
        return

    history_metadata = load_history_metadata()

    setup_theme()

    root = ctk.CTkToplevel(master)
    root.title("SnapRedesign // History Gallery")
    root.geometry("1380x820")
    root.configure(fg_color=BG)

    bg = tk.Canvas(root, bg=BG, highlightthickness=0)
    bg.pack(fill="both", expand=True)

    def redraw(event=None):
        bg.delete("bg")
        w = bg.winfo_width()
        h = bg.winfo_height()
        draw_hud_panel(bg, 16, 16, w - 32, h - 32, cut=26, fill=PANEL, outline=BORDER, width=2, tag="bg")
        draw_scanlines(bg, w, h, spacing=6, color="#0d1824")

    bg.bind("<Configure>", redraw)

    header = ctk.CTkFrame(
        bg,
        fg_color=PANEL_2,
        border_width=2,
        border_color=BORDER,
        corner_radius=18,
        height=90
    )
    header.place(x=32, y=30, relwidth=0.94)

    ctk.CTkLabel(
        header,
        text="HISTORY GALLERY",
        text_color=ACCENT,
        font=title_font(24)
    ).pack(anchor="w", padx=18, pady=(14, 0))

    ctk.CTkLabel(
        header,
        text=f"{len(image_files)} generated images archived",
        text_color=MUTED,
        font=body_font(13)
    ).pack(anchor="w", padx=18, pady=(4, 12))

    ctk.CTkLabel(
        bg,
        text="S\nN\nA\nP",
        text_color=BORDER,
        font=title_font(14),
        justify="center"
    ).place(x=38, y=140)

    details = ctk.CTkFrame(
        bg,
        fg_color=PANEL_2,
        border_width=2,
        border_color=BORDER,
        corner_radius=18
    )
    details.place(relx=0.76, y=138, relwidth=0.21, relheight=0.77)

    gallery = ctk.CTkScrollableFrame(
        bg,
        fg_color=PANEL,
        border_width=2,
        border_color=BORDER,
        corner_radius=18
    )
    gallery.place(x=78, y=138, relwidth=0.63, relheight=0.77)

    ctk.CTkLabel(
        details,
        text="GENERATION DETAILS",
        text_color=ACCENT,
        font=title_font(18)
    ).pack(anchor="w", padx=16, pady=(16, 6))

    details_summary = ctk.CTkLabel(
        details,
        text="Select an output card to inspect its prompt, preset, seed, and score.",
        text_color=MUTED,
        font=body_font(12),
        justify="left",
        wraplength=240
    )
    details_summary.pack(anchor="w", padx=16, pady=(0, 16))

    details_info = ctk.CTkTextbox(
        details,
        width=250,
        height=520,
        fg_color="#0b1220",
        border_width=1,
        border_color="#22324a",
        text_color=TEXT,
        font=body_font(12)
    )
    details_info.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def update_details(img_path, metadata):
        if metadata:
            details_text = (
                f"File: {img_path.name}\n"
                f"Preset: {metadata.get('preset', 'unknown')}\n"
                f"Seed: {metadata.get('seed', 'unknown')}\n"
                f"CLIP score: {metadata.get('score', 'unknown')}\n"
                f"Denoise: {metadata.get('denoise', 'unknown')}\n"
                f"Batch size: {metadata.get('batch_size', 'unknown')}\n"
                f"Seed lock: {metadata.get('seed_lock', 'unknown')}\n"
                f"Prompt ID: {metadata.get('prompt_id', 'unknown')}\n"
                f"Created: {metadata.get('created_at', 'unknown')}\n\n"
                f"Prompt:\n{metadata.get('prompt', '')}\n\n"
                f"Negative:\n{metadata.get('negative_prompt', '')}"
            )
        else:
            details_text = (
                f"File: {img_path.name}\n\n"
                "This image does not have saved metadata.\n"
                "It was likely generated before history tracking was added."
            )

        details_info.configure(state="normal")
        details_info.delete("1.0", "end")
        details_info.insert("1.0", details_text)
        details_info.configure(state="disabled")

    columns = 3
    thumb_size = (210, 210)
    root.image_refs = []

    for index, img_path in enumerate(image_files):
        row = index // columns
        col = index % columns
        metadata = history_metadata.get(img_path.name)

        card = ctk.CTkFrame(
            gallery,
            fg_color=CARD,
            border_width=1,
            border_color="#24324d",
            corner_radius=16
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="n")

        try:
            img = Image.open(img_path).convert("RGB")
            img.thumbnail(thumb_size)

            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            root.image_refs.append(ctk_img)

            img_label = ctk.CTkLabel(card, text="", image=ctk_img)
            img_label.pack(padx=10, pady=(10, 8))

            ctk.CTkLabel(
                card,
                text=img_path.name,
                text_color=TEXT,
                font=body_font(12),
                wraplength=190
            ).pack(padx=10, pady=(0, 4))

            ctk.CTkLabel(
                card,
                text=(
                    f"PRESET  {metadata.get('preset', 'unknown')}\n"
                    f"SEED    {metadata.get('seed', 'unknown')}\n"
                    f"SCORE   {metadata.get('score', 'unknown')}"
                ) if metadata else "LEGACY OUTPUT\nNO METADATA",
                text_color=BORDER,
                font=mono_font(11),
                justify="left"
            ).pack(padx=10, pady=(0, 8))

            ctk.CTkButton(
                card,
                text="View Details",
                command=lambda p=img_path, m=metadata: update_details(p, m),
                fg_color=ACCENT,
                hover_color="#ff4ce0",
                text_color="#06111a",
                width=150
            ).pack(padx=10, pady=(0, 12))

        except Exception as e:
            ctk.CTkLabel(
                card,
                text=f"Error loading:\n{img_path.name}\n{e}",
                text_color="#ff6b6b",
                font=body_font(12)
            ).pack(padx=10, pady=10)

    update_details(image_files[0], history_metadata.get(image_files[0].name))
    redraw()

if __name__ == "__main__":
    open_gallery()
