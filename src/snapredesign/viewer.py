import tkinter as tk
import customtkinter as ctk
from PIL import Image

from snapredesign.theme import (
    setup_theme,
    BG, PANEL, PANEL_2, CARD, BORDER, ACCENT, TEXT, MUTED, SUCCESS,
    title_font, body_font, mono_font
)


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


def pil_to_ctk(img, size):
    image = img.copy()
    image.thumbnail(size)
    return ctk.CTkImage(light_image=image, dark_image=image, size=image.size)


def show_results(original_path, results, master=None):
    setup_theme()

    root = ctk.CTkToplevel(master)
    root.title("SnapRedesign // Results")
    root.geometry("1450x820")
    root.configure(fg_color=BG)

    # Keep this window above the hidden root and usable immediately
    root.lift()
    root.focus_force()

    canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def redraw_bg(event=None):
        canvas.delete("bg")
        w = canvas.winfo_width()
        h = canvas.winfo_height()

        draw_hud_panel(canvas, 16, 16, w - 32, h - 32, cut=26, fill=PANEL, outline=BORDER, width=2, tag="bg")
        draw_scanlines(canvas, w, h, spacing=6, color="#0d1824")

    canvas.bind("<Configure>", redraw_bg)

    sidebar = ctk.CTkFrame(
        canvas,
        width=300,
        fg_color=PANEL_2,
        border_width=2,
        border_color=BORDER,
        corner_radius=18
    )
    sidebar.place(x=34, y=36, relheight=0.9)

    main = ctk.CTkFrame(
        canvas,
        fg_color="transparent"
    )
    main.place(x=352, y=36, relwidth=0.73, relheight=0.9)

    ctk.CTkLabel(
        sidebar,
        text="S\nN\nA\nP",
        text_color=BORDER,
        font=title_font(15),
        justify="center"
    ).pack(anchor="w", padx=18, pady=(18, 0))

    ctk.CTkLabel(
        sidebar,
        text="SNAPREDESIGN",
        text_color=ACCENT,
        font=title_font(24)
    ).pack(anchor="w", padx=18, pady=(2, 4))

    ctk.CTkLabel(
        sidebar,
        text="Original capture // identity source",
        text_color=MUTED,
        font=body_font(12)
    ).pack(anchor="w", padx=18, pady=(0, 12))

    original = Image.open(original_path).convert("RGB")
    orig_preview = original.copy()
    orig_preview.thumbnail((240, 240))
    orig_ctk = pil_to_ctk(orig_preview, (240, 240))

    orig_label = ctk.CTkLabel(sidebar, text="", image=orig_ctk)
    orig_label.image = orig_ctk
    orig_label.pack(padx=18, pady=(0, 16))

    ctk.CTkLabel(
        sidebar,
        text="SORT MODE",
        text_color=BORDER,
        font=mono_font(12)
    ).pack(anchor="w", padx=18)

    ctk.CTkLabel(
        sidebar,
        text="CLIP similarity descending",
        text_color=TEXT,
        font=body_font(12)
    ).pack(anchor="w", padx=18, pady=(2, 14))

    ctk.CTkLabel(
        sidebar,
        text="HUD NOTES",
        text_color=BORDER,
        font=mono_font(12)
    ).pack(anchor="w", padx=18, pady=(10, 4))

    info = ctk.CTkTextbox(
        sidebar,
        width=240,
        height=110,
        fg_color="#0b1220",
        border_width=1,
        border_color="#22324a",
        text_color=MUTED,
        font=body_font(12)
    )
    info.pack(padx=18, pady=(0, 18))
    info.insert(
        "1.0",
        "Higher CLIP score means the redesign stayed closer to the captured character.\n"
        "Top match is highlighted with a stronger accent border."
    )
    info.configure(state="disabled")

    sorted_results = sorted(results, key=lambda r: r["score"], reverse=True)

    card_positions = [
        (0.02, 0.02), (0.51, 0.02),
        (0.02, 0.50), (0.51, 0.50)
    ]

    # keep references alive for the lifetime of this window
    root._image_refs = [orig_ctk]

    for i, res in enumerate(sorted_results[:4]):
        rx, ry = card_positions[i]

        card = ctk.CTkFrame(
            main,
            fg_color=CARD,
            border_width=2,
            border_color=ACCENT if i == 0 else BORDER,
            corner_radius=18
        )
        card.place(relx=rx, rely=ry, relwidth=0.45, relheight=0.42)

        tag_text = "TOP MATCH" if i == 0 else f"VARIANT {i + 1}"

        ctk.CTkLabel(
            card,
            text=tag_text,
            text_color=ACCENT if i == 0 else BORDER,
            font=mono_font(12)
        ).pack(anchor="w", padx=16, pady=(14, 8))

        img = res["image"].convert("RGB")
        img.thumbnail((360, 280))
        ctk_img = pil_to_ctk(img, (360, 280))
        root._image_refs.append(ctk_img)

        img_label = ctk.CTkLabel(card, text="", image=ctk_img)
        img_label.image = ctk_img
        img_label.pack(padx=16, pady=(0, 10))

        score = float(res["score"])

        ctk.CTkLabel(
            card,
            text=f"CLIP SCORE  {score:.3f}",
            text_color=SUCCESS if score >= 0.80 else TEXT,
            font=title_font(16)
        ).pack(anchor="w", padx=16, pady=(0, 4))

        bar = ctk.CTkProgressBar(
            card,
            progress_color=ACCENT,
            fg_color="#1a2133",
            height=12
        )
        bar.pack(fill="x", padx=16, pady=(0, 14))
        bar.set(max(0.0, min(score, 1.0)))

    redraw_bg()
    return root