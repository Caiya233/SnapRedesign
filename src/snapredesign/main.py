import json
from pathlib import Path
import keyboard
import threading
import time
import queue
import tkinter as tk
import ctypes
from datetime import datetime
from tkinter import messagebox, ttk

from snapredesign.snip_overlay import snip_screen
from snapredesign.comfy_client import ComfyClient
from snapredesign.openai_prompt import build_prompt_from_settings
from snapredesign.viewer import show_results
from snapredesign.tray_app import create_icon
from snapredesign.style_ui import choose_style
from snapredesign.style_state import load_style_state, save_style_state


CONFIG_PATH = Path("config.json")
WORKFLOW_PATH = Path("workflow_api.json")
OUTPUT_DIR = Path("outputs")
HISTORY_PATH = OUTPUT_DIR / "history.json"

_app_root = None
_tray_icon = None
_result_queue = queue.Queue()
_loading_window = None
_loading_progress = None
_generation_in_progress = False


def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_workflow():
    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_history():
    if not HISTORY_PATH.exists():
        return []

    try:
        with open(HISTORY_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    return []


def append_history_entries(entries):
    history = load_history()
    history.extend(entries)

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def show_loading(style):
    global _loading_window, _loading_progress

    hide_loading()

    if _app_root is None or not _app_root.winfo_exists():
        return

    _loading_window = tk.Toplevel(_app_root)
    _loading_window.title("SnapRedesign")
    _loading_window.geometry("420x170")
    _loading_window.resizable(False, False)
    _loading_window.configure(bg="#0b1020")
    _loading_window.attributes("-topmost", True)
    _loading_window.protocol("WM_DELETE_WINDOW", lambda: None)

    title = tk.Label(
        _loading_window,
        text="GENERATING REDESIGN",
        bg="#0b1020",
        fg="#1ef2ff",
        font=("Segoe UI", 16, "bold"),
    )
    title.pack(pady=(20, 10))

    subtitle = tk.Label(
        _loading_window,
        text=(
            f"Preset: {style.get('preset', 'none')}  |  "
            f"Batch: {style.get('batch_size', 1)}  |  "
            f"Denoise: {style.get('denoise', 0.0):.2f}"
        ),
        bg="#0b1020",
        fg="#d7e7ff",
        font=("Segoe UI", 10),
    )
    subtitle.pack(pady=(0, 16))

    _loading_progress = ttk.Progressbar(_loading_window, mode="indeterminate", length=320)
    _loading_progress.pack(pady=(0, 14))
    _loading_progress.start(12)

    hint = tk.Label(
        _loading_window,
        text="SnapRedesign is running the ComfyUI workflow locally.",
        bg="#0b1020",
        fg="#93a4bf",
        font=("Segoe UI", 10),
    )
    hint.pack()

    _loading_window.transient(_app_root)
    _loading_window.grab_set()
    _loading_window.update_idletasks()


def hide_loading():
    global _loading_window, _loading_progress

    try:
        if _loading_progress is not None:
            _loading_progress.stop()
    except Exception:
        pass

    try:
        if _loading_window is not None and _loading_window.winfo_exists():
            _loading_window.grab_release()
            _loading_window.destroy()
    except Exception:
        pass

    _loading_window = None
    _loading_progress = None


def show_pipeline_error(error_text):
    parent = _app_root if _app_root is not None and _app_root.winfo_exists() else None
    messagebox.showerror("SnapRedesign // Generation Failed", error_text, parent=parent)


def generate_images_worker(image_path, style):
    try:
        prompt = build_prompt_from_settings(style)
        workflow = load_workflow()
        client = ComfyClient(load_config())

        images = client.run_workflow(
            workflow=workflow,
            input_image=image_path,
            prompt=prompt,
            denoise=style["denoise"],
            seed_lock=style["seed_lock"],
            batch_size=style["batch_size"]
        )

        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = int(time.time())
        created_at = datetime.now().isoformat(timespec="seconds")
        history_entries = []

        for i, res in enumerate(images):
            save_path = OUTPUT_DIR / f"redesign_{timestamp}_{i}.png"
            res["image"].save(save_path)
            res["save_path"] = str(save_path)

            history_entries.append({
                "image_name": save_path.name,
                "image_path": str(save_path),
                "created_at": created_at,
                "source_image": image_path,
                "preset": prompt.get("preset", style.get("preset", "none")),
                "prompt": prompt.get("prompt", ""),
                "negative_prompt": prompt.get("negative_prompt", ""),
                "seed": res.get("seed"),
                "score": round(float(res.get("score", 0.0)), 4),
                "denoise": float(style["denoise"]),
                "batch_size": int(style["batch_size"]),
                "seed_lock": bool(style["seed_lock"]),
                "prompt_id": res.get("prompt_id"),
            })

        append_history_entries(history_entries)

        _result_queue.put(("success", image_path, images))

    except Exception as e:
        _result_queue.put(("error", str(e)))


def poll_results():
    global _app_root, _generation_in_progress

    try:
        while True:
            item = _result_queue.get_nowait()

            if item[0] == "success":
                _, image_path, images = item
                _generation_in_progress = False
                hide_loading()
                show_results(image_path, images, master=_app_root)

            elif item[0] == "error":
                _, error_text = item
                _generation_in_progress = False
                hide_loading()
                show_pipeline_error(error_text)

    except queue.Empty:
        pass

    if _app_root is not None and _app_root.winfo_exists():
        _app_root.after(200, poll_results)


def start_pipeline():
    global _generation_in_progress

    try:
        if _generation_in_progress:
            messagebox.showinfo("SnapRedesign", "A generation is already running.", parent=_app_root)
            return

        print("Snip an image...")

        image_path = snip_screen()
        if image_path is None:
            return

        current_style = load_style_state()
        style = choose_style(master=_app_root)

        if style is None:
            style = current_style

        save_style_state(style)
        show_loading(style)
        _generation_in_progress = True

        threading.Thread(
            target=generate_images_worker,
            args=(image_path, style),
            daemon=True
        ).start()

    except Exception as e:
        _generation_in_progress = False
        hide_loading()
        show_pipeline_error(str(e))


def shutdown_app():
    global _app_root, _tray_icon, _generation_in_progress

    try:
        if _tray_icon is not None:
            _tray_icon.stop()
    except Exception:
        pass

    hide_loading()
    _generation_in_progress = False

    try:
        if _app_root is not None and _app_root.winfo_exists():
            _app_root.quit()
            _app_root.destroy()
    except Exception:
        pass


def main():
    global _app_root, _tray_icon

    enable_dpi_awareness()

    print("SnapRedesign running")
    print("CTRL+SHIFT+S to snip")
    print("Use tray > Quit to exit cleanly")

    _app_root = tk.Tk()
    _app_root.withdraw()

    keyboard.add_hotkey("ctrl+shift+s", start_pipeline)

    _tray_icon = create_icon()
    _tray_icon.run_detached()

    poll_results()

    try:
        _app_root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        shutdown_app()


if __name__ == "__main__":
    main()
