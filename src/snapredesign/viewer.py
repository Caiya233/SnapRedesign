import tkinter as tk
import customtkinter as ctk
from PIL import Image

from snapredesign.theme import (
    apply_responsive_geometry,
    draw_hud_panel,
    draw_scanlines,
    setup_theme,
    BG, PANEL, PANEL_2, CARD, BORDER, ACCENT, TEXT, MUTED, SUCCESS,
    title_font, body_font, mono_font
)

ORIGINAL_PREVIEW_SIZE = (240, 240)
RESULT_PREVIEW_SIZE = (360, 280)


def pil_to_ctk(img, size):
    image = img.copy()
    image.thumbnail(size)
    return ctk.CTkImage(light_image=image, dark_image=image, size=image.size)


def show_results(original_path, results, master=None):
    setup_theme()

    root = ctk.CTkToplevel(master)
    root.title("SnapRedesign // Results")
    apply_responsive_geometry(
        root,
        width_ratio=0.9,
        height_ratio=0.88,
        min_size=(980, 700),
        max_size=(1600, 1080),
    )
    root.configure(fg_color=BG)

    # Keep this window above the hidden root and usable immediately
    root.deiconify()
    root.lift()
    root.focus_force()
    root.attributes("-topmost", True)

    def release_topmost():
        if root.winfo_exists():
            root.attributes("-topmost", False)

    root.after(250, release_topmost)
    root.after_idle(root.lift)
    root.after_idle(root.focus_force)

    canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    redraw_job = {"id": None}

    def redraw_bg():
        redraw_job["id"] = None
        canvas.delete("bg")
        w = canvas.winfo_width()
        h = canvas.winfo_height()

        draw_hud_panel(canvas, 16, 16, w - 32, h - 32, cut=26, fill=PANEL, outline=BORDER, width=2, tag="bg")
        draw_scanlines(canvas, w, h, spacing=8, color="#0d1824")

    def schedule_bg_redraw(_event=None):
        if redraw_job["id"] is not None:
            root.after_cancel(redraw_job["id"])
        redraw_job["id"] = root.after(50, redraw_bg)

    canvas.bind("<Configure>", schedule_bg_redraw)

    layout = ctk.CTkFrame(canvas, fg_color="transparent")
    layout.place(relx=0.03, rely=0.04, relwidth=0.94, relheight=0.9)
    layout.grid_columnconfigure(0, weight=28, minsize=260)
    layout.grid_columnconfigure(1, weight=72)
    layout.grid_rowconfigure(0, weight=1)

    sidebar = ctk.CTkFrame(
        layout,
        fg_color=PANEL_2,
        border_width=2,
        border_color=BORDER,
        corner_radius=18
    )
    sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
    sidebar.grid_columnconfigure(0, weight=1)
    sidebar.grid_rowconfigure(7, weight=1)

    main = ctk.CTkFrame(
        layout,
        fg_color="transparent"
    )
    main.grid(row=0, column=1, sticky="nsew")
    main.grid_columnconfigure(0, weight=1, uniform="result-column")
    main.grid_columnconfigure(1, weight=1, uniform="result-column")
    main.grid_rowconfigure(0, weight=1, uniform="result-row")
    main.grid_rowconfigure(1, weight=1, uniform="result-row")

    ctk.CTkLabel(
        sidebar,
        text="S\nN\nA\nP",
        text_color=BORDER,
        font=title_font(15),
        justify="center"
    ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 0))

    ctk.CTkLabel(
        sidebar,
        text="SNAPREDESIGN",
        text_color=ACCENT,
        font=title_font(24)
    ).grid(row=1, column=0, sticky="w", padx=18, pady=(2, 4))

    ctk.CTkLabel(
        sidebar,
        text="Original image",
        text_color=MUTED,
        font=body_font(12)
    ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 12))

    original = Image.open(original_path).convert("RGB")
    orig_label = ctk.CTkLabel(sidebar, text="")
    orig_label.grid(row=3, column=0, padx=18, pady=(0, 16))

    ctk.CTkLabel(
        sidebar,
        text="RANKING",
        text_color=BORDER,
        font=mono_font(12)
    ).grid(row=4, column=0, sticky="w", padx=18)

    ctk.CTkLabel(
        sidebar,
        text="Sorted by CLIP similarity",
        text_color=TEXT,
        font=body_font(12)
    ).grid(row=5, column=0, sticky="w", padx=18, pady=(2, 14))

    ctk.CTkLabel(
        sidebar,
        text="NOTES",
        text_color=BORDER,
        font=mono_font(12)
    ).grid(row=6, column=0, sticky="w", padx=18, pady=(10, 4))

    info = ctk.CTkTextbox(
        sidebar,
        fg_color="#0b1220",
        border_width=1,
        border_color="#22324a",
        text_color=MUTED,
        font=body_font(12)
    )
    info.grid(row=7, column=0, sticky="nsew", padx=18, pady=(0, 18))
    info.insert(
        "1.0",
        "Higher CLIP similarity usually means the result stayed closer to the source image.\n"
        "The best match is highlighted."
    )
    info.configure(state="disabled")

    sorted_results = sorted(results, key=lambda r: r["score"], reverse=True)
    result_items = []
    orig_ctk = pil_to_ctk(original, ORIGINAL_PREVIEW_SIZE)
    orig_label.configure(image=orig_ctk)
    orig_label.image = orig_ctk
    root._image_refs = [orig_ctk]

    for i, res in enumerate(sorted_results[:4]):
        row, column = divmod(i, 2)

        card = ctk.CTkFrame(
            main,
            fg_color=CARD,
            border_width=2,
            border_color=ACCENT if i == 0 else BORDER,
            corner_radius=18
        )
        card.grid(row=row, column=column, sticky="nsew", padx=12, pady=12)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        tag_text = "BEST MATCH" if i == 0 else f"OPTION {i + 1}"

        ctk.CTkLabel(
            card,
            text=tag_text,
            text_color=ACCENT if i == 0 else BORDER,
            font=mono_font(12)
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        img_label = ctk.CTkLabel(card, text="")
        img_label.grid(row=1, column=0, sticky="n", padx=16, pady=(0, 10))

        score = float(res["score"])

        ctk.CTkLabel(
            card,
            text=f"CLIP SCORE  {score:.3f}",
            text_color=SUCCESS if score >= 0.80 else TEXT,
            font=title_font(16)
        ).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 4))

        bar = ctk.CTkProgressBar(
            card,
            progress_color=ACCENT,
            fg_color="#1a2133",
            height=12
        )
        bar.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 14))
        bar.set(max(0.0, min(score, 1.0)))

        result_items.append({
            "card": card,
            "label": img_label,
            "image": res["image"].convert("RGB"),
        })

    schedule_bg_redraw()

    for item in result_items:
        ctk_img = pil_to_ctk(item["image"], RESULT_PREVIEW_SIZE)
        item["label"].configure(image=ctk_img)
        item["label"].image = ctk_img
        root._image_refs.append(ctk_img)

    return root
