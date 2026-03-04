import random


# ------------------------------
# STYLE PRESETS
# ------------------------------

PRESETS = {
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
# LIGHTING OPTIONS
# ------------------------------

LIGHTING = [
    "dramatic cinematic lighting",
    "neon rim lighting",
    "soft studio lighting",
    "moody noir lighting",
    "golden hour lighting",
    "high contrast lighting",
]


# ------------------------------
# CAMERA ANGLES
# ------------------------------

CAMERA = [
    "low angle hero shot",
    "three quarter character view",
    "dynamic action angle",
    "top down stylized angle",
    "cinematic wide shot",
]


# ------------------------------
# COLOR PALETTES
# ------------------------------

COLOR_PALETTES = [
    "neon purple and pink palette",
    "black and gold palette",
    "vibrant streetwear colors",
    "dark muted palette",
    "teal and orange cinematic palette",
]


# ------------------------------
# ENVIRONMENTS
# ------------------------------

ENVIRONMENTS = [
    "minimal studio background",
    "futuristic city backdrop",
    "urban alley environment",
    "dramatic abstract background",
    "dark atmospheric setting",
]


# ------------------------------
# DETAIL LEVEL
# ------------------------------

DETAIL = [
    "ultra detailed",
    "high detail concept art",
    "professional character concept art",
    "AAA game concept quality",
]


# ------------------------------
# NEGATIVE PROMPTS
# ------------------------------

NEGATIVE_PROMPT = [
    "blurry",
    "low quality",
    "watermark",
    "text artifacts",
    "extra limbs",
    "bad anatomy",
    "distorted face",
]


# ------------------------------
# PROMPT BUILDER
# ------------------------------

def build_prompt(
    subject="same character",
    preset=None,
    redesign_strength=0.7,
):
    """
    Build a strong prompt for diffusion models.
    """

    if preset is None:
        preset = random.choice(list(PRESETS.keys()))

    style_elements = PRESETS[preset]

    lighting = random.choice(LIGHTING)
    camera = random.choice(CAMERA)
    palette = random.choice(COLOR_PALETTES)
    environment = random.choice(ENVIRONMENTS)
    detail = random.choice(DETAIL)

    prompt_parts = [
        subject,
        f"redesign strength {redesign_strength}",
        *style_elements,
        lighting,
        camera,
        palette,
        environment,
        detail,
        "concept art",
        "professional character design"
    ]

    prompt = ", ".join(prompt_parts)

    negative = ", ".join(NEGATIVE_PROMPT)

    return prompt, negative


# ------------------------------
# MULTI PROMPT GENERATION
# ------------------------------

def generate_prompt_variations(
    subject="same character redesigned",
    count=4
):
    prompts = []

    for _ in range(count):
        preset = random.choice(list(PRESETS.keys()))
        prompt, negative = build_prompt(subject, preset)

        prompts.append({
            "preset": preset,
            "prompt": prompt,
            "negative_prompt": negative
        })

    return prompts


# ------------------------------
# MAIN FUNCTION USED BY APP
# ------------------------------

def generate_prompt():

    preset = random.choice(list(PRESETS.keys()))

    prompt, negative = build_prompt(
        subject="same character but redesigned outfit",
        preset=preset,
        redesign_strength=0.8
    )

    return {
        "preset": preset,
        "prompt": prompt,
        "negative_prompt": negative
    }