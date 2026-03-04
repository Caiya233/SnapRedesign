# SnapRedesign

SnapRedesign is a **desktop AI redesign tool** that turns anything on your screen into new concept art using local AI models.

Press a hotkey, snip any image on your screen, choose a visual style, and SnapRedesign generates redesigned versions using a **local ComfyUI workflow**.

The goal is to make AI behave like a **design assistant for fast concept exploration**.

---

# Features

### Instant Screen Redesign

* Press **Ctrl + Shift + S**
* Select any part of your screen
* SnapRedesign automatically runs the AI pipeline

### Local AI Generation

* Uses **ComfyUI workflows**
* Runs entirely on your own GPU
* No cloud services required

ComfyUI workflows are JSON graphs of nodes that describe the image generation pipeline and can be executed through an API endpoint.

### Style Presets

Built-in prompt presets including:

* Cyberpunk
* Anime
* Comic
* Streetwear
* Samurai
* Dark Fantasy
* Sci-Fi
* Military
* Retro Arcade
* High Fashion

### Style Control UI

When generating an image you can choose:

* Style preset
* Denoise strength
* Seed locking (maintain character identity)

### CLIP Similarity Ranking

Generated images are ranked based on how closely they match the original image.

This helps preserve:

* character identity
* pose
* design consistency

### Image Comparison Viewer

The viewer displays:

```
Original image | Generated variants
```

Each generated image shows a **CLIP similarity score** so you can quickly find the best redesign.

### System Tray App

SnapRedesign runs in the background with a tray icon.

Tray menu:

```
Snip + Redesign
Open Outputs
Choose Style
Quit
```

Python libraries such as **pystray** allow applications to run in the system tray and attach interactive menus to an icon.

### Global Hotkeys

```
CTRL + SHIFT + S → capture image
ESC → exit app
```

The application listens for system-wide hotkeys and launches the redesign pipeline instantly.

---

# How It Works

Pipeline:

```
Snip screen
    ↓
Prompt generation
    ↓
ComfyUI workflow execution
    ↓
CLIP similarity scoring
    ↓
Image comparison viewer
```

ComfyUI executes workflows through its API by sending a workflow JSON to the `/prompt` endpoint and retrieving results after the job finishes.

---

# Project Structure

```
SnapRedesign
│
├── outputs/                     # Generated images
│
├── src/snapredesign/
│   ├── main.py                  # Application entry point
│   ├── comfy_client.py          # ComfyUI API client
│   ├── snip_overlay.py          # Screen capture overlay
│   ├── openai_prompt.py         # Prompt generation engine
│   ├── style_ui.py              # Style selection UI
│   ├── tray_app.py              # System tray app
│   └── viewer.py                # Image comparison viewer
│
├── workflow_api.json            # ComfyUI workflow
├── config.json                  # Configuration
├── requirements.txt             # Python dependencies
├── pyproject.toml
└── README.md
```

---

# Requirements

* Python **3.10+**
* **ComfyUI running locally**
* NVIDIA GPU recommended

---

# Installation

Clone the repository:

```
git clone https://github.com/yourusername/SnapRedesign.git
cd SnapRedesign
```

Install dependencies:

```
pip install -r requirements.txt
```

Dependencies include:

* PyTorch
* CLIP
* Pillow
* Requests
* Keyboard
* PyStray

---

# Running the App

Start SnapRedesign:

```
python -m snapredesign.main
```

Once running:

```
CTRL + SHIFT + S → snip an image
```

The redesigned images will appear in the **viewer window** and be saved to:

```
outputs/
```

---

# Example Workflow

```
Take screenshot
        ↓
Choose style preset
        ↓
Generate redesign variants
        ↓
Compare results
        ↓
Export best concept
```

---

# Use Cases

SnapRedesign is designed for:

### Concept Artists

Quickly explore alternate character designs.

### Fan Artists

Generate new outfits, palettes, and visual styles.

### Game Developers

Rapidly prototype character concepts.

### Writers

Visualize characters and worldbuilding ideas.

---

# Status

Prototype / class project.

Current capabilities:

* Screen capture
* AI redesign generation
* Style presets
* Local inference
* Image comparison
* CLIP ranking
* System tray app
* Global hotkeys

---

# Future Improvements

Potential upgrades:

* Workflow selector (Flux / SDXL / Turbo)
* Style library
* LoRA support
* Pose-lock with ControlNet
* History gallery
* Export to Photoshop / Krita