import json
from pathlib import Path

from snapredesign.openai_prompt import default_prompt_settings, normalize_prompt_mode


STYLE_STATE_PATH = Path("ui_state.json")


def load_style_state():
    defaults = default_prompt_settings()

    if STYLE_STATE_PATH.exists():
        try:
            with open(STYLE_STATE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            merged = defaults.copy()
            merged.update(data)

            merged["redesign_strength"] = float(merged.get("redesign_strength", defaults["redesign_strength"]))
            merged["denoise"] = float(merged.get("denoise", defaults["denoise"]))
            merged["mode"] = normalize_prompt_mode(merged.get("mode", defaults["mode"]))
            merged["seed_lock"] = bool(merged.get("seed_lock", defaults["seed_lock"]))
            merged["batch_size"] = int(merged.get("batch_size", defaults["batch_size"]))

            return merged
        except Exception:
            return defaults.copy()

    return defaults.copy()


def save_style_state(style):
    defaults = default_prompt_settings()
    payload = defaults.copy()
    payload.update(style)

    payload["redesign_strength"] = float(payload["redesign_strength"])
    payload["denoise"] = float(payload["denoise"])
    payload["mode"] = normalize_prompt_mode(payload["mode"])
    payload["seed_lock"] = bool(payload["seed_lock"])
    payload["batch_size"] = int(payload["batch_size"])

    with open(STYLE_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
