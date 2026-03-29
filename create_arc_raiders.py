import os
import glob
from PIL import Image

# Use one of the press kit images
src_img = r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\ARC Raiders_Press Kit_v.1.3.0\Keyart\ARC_Keyart_11.jpg"
if not os.path.exists(src_img):
    # fallback to another if 11 is not available or has issues
    pngs = glob.glob(r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\ARC Raiders_Press Kit_v.1.3.0\Keyart\*.*")
    src_img = [p for p in pngs if p.lower().endswith(('.png', '.jpg', '.jpeg'))][3]   

theme_dir = os.path.join(r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python\res\themes", "ARC_Raiders")
if not os.path.exists(theme_dir):
    os.makedirs(theme_dir)

img = Image.open(src_img)
w, h = img.size

# We want exactly 1920x462 for a 9.2inch ultra wide
new_w = 1920
ratio = new_w / w
new_h = int(h * ratio)
img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

# If height is greater than 462, crop the middle part
if new_h > 462:
    top = (new_h - 462) // 2
    bottom = top + 462
    img = img.crop((0, top, 1920, bottom))
else:
    # If smaller, resize so height is 462 and crop width
    ratio = 462 / new_h
    new_w2 = int(1920 * ratio)
    img = img.resize((new_w2, 462), Image.Resampling.LANCZOS)
    left = (new_w2 - 1920) // 2
    right = left + 1920
    img = img.crop((left, 0, right, 462))

bg_path = os.path.join(theme_dir, "theme_res_arc.png")
img.save(bg_path)
img.save(os.path.join(theme_dir, "preview.png"))

with open(os.path.join(theme_dir, "theme.yaml"), "w", encoding="utf-8") as f:
    f.write("display:\n")
    f.write("  DISPLAY_SIZE: '9.2\"'\n")
    f.write("  width: 1920\n")
    f.write("  height: 462\n")
    f.write("  background: 'theme_res_arc.png'\n")

print(f"Arc Raiders theme created successfully using {os.path.basename(src_img)}!")
