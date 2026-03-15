# SnapRedesign

SnapRedesign is a **desktop AI redesign tool** that turns anything on your screen into new concept art using local AI models.

Press a hotkey, snip any image on your screen, open the **Prompt Lab**, shape the redesign with presets or fully manual prompting, and SnapRedesign generates redesigned versions using a **local ComfyUI workflow**.

The goal is to make AI behave like a **design assistant for fast concept exploration**.

---

# Features

### Instant Screen Redesign

- Press **Ctrl + Shift + S**
- Select any part of your screen
- SnapRedesign automatically launches the redesign pipeline

### Local AI Generation

- Uses **ComfyUI workflows**
- Runs entirely on your own GPU
- No cloud services required

ComfyUI workflows are JSON graphs of nodes that describe the image generation pipeline and can be executed through API routes such as `/prompt`, `/history/{prompt_id}`, and `/view`.

### Prompt Lab

SnapRedesign now includes a dedicated **Prompt Lab** UI for deeper creative control.

You can:

- choose a prompt mode
- use a preset or no preset at all
- type your own custom positive prompt
- edit the negative prompt
- preview the final composed prompt before generation
- save settings for later runs

### Prompt Modes

Built-in prompt modes include:

- **Preset Only**
- **Manual Only**
- **Preset + Manual**
- **Randomized**

This means you can:

- rely fully on presets
- ignore presets and type everything yourself
- blend presets with your own prompt additions
- let SnapRedesign generate a more randomized prompt structure

### Style Presets

Built-in style presets include:

- Cyberpunk
- Anime
- Comic
- Streetwear
- Samurai
- Dark Fantasy
- Sci-Fi
- Military
- Retro Arcade
- High Fashion
- Game Character
- Punk
- Industrial
- Fantasy Hero
- MMA Fighter
- None

### Advanced Style Controls

Inside Prompt Lab, you can control:

- prompt mode
- style preset
- subject text
- custom positive prompt
- negative prompt
- redesign strength
- denoise strength
- seed locking
- batch size
- lighting
- camera angle
- color palette
- environment
- detail level

### Live Prompt Preview

Before generation, SnapRedesign builds the final positive and negative prompt for you and shows it live inside the UI.

This makes it easier to:

- understand what will actually be sent to the workflow
- iterate faster
- combine presets with custom prompt text more intentionally

### Persistent Settings

SnapRedesign now saves your prompt and style configuration to `ui_state.json`.

This includes settings such as:

- prompt mode
- preset
- custom prompt
- negative prompt
- redesign strength
- denoise
- seed lock
- batch size
- lighting / camera / palette / environment / detail

So the next time you open the app, your previous setup is already loaded.

### CLIP Similarity Ranking

Generated images are ranked based on how closely they match the original image.

This helps preserve:

- character identity
- pose
- design consistency

### Image Comparison Viewer

The results viewer displays:

```text
Original image | Generated variants
````

Each generated image shows a **CLIP similarity score** so you can quickly find the best redesign.

### History Gallery

SnapRedesign includes a **History Gallery** for browsing previously generated images saved in the `outputs/` folder.

This makes it easier to:

* review older redesigns
* compare experiments across sessions
* reuse previous concepts

### Cyberpunk Desktop UI

The desktop UI now uses a darker, more stylized visual presentation with:

* cyberpunk-inspired panels
* HUD-like overlays
* scanline effects
* neon accent colors
* improved viewer and gallery windows

### System Tray App

SnapRedesign runs in the background with a tray icon.

Tray menu:

```text
Snip + Redesign
History Gallery
Open Outputs
Choose Style
Quit
```

### Global Hotkeys

```text
CTRL + SHIFT + S → capture image
ESC → cancel snip overlay
```

The application listens for system-wide hotkeys and launches the redesign pipeline instantly.

---

# How It Works

Pipeline:

```text
Snip screen
    ↓
Prompt Lab / prompt construction
    ↓
ComfyUI workflow execution
    ↓
CLIP similarity scoring
    ↓
