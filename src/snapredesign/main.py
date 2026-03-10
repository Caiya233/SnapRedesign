import json
from pathlib import Path
import keyboard
import threading
import time
import queue
import tkinter as tk
import ctypes

from snapredesign.snip_overlay import snip_screen
from snapredesign.comfy_client import ComfyClient
from snapredesign.openai_prompt import generate_prompt
from snapredesign.viewer import show_results
from snapredesign.tray_app import create_icon
from snapredesign.style_ui import choose_style
from snapredesign.style_state import load_style_state, save_style_state


CONFIG_PATH = Path("config.json")
WORKFLOW_PATH = Path("workflow_api.json")
OUTPUT_DIR = Path("outputs")

_app_root = None
_tray_icon = None
_result_queue = queue.Queue()


def enable_dpi_awareness():
    """
    Make Windows use real monitor pixel coordinates so Tk mouse coords
    and Pillow ImageGrab bbox coords line up better.
    Must run before creating any Tk windows.
    """
    try:
        # Per-monitor DPI aware
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # Fallback for older Windows APIs
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


def generate_images_worker(image_path, style):
    try:
        prompt = generate_prompt(preset=style["preset"])
        workflow = load_workflow()
        client = ComfyClient(load_config())

        images = client.run_workflow(
            workflow=workflow,
            input_image=image_path,
            prompt=prompt,
            denoise=style["denoise"],
            seed_lock=style["seed_lock"]
        )

        OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = int(time.time())

        for i, res in enumerate(images):
            save_path = OUTPUT_DIR / f"redesign_{timestamp}_{i}.png"
            res["image"].save(save_path)

        _result_queue.put(("success", image_path, images))

    except Exception as e:
        _result_queue.put(("error", str(e)))


def poll_results():
    global _app_root

    try:
        while True:
            item = _result_queue.get_nowait()

            if item[0] == "success":
                _, image_path, images = item
                show_results(image_path, images, master=_app_root)

            elif item[0] == "error":
                _, error_text = item
                print("Pipeline error:", error_text)

    except queue.Empty:
        pass

    if _app_root is not None and _app_root.winfo_exists():
        _app_root.after(200, poll_results)


def start_pipeline():
    try:
        print("Snip an image...")

        image_path = snip_screen()
        if image_path is None:
            return

        current_style = load_style_state()
        style = choose_style()
        if style is None:
            style = current_style

        save_style_state(style)

        threading.Thread(
            target=generate_images_worker,
            args=(image_path, style),
            daemon=True
        ).start()

    except Exception as e:
        print("Pipeline error:", e)


def shutdown_app():
    global _app_root, _tray_icon

    try:
        if _tray_icon is not None:
            _tray_icon.stop()
    except Exception:
        pass

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
    threading.Thread(target=_tray_icon.run, daemon=True).start()

    poll_results()

    try:
        _app_root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        shutdown_app()


if __name__ == "__main__":
    main()