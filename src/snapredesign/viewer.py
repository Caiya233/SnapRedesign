import tkinter as tk

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
    ACCENT_2,
    TEXT,
    MUTED,
    SUCCESS,
    TRACK,
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


def pil_to_ctk(img, size):
    image = img.copy()
    image.thumbnail(size)
    return ctk.CTkImage(light_image=image, dark_image=image, size=image.size)


def _result_columns(width):
    if width >= 1400:
        return 3
    if width >= 820:
        return 2
    return 1


def _score_label(score):
    if score >= 0.85:
        return "IDENTITY LOCK"
    if score >= 0.72:
        return "STRONG MATCH"
    if score >= 0.58:
        return "LOOSE MATCH"
    return "HIGH DRIFT"


def _score_color(score):
    if score >= 0.85:
        return SUCCESS
    if score >= 0.72:
        return BORDER
    if score >= 0.58:
        return "#ffb454"
    return "#ff6b7d"


def show_results(original_path, results, master=None):
    setup_theme()

    root = ctk.CTkToplevel(master)
    root.title("SnapRedesign // Results")
    apply_window_geometry(root, width_ratio=0.92, height_ratio=0.9, min_width=1120, min_height=760)
    root.configure(fg_color=BG)
    root.lift()
    root.focus_force()

    canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    shell = ctk.CTkFrame(canvas, fg_color="transparent")
    shell.place(relx=0.03, rely=0.04, relwidth=0.94, relheight=0.92)
    shell.grid_rowconfigure(0, weight=1)
    shell.grid_columnconfigure(0, weight=0)
    shell.grid_columnconfigure(1, weight=1)

    def redraw_bg(event=None):
        canvas.delete("bg")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        draw_hud_panel(canvas, 16, 16, w - 32, h - 32, cut=26, fill=PANEL, outline=BORDER, width=2, tag="bg")
        draw_scanlines(canvas, w, h, spacing=6, color="#0d1824")

    canvas.bind("<Configure>", redraw_bg)

    sorted_results = sorted(results, key=lambda r: r["score"], reverse=True)
    top_score = max((float(res["score"]) for res in sorted_results), default=0.0)

    sidebar = ctk.CTkFrame(
        shell,
        width=320,
        fg_color=PANEL_2,
        border_width=2,
        border_color=BORDER,
        corner_radius=22,
    )
    sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

    main = ctk.CTkFrame(
        shell,
        fg_color="transparent",
    )
    main.grid(row=0, column=1, sticky="nsew")
    main.grid_rowconfigure(1, weight=1)
    main.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        sidebar,
        text="S\nN\nA\nP",
        text_color=BORDER,
        font=title_font(15),
        justify="center",
    ).pack(anchor="w", padx=20, pady=(20, 0))

    ctk.CTkLabel(
        sidebar,
        text="SNAPREDESIGN",
        text_color=ACCENT,
        font=title_font(28),
    ).pack(anchor="w", padx=20, pady=(4, 2))

    ctk.CTkLabel(
        sidebar,
        text="Original capture // ranked redesign set",
        text_color=MUTED,
        font=body_font(13),
    ).pack(anchor="w", padx=20, pady=(0, 14))

    with Image.open(original_path) as opened_original:
        original = opened_original.convert("RGB")
    orig_ctk = pil_to_ctk(original, (280, 280))

    orig_card = ctk.CTkFrame(
        sidebar,
        fg_color=BG,
        border_width=1,
        border_color=DIM_BORDER,
        corner_radius=18,
    )
    orig_card.pack(fill="x", padx=20, pady=(0, 18))

    orig_label = ctk.CTkLabel(orig_card, text="", image=orig_ctk)
    orig_label.image = orig_ctk
    orig_label.pack(padx=14, pady=14)

    stat_row = ctk.CTkFrame(sidebar, fg_color="transparent")
    stat_row.pack(fill="x", padx=20, pady=(0, 16))
    stat_row.grid_columnconfigure(0, weight=1)
    stat_row.grid_columnconfigure(1, weight=1)

    count_card = ctk.CTkFrame(
        stat_row,
        fg_color=CARD_ALT,
        border_width=1,
        border_color=DIM_BORDER,
        corner_radius=16,
    )
    count_card.grid(row=0, column=0, sticky="ew", padx=(0, 6))

    ctk.CTkLabel(
        count_card,
        text="VARIANTS",
        text_color=BORDER,
        font=mono_font(11),
    ).pack(anchor="w", padx=14, pady=(12, 2))
    ctk.CTkLabel(
        count_card,
        text=str(len(sorted_results)),
        text_color=TEXT,
        font=title_font(24),
    ).pack(anchor="w", padx=14, pady=(0, 12))

    score_card = ctk.CTkFrame(
        stat_row,
        fg_color=CARD_ALT,
        border_width=1,
        border_color=DIM_BORDER,
        corner_radius=16,
    )
    score_card.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    ctk.CTkLabel(
        score_card,
        text="TOP SCORE",
        text_color=ACCENT_2,
        font=mono_font(11),
    ).pack(anchor="w", padx=14, pady=(12, 2))
    ctk.CTkLabel(
        score_card,
        text=f"{top_score:.3f}",
        text_color=_score_color(top_score),
        font=title_font(24),
    ).pack(anchor="w", padx=14, pady=(0, 12))

    ctk.CTkLabel(
        sidebar,
        text="HUD NOTES",
        text_color=BORDER,
        font=mono_font(12),
    ).pack(anchor="w", padx=20, pady=(4, 6))

    info = ctk.CTkTextbox(
        sidebar,
        height=160,
        fg_color=BG,
        border_width=1,
        border_color=DIM_BORDER,
        text_color=MUTED,
        font=body_font(12),
    )
    info.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    info.insert(
        "1.0",
        "Results are ranked by CLIP similarity against the source capture.\n\n"
        "Higher scores usually mean the character stayed closer to the original silhouette, face, and overall identity.\n\n"
        "Resize the window freely. The variant grid will reflow automatically.",
    )
    info.configure(state="disabled")

    header = ctk.CTkFrame(
        main,
        fg_color=PANEL_2,
        border_width=2,
        border_color=BORDER,
        corner_radius=22,
    )
    header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        header,
        text="GENERATED VARIANTS",
        text_color=ACCENT,
        font=title_font(28),
    ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))

    ctk.CTkLabel(
        header,
        text="Responsive gallery // identity-ranked redesign outputs",
        text_color=MUTED,
        font=body_font(13),
    ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 18))

    status_badge = ctk.CTkLabel(
        header,
        text=f"TOP MATCH  {_score_label(top_score)}",
        text_color=_score_color(top_score),
        fg_color=BG,
        corner_radius=14,
        padx=14,
        pady=8,
        font=mono_font(11),
    )
    status_badge.grid(row=0, column=1, rowspan=2, sticky="e", padx=20)

    gallery = ctk.CTkScrollableFrame(
        main,
        fg_color=PANEL,
        border_width=2,
        border_color=DIM_BORDER,
        corner_radius=22,
    )
    gallery.grid(row=1, column=0, sticky="nsew")

    root._image_refs = [orig_ctk]
    layout_job = {"id": None}

    def render_cards():
        layout_job["id"] = None

        if not gallery.winfo_exists():
            return

        available_width = gallery.winfo_width()
        if available_width <= 1:
            root.after(60, render_cards)
            return

        for child in gallery.winfo_children():
            child.destroy()

        columns = _result_columns(available_width)
        for column in range(4):
            gallery.grid_columnconfigure(column, weight=0, uniform="")
        for column in range(columns):
            gallery.grid_columnconfigure(column, weight=1, uniform="result")

        gap = 14
        card_width = max(260, (available_width - (gap * (columns + 1))) // columns)
        image_size = (card_width - 34, max(190, int((card_width - 34) * 0.72)))

        root._image_refs = [orig_ctk]

        for index, res in enumerate(sorted_results):
            row = index // columns
            column = index % columns
            score = float(res["score"])
            card = ctk.CTkFrame(
                gallery,
                fg_color=CARD,
                border_width=2,
                border_color=ACCENT if index == 0 else DIM_BORDER,
                corner_radius=20,
            )
            card.grid(row=row, column=column, sticky="nsew", padx=gap // 2, pady=gap // 2)

            label_row = ctk.CTkFrame(card, fg_color="transparent")
            label_row.pack(fill="x", padx=16, pady=(16, 8))

            ctk.CTkLabel(
                label_row,
                text="TOP MATCH" if index == 0 else f"VARIANT {index + 1}",
                text_color=ACCENT if index == 0 else BORDER,
                font=mono_font(12),
            ).pack(side="left")

            ctk.CTkLabel(
                label_row,
                text=_score_label(score),
                text_color=_score_color(score),
                font=mono_font(11),
            ).pack(side="right")

            image = res["image"].convert("RGB")
            ctk_img = pil_to_ctk(image, image_size)
            root._image_refs.append(ctk_img)

            image_label = ctk.CTkLabel(card, text="", image=ctk_img)
            image_label.image = ctk_img
            image_label.pack(padx=16, pady=(0, 12))

            ctk.CTkLabel(
                card,
                text=f"CLIP SCORE  {score:.3f}",
                text_color=_score_color(score),
                font=title_font(18),
            ).pack(anchor="w", padx=16, pady=(0, 4))

            subtitle = "Best identity-preserving redraw in this batch." if index == 0 else "Alternate redesign candidate."
            ctk.CTkLabel(
                card,
                text=subtitle,
                text_color=MUTED,
                font=body_font(12),
            ).pack(anchor="w", padx=16, pady=(0, 10))

            bar = ctk.CTkProgressBar(
                card,
                progress_color=ACCENT if index == 0 else ACCENT_2,
                fg_color=TRACK,
                height=12,
            )
            bar.pack(fill="x", padx=16, pady=(0, 16))
            bar.set(max(0.0, min(score, 1.0)))

    def schedule_render(event=None):
        if layout_job["id"] is not None:
            root.after_cancel(layout_job["id"])
        layout_job["id"] = root.after(80, render_cards)

    root.bind("<Configure>", redraw_bg)
    main.bind("<Configure>", schedule_render)
    gallery.bind("<Configure>", schedule_render)

    redraw_bg()
    render_cards()
    return root