Image comparison viewer
```

ComfyUI executes workflows by accepting a workflow JSON through `/prompt`, then the app polls execution history and downloads outputs when the job is complete.

---

# Project Structure

```text
SnapRedesign
│
├── outputs/                     # Generated images
│
├── src/snapredesign/
│   ├── main.py                  # Application entry point
│   ├── comfy_client.py          # ComfyUI API client
│   ├── snip_overlay.py          # Screen capture overlay
│   ├── openai_prompt.py         # Prompt generation engine
│   ├── style_state.py           # Saved prompt/style state
│   ├── style_ui.py              # Prompt Lab UI
│   ├── theme.py                 # Shared cyberpunk theme values
│   ├── tray_app.py              # System tray app
│   ├── viewer.py                # Image comparison viewer
│   └── history_gallery.py       # Output gallery viewer
│
├── workflow_api.json            # ComfyUI workflow
├── config.json                  # Configuration
├── ui_state.json                # Saved prompt/style settings
├── requirements.txt             # Python dependencies
├── pyproject.toml
└── README.md
```

---

# Requirements

* Python **3.10+**
* **ComfyUI running locally (SEE SETUP BELOW)**
* NVIDIA GPU recommended (for faster generation speed)
* Windows recommended (`keyboard` library works best there)

---

# ComfyUI Setup

SnapRedesign acts as a lightweight frontend, while a local ComfyUI instance serves as the AI backend engine. Before starting the app, you **must** complete the following ComfyUI setup:

1. **Download ComfyUI:**
   Download the [ComfyUI Windows Portable](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z) standalone package and extract it. Avoid spaces or non-English characters in the folder path.

2. **Place Core Models:**
   This project's workflow relies on three specific model weights. Place them in the following directories:

   * **UNET Model:** [`z_image_turbo_bf16.safetensors`](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) → `ComfyUI/models/unet/`
   * **CLIP Text Encoder:** [`qwen_3_4b.safetensors`](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) → `ComfyUI/models/clip/`
   * **VAE Model:** [`ae.safetensors`](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) → `ComfyUI/models/vae/`

3. **Start ComfyUI:**
   Double-click `run_nvidia_gpu.bat` in the ComfyUI directory and keep the terminal window running in the background.

4. **Align Port Configuration:**
   ComfyUI runs on port `8188` by default. The checked-in `config.json` already uses that port, and if you customize it later it should still look like this:

```json
{
  "comfy_url": "http://127.0.0.1:8188"
}
```

---

# App Installation

Clone the repository:

```bash
git clone https://github.com/Caiya233/SnapRedesign.git
cd SnapRedesign
```

Create and activate a virtual environment:
(if source code modification is needed. Otherwise, feel free to skip this step.)

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies include:

* PyTorch
* CLIP
* Pillow
* Requests
* Keyboard
* PyStray
* CustomTkinter

Install the project as a local editable package:

```bash
pip install -e .
```

---

# Running the App

Start SnapRedesign:

```bash
python -m snapredesign.main
```

Once running:

```text
CTRL + SHIFT + S → snip an image
```

Then:

1. capture an image region
2. configure Prompt Lab
3. generate redesign variants
4. compare results in the viewer
5. browse previous outputs in History Gallery

To view previous outputs, right-click the tray icon and choose **History Gallery**.

---

# Example Workflow

```text
Take screenshot
        ↓
Open Prompt Lab
        ↓
Choose preset / manual prompt / mixed mode
        ↓
Tune style controls
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

Quickly explore alternate character designs, silhouettes, outfits, and visual directions.

### Fan Artists

Generate new outfits, palettes, and visual styles for existing characters.

### Game Developers

Rapidly prototype character concepts and visual iterations.

### Writers

Visualize characters, worlds, factions, and story aesthetics.

### Designers / Creative Technologists

Use local AI generation like a fast ideation layer for concept exploration.

---

# Status

Prototype / class project.

Current capabilities:

* screen capture
* Prompt Lab
* prompt modes
* manual prompt editing
* style presets
* local inference
* image comparison
* CLIP ranking
* system tray app
* global hotkeys
* persistent settings
* history gallery
* cyberpunk UI styling

---

# Future Improvements

Potential upgrades:

* workflow selector (Flux / SDXL / Turbo)
* style library
* LoRA support
* pose-lock with ControlNet
* stronger prompt suggestion tools
* saved prompt profiles
* export to Photoshop / Krita
* side-by-side prompt diffing
* multi-workflow generation presets
