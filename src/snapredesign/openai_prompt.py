import random


# ------------------------------
# STYLE PRESETS
# ------------------------------

PRESETS = {
    "none": [],

    "cyberpunk": [
        "cyberpunk aesthetic",
        "neon lighting",
        "glowing techwear",
        "futuristic street environment"
    ],

    "anime": [
        "anime character design",
        "cel shaded illustration",
        "dynamic action pose",
        "high contrast shading"
    ],

    "comic": [
        "comic book illustration",
        "inked line art",
        "bold colors",
        "graphic novel style"
    ],

    "streetwear": [
        "urban streetwear fashion",
        "modern sneaker culture",
        "stylized character design",
        "contemporary fashion concept"
    ],

    "mma_fighter": [
        "professional MMA fighter",
        "muscular physique",
        "dynamic combat stance",
        "fight arena aesthetic"
    ],

    "dark_fantasy": [
        "dark fantasy warrior",
        "gritty medieval armor",
        "dramatic lighting",
        "epic fantasy concept art"
    ],

    "sci_fi": [
        "futuristic sci-fi armor",
        "advanced technology suit",
        "space age materials",
        "concept art character"
    ],

    "samurai": [
        "modern samurai warrior",
        "traditional armor elements",
        "cinematic atmosphere",
        "stylized martial arts character"
    ],

    "high_fashion": [
        "high fashion editorial",
        "avant garde clothing",
        "runway aesthetic",
        "luxury fashion photography"
    ],

    "game_character": [
        "video game character design",
        "AAA game concept art",
        "stylized hero design",
        "dynamic character pose"
    ],

    "retro_arcade": [
        "retro arcade fighter aesthetic",
        "90s fighting game character",
        "vibrant arcade colors",
        "classic game character design"
    ],

    "industrial": [
        "brutalist industrial aesthetic",
        "heavy mechanical elements",
        "dark metal textures",
        "post industrial design"
    ],

    "punk": [
        "punk fashion aesthetic",
        "rebellious character design",
        "grunge style clothing",
        "urban dystopian vibe"
    ],

    "military": [
        "tactical military gear",
        "special forces equipment",
        "combat ready character",
        "modern warfare aesthetic"
    ],

    "fantasy_hero": [
        "epic fantasy hero",
        "heroic character design",
        "mythic armor",
        "high fantasy concept art"
    ]
}


# ------------------------------
# CONTROL OPTIONS
# ------------------------------

PROMPT_MODES = [
    "preset_only",
    "manual_only",
    "preset_plus_manual",
    "randomized"
]

LIGHTING = [
    "random",
    "dramatic cinematic lighting",
    "neon rim lighting",
    "soft studio lighting",
    "moody noir lighting",
    "golden hour lighting",
    "high contrast lighting",
]

CAMERA = [
    "random",
    "low angle hero shot",
    "three quarter character view",
    "dynamic action angle",
    "top down stylized angle",
    "cinematic wide shot",
]

COLOR_PALETTES = [
    "random",
    "neon purple and pink palette",
    "black and gold palette",
    "vibrant streetwear colors",
    "dark muted palette",
    "teal and orange cinematic palette",
]

ENVIRONMENTS = [
    "random",
    "minimal studio background",
    "futuristic city backdrop",
    "urban alley environment",
    "dramatic abstract background",
    "dark atmospheric setting",
]

DETAIL = [
    "random",
    "ultra detailed",
    "high detail concept art",
    "professional character concept art",
    "AAA game concept quality",
]

DEFAULT_NEGATIVE_PROMPT = (
    "blurry, low quality, watermark, text artifacts, extra limbs, "
    "bad anatomy, distorted face"
)


# ------------------------------
# HELPERS
# ------------------------------

def _clean_csv_text(text):
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def _pick(value, choices):
    if value == "random" or not value:
        valid = [c for c in choices if c != "random"]
        return random.choice(valid)
    return value


def _dedupe_keep_order(items):
    seen = set()
    output = []
    for item in items:
        norm = item.strip().lower()
        if item and norm not in seen:
            seen.add(norm)
            output.append(item.strip())
    return output


def default_prompt_settings():
    return {
        "mode": "preset_only",
        "preset": "cyberpunk",
        "custom_prompt": "",
        "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
        "lighting": "random",
        "camera": "random",
        "palette": "random",
        "environment": "random",
        "detail": "random",
        "subject": "same character but redesigned outfit",
        "redesign_strength": 0.8,
        "denoise": 0.6,
        "seed_lock": False,
        "batch_size": 4,
    }


# ------------------------------
# PROMPT BUILDING
# ------------------------------

def build_prompt_from_settings(settings):
    mode = settings.get("mode", "preset_only")
    preset = settings.get("preset", "cyberpunk")
    custom_prompt = settings.get("custom_prompt", "").strip()
    negative_prompt = settings.get("negative_prompt", DEFAULT_NEGATIVE_PROMPT).strip()
    subject = settings.get("subject", "same character but redesigned outfit").strip()
    redesign_strength = float(settings.get("redesign_strength", 0.8))

    lighting = _pick(settings.get("lighting", "random"), LIGHTING)
    camera = _pick(settings.get("camera", "random"), CAMERA)
    palette = _pick(settings.get("palette", "random"), COLOR_PALETTES)
    environment = _pick(settings.get("environment", "random"), ENVIRONMENTS)
    detail = _pick(settings.get("detail", "random"), DETAIL)

    prompt_parts = [subject, f"redesign strength {redesign_strength:.2f}"]

    preset_parts = PRESETS.get(preset, [])

    if mode == "preset_only":
        prompt_parts.extend(preset_parts)

    elif mode == "manual_only":
        prompt_parts.extend(_clean_csv_text(custom_prompt))

    elif mode == "preset_plus_manual":
        prompt_parts.extend(preset_parts)
        prompt_parts.extend(_clean_csv_text(custom_prompt))

    elif mode == "randomized":
        random_preset = random.choice([k for k in PRESETS.keys() if k != "none"])
        prompt_parts.extend(PRESETS[random_preset])
        if custom_prompt:
            prompt_parts.extend(_clean_csv_text(custom_prompt))
    else:
        prompt_parts.extend(preset_parts)

    prompt_parts.extend([lighting, camera, palette, environment, detail])
    prompt_parts.extend(["concept art", "professional character design"])

    prompt_parts = _dedupe_keep_order(prompt_parts)

    positive = ", ".join(prompt_parts)
    negative = negative_prompt if negative_prompt else DEFAULT_NEGATIVE_PROMPT

    return {
        "preset": preset,
        "prompt": positive,
        "negative_prompt": negative
    }


def generate_prompt(preset=None):
    settings = default_prompt_settings()
    if preset is not None:
        settings["preset"] = preset
    return build_prompt_from_settings(settings)