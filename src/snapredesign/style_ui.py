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
    apply_responsive_geometry,
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
    result = defaults.copy()
    result.update(saved)
    confirmed = {"value": False}

    root = ctk.CTkToplevel(master)
    root.title("SnapRedesign // Prompt Lab")
    apply_responsive_geometry(
        root,
        width_ratio=0.84,
        height_ratio=0.9,
        min_size=(920, 700),
        max_size=(1500, 1080),
    )
    root.configure(fg_color=BG)

    root.lift()
    root.focus_force()
    root.grab_set()

    base = tk.Canvas(root, bg=BG, highlightthickness=0)
    base.pack(fill="both", expand=True)

    redraw_job = {"id": None}

    def redraw_background():
        redraw_job["id"] = None
        base.delete("bg")
        w = base.winfo_width()
        h = base.winfo_height()
        draw_hud_panel(base, 16, 16, w - 32, h - 32, cut=26, fill=PANEL, outline=BORDER, width=2)
        draw_hud_panel(base, 34, 84, w - 68, h - 120, cut=22, fill=PANEL_2, outline="#22324a", width=1)
        draw_scanlines(base, w, h, spacing=8)

        base.create_text(
            max(58, int(w * 0.05)), 36,
            text="SNAPREDESIGN // PROMPT LAB",
            fill=ACCENT,
            font=("Segoe UI", 22, "bold"),
            anchor="nw",
            tags="bg"
        )
        base.create_text(
            max(60, int(w * 0.052)), 68,
            text="preset control // manual prompting // live preview",
            fill=MUTED,
            font=("Segoe UI", 11),
            anchor="nw",
            tags="bg"
        )

    def schedule_redraw_background(_event=None):
        if redraw_job["id"] is not None:
            root.after_cancel(redraw_job["id"])
        redraw_job["id"] = root.after(50, redraw_background)

    base.bind("<Configure>", schedule_redraw_background)

    ctk.CTkLabel(
        base,
        text="S\nN\nA\nP",
        text_color=BORDER,
        font=title_font(15),
        justify="center"
    ).place(relx=0.02, rely=0.15, anchor="nw")

    content = ctk.CTkFrame(base, fg_color="transparent")
    content.place(relx=0.07, rely=0.13, relwidth=0.88, relheight=0.7)
    content.grid_columnconfigure(0, weight=1, uniform="prompt-column")
    content.grid_columnconfigure(1, weight=1, uniform="prompt-column")
    content.grid_rowconfigure(0, weight=1)

    scroll_kwargs = {
        "fg_color": "transparent",
        "scrollbar_button_color": "#1b2740",
        "scrollbar_button_hover_color": "#243657",
    }
    left = ctk.CTkScrollableFrame(content, **scroll_kwargs)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
    left.grid_columnconfigure(0, weight=1)

    right = ctk.CTkScrollableFrame(content, **scroll_kwargs)
    right.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
    right.grid_columnconfigure(0, weight=1)

    def add_section_label(parent, row, text):
        ctk.CTkLabel(
            parent,
            text=text,
            text_color=BORDER,
            font=mono_font(12),
        ).grid(row=row, column=0, sticky="w", pady=(0, 6))
        return row + 1

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
    left_row = 0
    left_row = add_section_label(left, left_row, "PROMPT MODE")
    mode_menu = ctk.CTkOptionMenu(
        left,
        variable=mode_var,
        values=PROMPT_MODES,
        fg_color="#172033",
        button_color=ACCENT,
        button_hover_color="#ff4ce0",
        dropdown_fg_color="#101726",
        dropdown_hover_color="#1b2740",
        text_color=TEXT
    )
    mode_menu.grid(row=left_row, column=0, sticky="ew", pady=(0, 16))
    left_row += 1

    left_row = add_section_label(left, left_row, "PRESET")
    preset_menu = ctk.CTkOptionMenu(
        left,
        variable=preset_var,
        values=list(PRESETS.keys()),
        fg_color="#172033",
        button_color=ACCENT,
        button_hover_color="#ff4ce0",
        dropdown_fg_color="#101726",
        dropdown_hover_color="#1b2740",
        text_color=TEXT
    )
    preset_menu.grid(row=left_row, column=0, sticky="ew", pady=(0, 16))
    left_row += 1

    left_row = add_section_label(left, left_row, "SUBJECT")
    subject_entry = ctk.CTkEntry(left, textvariable=subject_var)
    subject_entry.grid(row=left_row, column=0, sticky="ew", pady=(0, 16))
    left_row += 1

    left_row = add_section_label(left, left_row, "CUSTOM POSITIVE PROMPT")
    custom_box = ctk.CTkTextbox(left, height=140, fg_color="#0b1220", text_color=TEXT)
    custom_box.grid(row=left_row, column=0, sticky="ew", pady=(0, 16))
    custom_box.insert("1.0", saved.get("custom_prompt", ""))
    left_row += 1

    left_row = add_section_label(left, left_row, "NEGATIVE PROMPT")
    negative_box = ctk.CTkTextbox(left, height=110, fg_color="#0b1220", text_color=TEXT)
    negative_box.grid(row=left_row, column=0, sticky="ew", pady=(0, 16))
    negative_box.insert("1.0", saved.get("negative_prompt", defaults["negative_prompt"]))
    left_row += 1

    left_row = add_section_label(left, left_row, "REDESIGN STRENGTH")
    redesign_value = ctk.CTkLabel(
        left,
        text=f"{saved.get('redesign_strength', defaults['redesign_strength']):.2f}",
        text_color=TEXT,
        font=body_font(12),
    )
    redesign_value.grid(row=left_row, column=0, sticky="e", pady=(0, 4))
    left_row += 1

    def on_redesign_change(value):
        redesign_value.configure(text=f"{float(value):.2f}")
        update_preview()

    redesign_slider = ctk.CTkSlider(
        left, from_=0.1, to=1.5, number_of_steps=28,
        progress_color=ACCENT, button_color=BORDER, button_hover_color="#93fbff",
        fg_color="#1a2133", command=on_redesign_change
    )
    redesign_slider.set(float(saved.get("redesign_strength", defaults["redesign_strength"])))
    redesign_slider.grid(row=left_row, column=0, sticky="ew", pady=(0, 16))

    # right panel
    def labeled_menu(parent, row, label, variable, values):
        row = add_section_label(parent, row, label)
        widget = ctk.CTkOptionMenu(
            parent,
            variable=variable,
            values=values,
            fg_color="#172033",
            button_color=ACCENT,
            button_hover_color="#ff4ce0",
            dropdown_fg_color="#101726",
            dropdown_hover_color="#1b2740",
            text_color=TEXT,
            command=lambda _: update_preview()
        )
        widget.grid(row=row, column=0, sticky="ew", pady=(0, 16))
        return widget, row + 1

    right_row = 0
    _, right_row = labeled_menu(right, right_row, "LIGHTING", lighting_var, LIGHTING)
    _, right_row = labeled_menu(right, right_row, "CAMERA", camera_var, CAMERA)
    _, right_row = labeled_menu(right, right_row, "COLOR PALETTE", palette_var, COLOR_PALETTES)
    _, right_row = labeled_menu(right, right_row, "ENVIRONMENT", environment_var, ENVIRONMENTS)
    _, right_row = labeled_menu(right, right_row, "DETAIL LEVEL", detail_var, DETAIL)

    right_row = add_section_label(right, right_row, "DENOISE")
    denoise_value = ctk.CTkLabel(
        right,
        text=f"{saved.get('denoise', defaults['denoise']):.2f}",
        text_color=TEXT,
        font=body_font(12),
    )
    denoise_value.grid(row=right_row, column=0, sticky="e", pady=(0, 4))
    right_row += 1

    def on_denoise_change(value):
        denoise_value.configure(text=f"{float(value):.2f}")

    denoise_slider = ctk.CTkSlider(
        right, from_=0.2, to=0.95, number_of_steps=15,
        progress_color=ACCENT, button_color=BORDER, button_hover_color="#93fbff",
        fg_color="#1a2133", command=on_denoise_change
    )
    denoise_slider.set(float(saved.get("denoise", defaults["denoise"])))
    denoise_slider.grid(row=right_row, column=0, sticky="ew", pady=(0, 16))
    right_row += 1

    right_row = add_section_label(right, right_row, "BATCH SIZE")
    batch_value = ctk.CTkLabel(
        right,
        text=str(saved.get("batch_size", defaults["batch_size"])),
        text_color=TEXT,
        font=body_font(12),
    )
    batch_value.grid(row=right_row, column=0, sticky="e", pady=(0, 4))
    right_row += 1

    def on_batch_change(value):
        batch_value.configure(text=str(int(float(value))))

    batch_slider = ctk.CTkSlider(
        right, from_=1, to=8, number_of_steps=7,
        progress_color=ACCENT, button_color=BORDER, button_hover_color="#93fbff",
        fg_color="#1a2133", command=on_batch_change
    )
    batch_slider.set(int(saved.get("batch_size", defaults["batch_size"])))
    batch_slider.grid(row=right_row, column=0, sticky="ew", pady=(0, 16))
    right_row += 1

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
    seed_box.grid(row=right_row, column=0, sticky="w", pady=(0, 20))
    right_row += 1

    right_row = add_section_label(right, right_row, "FINAL PROMPT PREVIEW")
    preview_box = ctk.CTkTextbox(right, height=220, fg_color="#0b1220", text_color=TEXT)
    preview_box.grid(row=right_row, column=0, sticky="ew", pady=(0, 14))

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

    buttons = ctk.CTkFrame(base, fg_color="transparent")
    buttons.place(relx=0.07, rely=0.86, relwidth=0.88, relheight=0.07)
    buttons.grid_columnconfigure(0, weight=1)
    buttons.grid_columnconfigure(1, weight=1)

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
    reset_btn.grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)

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
    save_btn.grid(row=0, column=1, sticky="e", pady=6)

    schedule_redraw_background()
    update_preview()

    root.wait_window()
    if confirmed["value"]:
        return result
    return None
