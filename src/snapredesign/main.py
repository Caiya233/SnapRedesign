import json
from pathlib import Path
import keyboard
import threading

from snapredesign.snip_overlay import snip_screen
from snapredesign.comfy_client import ComfyClient
from snapredesign.openai_prompt import generate_prompt
from snapredesign.viewer import show_results
from snapredesign.tray_app import create_icon
from snapredesign.style_ui import choose_style


CONFIG_PATH = Path("config.json")
WORKFLOW_PATH = Path("workflow_api.json")
OUTPUT_DIR = Path("outputs")


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def load_workflow():
    with open(WORKFLOW_PATH) as f:
        return json.load(f)


def run_pipeline():
    try:
        print("Snip an image...")

        image_path = snip_screen()
        if image_path is None:
            return

        style = choose_style()

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

        show_results(image_path, images)

    except Exception as e:
        print("Pipeline error:", e)


def main():

    print("SnapRedesign running")
    print("CTRL+SHIFT+S to snip")

    keyboard.add_hotkey(
        "ctrl+shift+s",
        lambda: threading.Thread(target=run_pipeline).start()
    )

    tray = create_icon()

    tray.run()


if __name__ == "__main__":
    main()