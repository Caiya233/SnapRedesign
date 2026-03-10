import json
from pathlib import Path

STYLE_STATE_PATH = Path("ui_state.json")

DEFAULT_STYLE = {
    "preset": "cyberpunk",
    "denoise": 0.6,
    "seed_lock": False
}


def load_style_state():
    if STYLE_STATE_PATH.exists():
        try:
            with open(STYLE_STATE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {
                "preset": data.get("preset", DEFAULT_STYLE["preset"]),
                "denoise": float(data.get("denoise", DEFAULT_STYLE["denoise"])),
                "seed_lock": bool(data.get("seed_lock", DEFAULT_STYLE["seed_lock"]))
            }
        except Exception:
            return DEFAULT_STYLE.copy()

    return DEFAULT_STYLE.copy()


def save_style_state(style):
    payload = {
        "preset": style["preset"],
        "denoise": float(style["denoise"]),
        "seed_lock": bool(style["seed_lock"])
    }

    with open(STYLE_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)