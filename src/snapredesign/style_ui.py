import tkinter as tk
from snapredesign.openai_prompt import PRESETS

def choose_style():

    result = {
        "preset": None,
        "denoise": 0.6,
        "seed_lock": False
    }

    root = tk.Tk()
    root.title("SnapRedesign Style")

    tk.Label(root, text="Choose Style").pack()

    preset_var = tk.StringVar(value=list(PRESETS.keys())[0])

    dropdown = tk.OptionMenu(root, preset_var, *PRESETS.keys())
    dropdown.pack()

    tk.Label(root, text="Denoise Strength").pack()

    denoise = tk.Scale(root, from_=0.2, to=0.9, resolution=0.05,
                       orient=tk.HORIZONTAL)
    denoise.set(0.6)
    denoise.pack()

    seed_lock = tk.BooleanVar()

    tk.Checkbutton(root,
                   text="Lock Seed (keep character identity)",
                   variable=seed_lock).pack()

    def confirm():
        result["preset"] = preset_var.get()
        result["denoise"] = denoise.get()
        result["seed_lock"] = seed_lock.get()
        root.destroy()

    tk.Button(root, text="Generate", command=confirm).pack()

    root.mainloop()

    return result