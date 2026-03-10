import tkinter as tk
import customtkinter as ctk

from snapredesign.openai_prompt import (
    PRESETS,
    PROMPT_MODES,
    LIGHTING,
    CAMERA,
    COLOR_PALETTES,
    ENVIRONMENTS,
    DETAIL,
    build_prompt_from_settings,
    default_prompt_settings,
)
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


def choose_style(master=None):
    setup_theme()
    defaults = default_prompt_settings()
    saved = load_style_state()
    result = saved.copy()
    confirmed = {"value": False}

    root = ctk.CTkToplevel(master)
    root.title("SnapRedesign // Prompt Lab")
    root.geometry("1080x860")
    root.configure(fg_color=BG)

    root.lift()
    root.focus_force()
    root.grab_set()

    base = tk.Canvas(root, bg=BG, highlightthickness=0)
    base.pack(fill="both", expand=True)

    def redraw_background(event=None):
        base.delete("bg")
        w = base.winfo_width()
        h = base.winfo_height()
        draw_hud_panel(base, 16, 16, w - 32, h - 32, cut=26, fill=PANEL, outline=BORDER, width=2)
        draw_hud_panel(base, 34, 84, w - 68, h - 120, cut=22, fill=PANEL_2, outline="#22324a", width=1)
        draw_scanlines(base, w, h)

        base.create_text(
            58, 36,
            text="SNAPREDESIGN // PROMPT LAB",
            fill=ACCENT,
            font=("Segoe UI", 22, "bold"),
            anchor="nw",
            tags="bg"
        )
        base.create_text(
            60, 68,
            text="preset control // manual prompting // live preview",
            fill=MUTED,
            font=("Segoe UI", 11),
            anchor="nw",
            tags="bg"
        )

    base.bind("<Configure>", redraw_background)

    ctk.CTkLabel(
        base,
        text="S\nN\nA\nP",
        text_color=BORDER,
        font=title_font(15),
        justify="center"
    ).place(x=26, y=120)

    left = ctk.CTkFrame(base, fg_color="transparent", width=470, height=680)
    left.place(x=72, y=110)

    right = ctk.CTkFrame(base, fg_color="transparent", width=470, height=680)
    right.place(x=560, y=110)

    # variables
    mode_var = ctk.StringVar(value=saved.get("mode", defaults["mode"]))
    preset_var = ctk.StringVar(value=saved.get("preset", defaults["preset"]))
    subject_var = ctk.StringVar(value=saved.get("subject", defaults["subject"]))
    lighting_var = ctk.StringVar(value=saved.get("lighting", defaults["lighting"]))
    camera_var = ctk.StringVar(value=saved.get("camera", defaults["camera"]))
    palette_var = ctk.StringVar(value=saved.get("palette", defaults["palette"]))
    environment_var = ctk.StringVar(value=saved.get("environment", defaults["environment"]))
    detail_var = ctk.StringVar(value=saved.get("detail", defaults["detail"]))
    seed_var = ctk.BooleanVar(value=saved.get("seed_lock", defaults["seed_lock"]))

    # left panel
    ctk.CTkLabel(left, text="PROMPT MODE", text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
    mode_menu = ctk.CTkOptionMenu(
        left,
        variable=mode_var,
        values=PROMPT_MODES,
        width=420,
        fg_color="#172033",
        button_color=ACCENT,
        button_hover_color="#ff4ce0",
        dropdown_fg_color="#101726",
        dropdown_hover_color="#1b2740",
        text_color=TEXT
    )
    mode_menu.pack(anchor="w", pady=(0, 16))

    ctk.CTkLabel(left, text="PRESET", text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
    preset_menu = ctk.CTkOptionMenu(
        left,
        variable=preset_var,
        values=list(PRESETS.keys()),
        width=420,
        fg_color="#172033",
        button_color=ACCENT,
        button_hover_color="#ff4ce0",
        dropdown_fg_color="#101726",
        dropdown_hover_color="#1b2740",
        text_color=TEXT
    )
    preset_menu.pack(anchor="w", pady=(0, 16))

    ctk.CTkLabel(left, text="SUBJECT", text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
    subject_entry = ctk.CTkEntry(left, textvariable=subject_var, width=420)
    subject_entry.pack(anchor="w", pady=(0, 16))

    ctk.CTkLabel(left, text="CUSTOM POSITIVE PROMPT", text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
    custom_box = ctk.CTkTextbox(left, width=420, height=140, fg_color="#0b1220", text_color=TEXT)
    custom_box.pack(anchor="w", pady=(0, 16))
    custom_box.insert("1.0", saved.get("custom_prompt", ""))

    ctk.CTkLabel(left, text="NEGATIVE PROMPT", text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
    negative_box = ctk.CTkTextbox(left, width=420, height=110, fg_color="#0b1220", text_color=TEXT)
    negative_box.pack(anchor="w", pady=(0, 16))
    negative_box.insert("1.0", saved.get("negative_prompt", defaults["negative_prompt"]))

    ctk.CTkLabel(left, text="REDESIGN STRENGTH", text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
    redesign_value = ctk.CTkLabel(left, text=f"{saved.get('redesign_strength', defaults['redesign_strength']):.2f}", text_color=TEXT, font=body_font(12))
    redesign_value.pack(anchor="e", pady=(0, 4))

    def on_redesign_change(value):
        redesign_value.configure(text=f"{float(value):.2f}")
        update_preview()

    redesign_slider = ctk.CTkSlider(
        left, from_=0.1, to=1.5, number_of_steps=28,
        progress_color=ACCENT, button_color=BORDER, button_hover_color="#93fbff",
        fg_color="#1a2133", command=on_redesign_change
    )
    redesign_slider.set(float(saved.get("redesign_strength", defaults["redesign_strength"])))
    redesign_slider.pack(fill="x", pady=(0, 16))

    # right panel
    def labeled_menu(parent, label, variable, values):
        ctk.CTkLabel(parent, text=label, text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
        widget = ctk.CTkOptionMenu(
            parent,
            variable=variable,
            values=values,
            width=420,
            fg_color="#172033",
            button_color=ACCENT,
            button_hover_color="#ff4ce0",
            dropdown_fg_color="#101726",
            dropdown_hover_color="#1b2740",
            text_color=TEXT,
            command=lambda _: update_preview()
        )
        widget.pack(anchor="w", pady=(0, 16))
        return widget

    labeled_menu(right, "LIGHTING", lighting_var, LIGHTING)
    labeled_menu(right, "CAMERA", camera_var, CAMERA)
    labeled_menu(right, "COLOR PALETTE", palette_var, COLOR_PALETTES)
    labeled_menu(right, "ENVIRONMENT", environment_var, ENVIRONMENTS)
    labeled_menu(right, "DETAIL LEVEL", detail_var, DETAIL)

    ctk.CTkLabel(right, text="DENOISE", text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
    denoise_value = ctk.CTkLabel(right, text=f"{saved.get('denoise', defaults['denoise']):.2f}", text_color=TEXT, font=body_font(12))
    denoise_value.pack(anchor="e", pady=(0, 4))

    def on_denoise_change(value):
        denoise_value.configure(text=f"{float(value):.2f}")

    denoise_slider = ctk.CTkSlider(
        right, from_=0.2, to=0.95, number_of_steps=15,
        progress_color=ACCENT, button_color=BORDER, button_hover_color="#93fbff",
        fg_color="#1a2133", command=on_denoise_change
    )
    denoise_slider.set(float(saved.get("denoise", defaults["denoise"])))
    denoise_slider.pack(fill="x", pady=(0, 16))

    ctk.CTkLabel(right, text="BATCH SIZE", text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
    batch_value = ctk.CTkLabel(right, text=str(saved.get("batch_size", defaults["batch_size"])), text_color=TEXT, font=body_font(12))
    batch_value.pack(anchor="e", pady=(0, 4))

    def on_batch_change(value):
        batch_value.configure(text=str(int(float(value))))

    batch_slider = ctk.CTkSlider(
        right, from_=1, to=8, number_of_steps=7,
        progress_color=ACCENT, button_color=BORDER, button_hover_color="#93fbff",
        fg_color="#1a2133", command=on_batch_change
    )
    batch_slider.set(int(saved.get("batch_size", defaults["batch_size"])))
    batch_slider.pack(fill="x", pady=(0, 16))

    seed_box = ctk.CTkCheckBox(
        right,
        text="Lock Seed // preserve identity",
        variable=seed_var,
        text_color=TEXT,
        fg_color=ACCENT,
        hover_color="#ff4ce0",
        border_color=BORDER,
        command=lambda: update_preview()
    )
    seed_box.pack(anchor="w", pady=(0, 20))

    ctk.CTkLabel(right, text="FINAL PROMPT PREVIEW", text_color=BORDER, font=mono_font(12)).pack(anchor="w", pady=(0, 6))
    preview_box = ctk.CTkTextbox(right, width=420, height=180, fg_color="#0b1220", text_color=TEXT)
    preview_box.pack(anchor="w", pady=(0, 14))

    def collect_settings():
        return {
            "mode": mode_var.get(),
            "preset": preset_var.get(),
            "subject": subject_var.get().strip(),
            "custom_prompt": custom_box.get("1.0", "end").strip(),
            "negative_prompt": negative_box.get("1.0", "end").strip(),
            "lighting": lighting_var.get(),
            "camera": camera_var.get(),
            "palette": palette_var.get(),
            "environment": environment_var.get(),
            "detail": detail_var.get(),
            "redesign_strength": round(float(redesign_slider.get()), 2),
            "denoise": round(float(denoise_slider.get()), 2),
            "seed_lock": seed_var.get(),
            "batch_size": int(float(batch_slider.get())),
        }

    def update_preview(*_args):
        current = collect_settings()
        built = build_prompt_from_settings(current)
        preview_box.configure(state="normal")
        preview_box.delete("1.0", "end")
        preview_box.insert(
            "1.0",
            f"Positive Prompt:\n{built['prompt']}\n\nNegative Prompt:\n{built['negative_prompt']}"
        )
        preview_box.configure(state="disabled")

    def confirm():
        result.update(collect_settings())
        save_style_state(result)
        confirmed["value"] = True
        root.grab_release()
        root.destroy()

    def reset_defaults():
        mode_var.set(defaults["mode"])
        preset_var.set(defaults["preset"])
        subject_var.set(defaults["subject"])
        lighting_var.set(defaults["lighting"])
        camera_var.set(defaults["camera"])
        palette_var.set(defaults["palette"])
        environment_var.set(defaults["environment"])
        detail_var.set(defaults["detail"])
        seed_var.set(defaults["seed_lock"])

        custom_box.delete("1.0", "end")
        negative_box.delete("1.0", "end")
        negative_box.insert("1.0", defaults["negative_prompt"])

        redesign_slider.set(defaults["redesign_strength"])
        denoise_slider.set(defaults["denoise"])
        batch_slider.set(defaults["batch_size"])
        on_redesign_change(defaults["redesign_strength"])
        on_denoise_change(defaults["denoise"])
        on_batch_change(defaults["batch_size"])
        update_preview()

    # live updates
    mode_menu.configure(command=lambda _: update_preview())
    preset_menu.configure(command=lambda _: update_preview())
    subject_entry.bind("<KeyRelease>", update_preview)
    custom_box.bind("<KeyRelease>", update_preview)
    negative_box.bind("<KeyRelease>", update_preview)

    buttons = ctk.CTkFrame(base, fg_color="transparent", width=970, height=50)
    buttons.place(x=72, y=795)

    reset_btn = ctk.CTkButton(
        buttons,
        text="RESET",
        command=reset_defaults,
        width=180,
        height=40,
        fg_color="#1b2740",
        hover_color="#243657",
        text_color=TEXT
    )
    reset_btn.pack(side="left", padx=(0, 12))

    save_btn = ctk.CTkButton(
        buttons,
        text="SAVE + GENERATE",
        command=confirm,
        width=260,
        height=40,
        fg_color=ACCENT,
        hover_color="#ff4ce0",
        text_color="#05070d",
        font=title_font(14)
    )
    save_btn.pack(side="right")

    redraw_background()
    update_preview()

    root.wait_window()
    if confirmed["value"]:
        return result
    return None