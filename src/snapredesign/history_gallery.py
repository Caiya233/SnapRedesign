import tkinter as tk
from pathlib import Path
from PIL import Image
import customtkinter as ctk
import json
from tkinter import messagebox

from snapredesign.theme import (
    apply_responsive_geometry,
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

GALLERY_THUMB_SIZE = 190
GALLERY_WRAP_LENGTH = 190


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
    apply_responsive_geometry(
        root,
        width_ratio=0.9,
        height_ratio=0.88,
        min_size=(980, 700),
        max_size=(1600, 1080),
    )
    root.configure(fg_color=BG)

    bg = tk.Canvas(root, bg=BG, highlightthickness=0)
    bg.pack(fill="both", expand=True)

    redraw_job = {"id": None}

    def redraw():
        redraw_job["id"] = None
        bg.delete("bg")
        w = bg.winfo_width()
        h = bg.winfo_height()
        draw_hud_panel(bg, 16, 16, w - 32, h - 32, cut=26, fill=PANEL, outline=BORDER, width=2, tag="bg")
        draw_scanlines(bg, w, h, spacing=8, color="#0d1824")

    def schedule_redraw(_event=None):
        if redraw_job["id"] is not None:
            root.after_cancel(redraw_job["id"])
        redraw_job["id"] = root.after(50, redraw)

    bg.bind("<Configure>", schedule_redraw)

    layout = ctk.CTkFrame(bg, fg_color="transparent")
    layout.place(relx=0.03, rely=0.04, relwidth=0.94, relheight=0.9)
    layout.grid_columnconfigure(0, weight=68)
    layout.grid_columnconfigure(1, weight=32, minsize=280)
    layout.grid_rowconfigure(1, weight=1)

    header = ctk.CTkFrame(
        layout,
        fg_color=PANEL_2,
        border_width=2,
        border_color=BORDER,
        corner_radius=18,
        height=90
    )
    header.grid(row=0, column=0, columnspan=2, sticky="ew")
    header.grid_columnconfigure(0, weight=0)
    header.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        header,
        text="S\nN\nA\nP",
        text_color=BORDER,
        font=title_font(14),
        justify="center"
    ).grid(row=0, column=0, rowspan=2, sticky="nw", padx=(18, 10), pady=(14, 12))

    ctk.CTkLabel(
        header,
        text="HISTORY GALLERY",
        text_color=ACCENT,
        font=title_font(24)
    ).grid(row=0, column=1, sticky="w", padx=(0, 18), pady=(14, 0))

    ctk.CTkLabel(
        header,
        text=f"{len(image_files)} generated images archived",
        text_color=MUTED,
        font=body_font(13)
    ).grid(row=1, column=1, sticky="w", padx=(0, 18), pady=(4, 12))

    details = ctk.CTkFrame(
        layout,
        fg_color=PANEL_2,
        border_width=2,
        border_color=BORDER,
        corner_radius=18
    )
    details.grid(row=1, column=1, sticky="nsew", pady=(18, 0))
    details.grid_columnconfigure(0, weight=1)
    details.grid_rowconfigure(2, weight=1)

    gallery = ctk.CTkScrollableFrame(
        layout,
        fg_color=PANEL,
        border_width=2,
        border_color=BORDER,
        corner_radius=18
    )
    gallery.grid(row=1, column=0, sticky="nsew", padx=(0, 18), pady=(18, 0))

    ctk.CTkLabel(
        details,
        text="GENERATION DETAILS",
        text_color=ACCENT,
        font=title_font(18)
    ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 6))

    details_summary = ctk.CTkLabel(
        details,
        text="Select an output card to inspect its prompt, preset, seed, and score.",
        text_color=MUTED,
        font=body_font(12),
        justify="left",
        wraplength=240
    )
    details_summary.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))

    details_info = ctk.CTkTextbox(
        details,
        fg_color="#0b1220",
        border_width=1,
        border_color="#22324a",
        text_color=TEXT,
        font=body_font(12)
    )
    details_info.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))

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

    root.image_refs = []
    gallery_cards = []
    resize_job = {"id": None}
    gallery_layout_state = {"columns": None}
    source_image_cache = {}
    thumb_cache = {}

    def refresh_detail_wrap(_event=None):
        details_summary.configure(wraplength=max(details.winfo_width() - 40, 180))

    def get_source_image(img_path):
        cache_key = str(img_path)
        if cache_key not in source_image_cache:
            source_image_cache[cache_key] = Image.open(img_path).convert("RGB")
        return source_image_cache[cache_key]

    def get_thumbnail(img_path):
        cache_key = str(img_path)
        if cache_key not in thumb_cache:
            img = get_source_image(img_path).copy()
            img.thumbnail((GALLERY_THUMB_SIZE, GALLERY_THUMB_SIZE))
            thumb_cache[cache_key] = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        return thumb_cache[cache_key]

    def build_meta_text(metadata):
        if metadata:
            return (
                f"PRESET  {metadata.get('preset', 'unknown')}\n"
                f"SEED    {metadata.get('seed', 'unknown')}\n"
                f"SCORE   {metadata.get('score', 'unknown')}"
            )
        return "LEGACY OUTPUT\nNO METADATA"

    def create_gallery_card(img_path, metadata):
        card = ctk.CTkFrame(
            gallery,
            fg_color=CARD,
            border_width=1,
            border_color="#24324d",
            corner_radius=16
        )
        card.grid_columnconfigure(0, weight=1)

        image_label = ctk.CTkLabel(card, text="")
        image_label.grid(row=0, column=0, padx=10, pady=(10, 8))
        ctk_img = get_thumbnail(img_path)
        image_label.configure(image=ctk_img)
        image_label.image = ctk_img

        name_label = ctk.CTkLabel(
            card,
            text=img_path.name,
            text_color=TEXT,
            font=body_font(12),
            wraplength=GALLERY_WRAP_LENGTH,
        )
        name_label.grid(row=1, column=0, padx=10, pady=(0, 4), sticky="ew")

        meta_label = ctk.CTkLabel(
            card,
            text=build_meta_text(metadata),
            text_color=BORDER,
            font=mono_font(11),
            justify="left"
        )
        meta_label.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="w")

        button = ctk.CTkButton(
            card,
            text="View Details",
            command=lambda p=img_path, m=metadata: update_details(p, m),
            fg_color=ACCENT,
            hover_color="#ff4ce0",
            text_color="#06111a",
        )
        button.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 12))

        return {
            "card": card,
            "ctk_img": ctk_img,
            "image_label": image_label,
            "name_label": name_label,
            "meta_label": meta_label,
            "path": img_path,
            "metadata": metadata,
        }

    def ensure_gallery_cards():
        if gallery_cards:
            return

        root.image_refs = []
        for img_path in image_files:
            metadata = history_metadata.get(img_path.name)
            item = create_gallery_card(img_path, metadata)
            gallery_cards.append(item)
            root.image_refs.append(item["ctk_img"])

    def reflow_gallery_cards(columns):
        for index, item in enumerate(gallery_cards):
            row = index // columns
            column = index % columns
            item["card"].grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        gallery.update_idletasks()

    def render_gallery():
        resize_job["id"] = None

        available_width = gallery.winfo_width()
        if available_width <= 1:
            available_width = max(int(root.winfo_width() * 0.58), 600)

        if available_width < 560:
            columns = 1
        elif available_width < 900:
            columns = 2
        elif available_width < 1240:
            columns = 3
        else:
            columns = 4

        for column in range(4):
            gallery.grid_columnconfigure(column, weight=1 if column < columns else 0)

        ensure_gallery_cards()

        if gallery_layout_state["columns"] == columns:
            return

        gallery_layout_state["columns"] = columns
        reflow_gallery_cards(columns)

    def schedule_gallery_render(_event=None):
        if resize_job["id"] is not None:
            root.after_cancel(resize_job["id"])
        resize_job["id"] = root.after(100, render_gallery)

    update_details(image_files[0], history_metadata.get(image_files[0].name))
    details.bind("<Configure>", refresh_detail_wrap)
    gallery._parent_canvas.bind("<Configure>", schedule_gallery_render, add="+")
    schedule_redraw()
    refresh_detail_wrap()
    schedule_gallery_render()

if __name__ == "__main__":
    open_gallery()
