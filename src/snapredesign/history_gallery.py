import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk

def open_gallery():
    OUTPUT_DIR = Path("outputs")
    if not OUTPUT_DIR.exists():
        print("No outputs folder found.")
        return

    # Get all image files in the outputs directory
    image_files = sorted(
        [f for f in OUTPUT_DIR.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    if not image_files:
        print("No images found in outputs.")
        return

    root = tk.Tk()
    root.title("SnapRedesign History Gallery")
    root.geometry("820x600")

    # canvas + scrollbar
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    columns = 4
    thumbnail_size = (180, 180)
    
    # to prevent garbage collection
    root.image_refs = []

    for index, img_path in enumerate(image_files):
        try:
            img = Image.open(img_path)
            img.thumbnail(thumbnail_size)
            tk_img = ImageTk.PhotoImage(img)
            root.image_refs.append(tk_img)

            row = index // columns
            col = index % columns

            frame = tk.Frame(scrollable_frame, padx=5, pady=5)
            frame.grid(row=row, column=col)

            lbl = tk.Label(frame, image=tk_img)
            lbl.pack()
            
        except Exception as e:
            print(f"Error loading {img_path}: {e}")

    root.mainloop()

if __name__ == "__main__":
    open_gallery()