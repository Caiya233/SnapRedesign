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
* **ComfyUI running locally (SEE SETUP BELOW)**
* NVIDIA GPU recommended (for faster generation speed)
* Windows recommended (`keyboard` library doesn't work well on MacOS)

---

# ComfyUI Setup

SnapRedesign acts as a lightweight frontend, while a local ComfyUI instance serves as the AI backend engine. Before starting the app, you **must** complete the following ComfyUI setup:

1. **Download ComfyUI**: Download the [ComfyUI Windows Portable](https://github.com/comfyanonymous/ComfyUI) standalone package and extract it (ensure there are no spaces or non-English characters in the folder path).
2. **Place Core Models**: This project's workflow relies on three specific model weights. Please place them strictly in the following directories:
   * **UNET Model**: [z_image_turbo_bf16.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) ➡️ Place in `ComfyUI/models/unet/`
   * **CLIP Text Encoder**: [qwen_3_4b.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/text_encoders/qwen_3_4b.safetensors) ➡️ Place in `ComfyUI/models/clip/`
   * **VAE Model**: [ae.safetensors](https://huggingface.co/Comfy-Org/z_image_turbo/blob/main/split_files/vae/ae.safetensors) ➡️ Place in `ComfyUI/models/vae/`
3. **Fire the Engine**: Double-click `run_nvidia_gpu.bat` in the ComfyUI directory (SINCE NVIDIA GPU IS RECOMMENDED). Wait for it to load and keep the terminal window running in the background.
4. **Align Port Configuration**: ComfyUI runs on port `8188` by default. Ensure the `config.json` in the root directory of SnapRedesign is configured as follows:
    ```json
    {
        "comfy_url": "http://127.0.0.1:8188"
    }
    ```

---

# App Installation

Clone the repository:

```
git clone https://github.com/yourusername/SnapRedesign.git
cd SnapRedesign
```

Create & activate a virtual environment:

```
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

* Dependencies include:

    * PyTorch
    * CLIP
    * Pillow
    * Requests
    * Keyboard
    * PyStray

Install the project as a local editable package:

```
pip install -e .
```

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

Right-click the icon in the system tray & select ```History Gallery```, then the redesigned images saved to ```outputs/``` folder will appear in the **viewer window**.

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