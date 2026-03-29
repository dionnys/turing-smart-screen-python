import os
from PIL import Image, ImageDraw, ImageFont
import urllib.request
from io import BytesIO

theme_dir = os.path.join(r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python\res\themes", "ARC_Raiders")
bg_path = os.path.join(theme_dir, "theme_res_arc.png")
preview_path = os.path.join(theme_dir, "preview.png")

logo_url = "https://sht-vod.dn.nexoncdn.co.kr/arcraiders/app-assets/footer_arcraiders.BxG0HyYX.png"

# We open the ORIGINAL raw keyart again so we don't paste multiple logos
src_bg = r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\ARC Raiders_Press Kit_v.1.3.0\Keyart\ARC_Keyart_11.jpg"
img = Image.open(src_bg)
w, h = img.size
new_w = 1920
ratio = new_w / w
new_h = int(h * ratio)
img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
if new_h > 462:
    top = (new_h - 462) // 2
    img = img.crop((0, top, 1920, top + 462))
else:
    ratio = 462 / new_h
    new_w2 = int(1920 * ratio)
    img = img.resize((new_w2, 462), Image.Resampling.LANCZOS)
    left = (new_w2 - 1920) // 2
    img = img.crop((left, 0, left + 1920, 462))

img = img.convert("RGBA")
w, h = img.size

# Download Logo
req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
logo_bytes = response.read()

logo_img = Image.open(BytesIO(logo_bytes)).convert("RGBA")
# Wait, let's see how big the logo is.
logo_w, logo_h = logo_img.size

# Resize logo if it's too big or just size it to 400px wide
desired_w = 400
if logo_w != desired_w:
    ratio = desired_w / logo_w
    n_w, n_h = desired_w, int(logo_h * ratio)
    logo_img = logo_img.resize((n_w, n_h), Image.Resampling.LANCZOS)
    logo_w, logo_h = n_w, n_h

# Center the logo mathematically!
pos_x = (1920 - logo_w) // 2
pos_y = (462 - logo_h) // 2

# Paste Logo using alpha mask
img.alpha_composite(logo_img, (pos_x, pos_y))

# Add "autor dionnys"
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("arialbd.ttf", 36)
except:
    font = ImageFont.load_default()

text = "By dionnys"
text_bbox = draw.textbbox((0, 0), text, font=font)
text_w = text_bbox[2] - text_bbox[0]
text_h = text_bbox[3] - text_bbox[1]

# Position bottom right
pos_x = w - text_w - 30
pos_y = h - text_h - 30

draw.text((pos_x+2, pos_y+2), text, font=font, fill=(0,0,0,255))
draw.text((pos_x, pos_y), text, font=font, fill=(255,255,255,255))

final_img = img.convert("RGB")
final_img.save(bg_path)
final_img.save(preview_path)

yaml_path = os.path.join(theme_dir, "theme.yaml")
yaml_content = []
with open(yaml_path, "r", encoding="utf-8") as f:
    yaml_content = f.readlines()

if not any("author: 'dionnys'" in line or "author: dionnys" in line for line in yaml_content):
    yaml_content.insert(0, "author: 'dionnys'\n")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.writelines(yaml_content)

print("Downloaded official logo, superimposed it flawlessly and saved the theme.")
