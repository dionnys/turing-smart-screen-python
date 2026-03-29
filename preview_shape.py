from PIL import Image
import os
import ruamel.yaml

MAIN_DIRECTORY = r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python"
THEMES_DIR = os.path.join(MAIN_DIRECTORY, 'res/themes')

for theme in os.listdir(THEMES_DIR):
    img_path = os.path.join(THEMES_DIR, theme, "preview.png")
    if "9.2inch" in theme or theme == "Assassin's Creed":
        if os.path.exists(img_path):
            img = Image.open(img_path)
            print(f"Theme: {theme} - Preview Shape: {img.size}")
        else:
            print(f"Theme: {theme} - No preview.png found!")
