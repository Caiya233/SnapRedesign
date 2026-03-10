import tkinter as tk
import customtkinter as ctk

from snapredesign.openai_prompt import PRESETS
from snapredesign.style_state import load_style_state, save_style_state
from snapredesign.theme import (
    setup_theme,
    BG, PANEL, PANEL_2, BORDER, ACCENT, TEXT, MUTED,
    title_font, body_font, mono_font
)


def draw_hud_panel(canvas, x, y, w, h, cut=18, fill=PANEL, outline=BORDER, width=2):
    points = [
        x + cut, y,
        x + w, y,
        x + w, y + h - cut,
        x + w - cut, y + h,
        x, y + h,
        x, y + cut
    ]
    canvas.create_polygon(points, fill=fill, outline=outline, width=width, smooth=False, tags="bg")


def draw_scanlines(canvas, width, height, spacing=6, color="#0d1824"):
    canvas.delete("scanline")
    for y in range(0, height, spacing):
        canvas.create_line(0, y, width, y, fill=color, width=1, tags="scanline")


def choose_style():
    setup_theme()
    saved = load_style_state()
    result = saved.copy()

    root = ctk.CTk()
    root.title("SnapRedesign // Style Console")
    root.geometry("620x500")
    root.resizable(False, False)
    root.configure(fg_color=BG)

    base = tk.Canvas(root, bg=BG, highlightthickness=0)
    base.pack(fill="both", expand=True)

    def redraw_background(event=None):
        base.delete("bg")
        w = base.winfo_width()
        h = base.winfo_height()

        draw_hud_panel(base, 18, 18, w - 36, h - 36, cut=24, fill=PANEL, outline=BORDER, width=2)
        draw_hud_panel(base, 34, 86, w - 68, h - 138, cut=20, fill=PANEL_2, outline="#21324a", width=1)
        draw_scanlines(base, w, h, spacing=6, color="#0d1824")

        base.create_text(
            54, 44,
            text="SNAPREDESIGN",
            fill=ACCENT,
            font=("Segoe UI", 22, "bold"),
            anchor="nw",
            tags="bg"
        )
        base.create_text(
            56, 72,
            text="style control // persistent profile",
            fill=MUTED,
            font=("Segoe UI", 11),
            anchor="nw",
            tags="bg"
        )

    base.bind("<Configure>", redraw_background)

    content = ctk.CTkFrame(base, fg_color="transparent")
    content.place(x=70, y=110, relwidth=0.76, relheight=0.68)

    side = ctk.CTkFrame(base, fg_color="transparent", width=32, height=220)
    side.place(x=28, y=120)

    ctk.CTkLabel(
        side,
        text="S\nN\nA\nP",
        text_color=BORDER,
        font=title_font(16),
        justify="center"
    ).pack()

    ctk.CTkLabel(
        content,
        text="STYLE PRESET",
        text_color=BORDER,
        font=mono_font(12)
    ).pack(anchor="w", pady=(0, 6))

    preset_var = ctk.StringVar(value=saved["preset"])

    preset_menu = ctk.CTkOptionMenu(
        content,
        variable=preset_var,
        values=list(PRESETS.keys()),
        width=380,
        fg_color="#172033",
        button_color=ACCENT,
        button_hover_color="#ff4ce0",
        dropdown_fg_color="#101726",
        dropdown_hover_color="#1b2740",
        text_color="white"
    )
    preset_menu.pack(anchor="w", pady=(0, 18))

    ctk.CTkLabel(
        content,
        text="DENOISE STRENGTH",
        text_color=BORDER,
        font=mono_font(12)
    ).pack(anchor="w", pady=(0, 6))

    denoise_value = ctk.CTkLabel(
        content,
        text=f"{saved['denoise']:.2f}",
        text_color="white",
        font=body_font(13)
    )
    denoise_value.pack(anchor="e", pady=(0, 4))

    def on_slider_change(value):
        denoise_value.configure(text=f"{float(value):.2f}")

    denoise_slider = ctk.CTkSlider(
        content,
        from_=0.2,
        to=0.9,
        number_of_steps=14,
        progress_color=ACCENT,
        button_color=BORDER,
        button_hover_color="#93fbff",
        fg_color="#1a2133",
        command=on_slider_change
    )
    denoise_slider.set(saved["denoise"])
    denoise_slider.pack(fill="x", pady=(0, 18))

    seed_var = ctk.BooleanVar(value=saved["seed_lock"])

    seed_box = ctk.CTkCheckBox(
        content,
        text="Lock Seed // preserve identity",
        variable=seed_var,
        text_color="white",
        fg_color=ACCENT,
        hover_color="#ff4ce0",
        border_color=BORDER
    )
    seed_box.pack(anchor="w", pady=(0, 24))

    info_box = ctk.CTkTextbox(
        content,
        width=420,
        height=90,
        fg_color="#0b1220",
        border_color="#22324a",
        border_width=1,
        text_color=MUTED,
        font=body_font(12)
    )
    info_box.pack(fill="x", pady=(0, 22))
    info_box.insert(
        "1.0",
        "Saved settings are now used by the next redesign run.\n"
        "Tray > Choose Style updates the persistent style profile.\n"
        "Ctrl+Shift+S still opens this window before generation."
    )
    info_box.configure(state="disabled")

    buttons = ctk.CTkFrame(content, fg_color="transparent")
    buttons.pack(fill="x")

    def confirm():
        result["preset"] = preset_var.get()
        result["denoise"] = round(float(denoise_slider.get()), 2)
        result["seed_lock"] = seed_var.get()
        save_style_state(result)
        root.destroy()

    generate_btn = ctk.CTkButton(
        buttons,
        text="SAVE + GENERATE",
        command=confirm,
        height=42,
        fg_color=ACCENT,
        hover_color="#ff4ce0",
        text_color="#05070d",
        font=title_font(14)
    )
    generate_btn.pack(fill="x")

    redraw_background()
    root.mainloop()
    return result