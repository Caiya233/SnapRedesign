SnapRedesign

Overview:
A little app that runs in the background (system tray). You hit a hotkey, snip/crop any image on your screen, pick a style preset, and it spits out redesign fan art using Stable Diffusion on your own PC through AUTOMATIC1111’s API (img2img). 

Team (4):

App/UX: tray app, hotkey, snip tool, results popup + save/export

A1111/API: set up A1111 with --api, make the img2img calls, batching/queueing

Prompts/Presets: build style presets + “keep character the same but change outfit/era/style” prompt templates

Consistency + Testing: tune seed/denoise settings, (stretch) pose-lock with ControlNet, make the demo + evaluation

Theme:
AI as a design assistant (fast concept art / redesign workflow)

Novelty:
It’s basically “anything you see → redesign it” with one hotkey. Also adds simple controls so the character stays recognizable: seed lock + “how much to change it” slider.

Value:
For fan artists + concept artists + writers/game devs who want to crank out redesign ideas fast (different outfits, eras, palettes, vibes) without a bunch of manual steps.

Technology:

Uses img2img through A1111’s local REST API (send the cropped image + prompt + settings, get images back). 

Fast mode: quick previews first, then rerun the best one at higher quality settings.

Stretch: ControlNet to keep pose/silhouette stable.

Work plan (who does what):
Week 1: snip tool + working img2img API + 4 style presets
Week 2: seed lock + “change strength” slider + batch variants + history/gallery
Week 3: (stretch) pose-lock + run tests (10 images × 3 presets) + polish demo 
