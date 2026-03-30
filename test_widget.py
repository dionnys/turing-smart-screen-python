import tkinter as tk
from PIL import Image, ImageTk
import time
import threading

def update_image(label, root):
    while True:
        # Create a dummy image
        img = Image.new("RGB", (320, 480), "blue")
        tkimage = ImageTk.PhotoImage(img)
        label.config(image=tkimage)
        label.image = tkimage
        time.sleep(1)

def run_widget():
    root = tk.Tk()
    root.overrideredirect(True) # Remove window borders
    root.attributes("-topmost", True) # Always on top
    # Optional: root.attributes("-alpha", 0.8) for transparency
    
    # Try to make click-through depending on OS
    try:
        root.attributes("-transparentcolor", "black") # If "black" were the bg
    except:
        pass

    # Give it a position like top-right
    root.geometry("320x480+100+100")
    
    label = tk.Label(root, bg='black')
    label.pack(expand=True, fill="both")
    
    threading.Thread(target=update_image, args=(label, root), daemon=True).start()
    
    root.mainloop()

if __name__ == "__main__":
    run_widget()
