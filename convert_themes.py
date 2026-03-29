import os
import shutil
from pathlib import Path
from PIL import Image

src_dir = r"res\themes\--Theme examples\8.8inch"
dest_dir = r"res\themes\--Theme examples\9.2inch"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# Copy all folders
print("Copying directories...")
for item in os.listdir(src_dir):
    src_path = os.path.join(src_dir, item)
    dest_path = os.path.join(dest_dir, item)
    if os.path.isdir(src_path):
        if not os.path.exists(dest_path):
            shutil.copytree(src_path, dest_path)

print("Converting yaml and resizing images...")
for theme_folder in os.listdir(dest_dir):
    theme_path = os.path.join(dest_dir, theme_folder)
    yaml_path = os.path.join(theme_path, "theme.yaml")
    
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        content = content.replace('DISPLAY_SIZE: 8.8"', 'DISPLAY_SIZE: 9.2"')
        content = content.replace('WIDTH: 480', 'WIDTH: 462')
        content = content.replace('WIDTH:  480', 'WIDTH: 462')
        content = content.replace('HEIGHT: 480', 'HEIGHT: 462')
        content = content.replace('HEIGHT:  480', 'HEIGHT: 462')
        
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    # Resize images if they are 1920x480 or 480x1920
    for img_name in ["background.png", "preview.png"]:
        img_path = os.path.join(theme_path, img_name)
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                w, h = img.size
                if str(w) == "1920" and str(h) == "480":
                    img = img.resize((1920, 462))
                    img.save(img_path)
                elif str(w) == "480" and str(h) == "1920":
                    img = img.resize((462, 1920))
                    img.save(img_path)
            except Exception as e:
                print(f"Error with {img_path}: {e}")

print("Done generating 9.2inch themes!")
