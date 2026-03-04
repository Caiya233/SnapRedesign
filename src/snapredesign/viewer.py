import tkinter as tk
from PIL import Image, ImageTk


def show_results(original_path, results):

    root = tk.Tk()
    root.title("SnapRedesign Results")

    orig = Image.open(original_path).resize((256, 256))
    orig_img = ImageTk.PhotoImage(orig)

    tk.Label(root, text="Original").grid(row=0, column=0)
    tk.Label(root, image=orig_img).grid(row=1, column=0)

    sorted_results = sorted(results,
                            key=lambda r: r["score"],
                            reverse=True)

    for i, res in enumerate(sorted_results):

        img = res["image"].resize((256, 256))
        tk_img = ImageTk.PhotoImage(img)

        frame = tk.Frame(root)
        frame.grid(row=1, column=i + 1)

        label = tk.Label(frame, image=tk_img)
        label.image = tk_img
        label.pack()

        tk.Label(frame,
                 text=f"CLIP: {res['score']:.3f}").pack()

    root.mainloop()