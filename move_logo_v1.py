import os
from PIL import Image, ImageSequence
import urllib.request
from io import BytesIO

logo_url = "https://sht-vod.dn.nexoncdn.co.kr/arcraiders/app-assets/footer_arcraiders.BxG0HyYX.png"

try:
    req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
    logo_bytes = urllib.request.urlopen(req).read()
    global_logo_img = Image.open(BytesIO(logo_bytes)).convert("RGBA")
    
    desired_w = 400
    lw, lh = global_logo_img.size
    ratio = desired_w / lw
    global_logo_img = global_logo_img.resize((desired_w, int(lh * ratio)), Image.Resampling.LANCZOS)
except Exception as e:
    global_logo_img = None
    print("Logo fail:", e)

def build_theme(v_num, bg_src):
    theme_name = f"ARC_Raiders_v{v_num}"
    theme_dir = os.path.join(r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python\res\themes", theme_name)
    os.makedirs(theme_dir, exist_ok=True)
    
    bg_path = os.path.join(theme_dir, "background.png")
    preview_path = os.path.join(theme_dir, "preview.png")

    img = Image.open(bg_src).convert("RGBA")
        
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

    if global_logo_img:
        # User requested logo on the "other side" (Right side)
        # We put it Bottom Right so it doesn't overlap the top-right sensors 
        # (Sensors usually occupy Y = 40 to 180 and X = 1120 to 1800)
        px = 1920 - global_logo_img.size[0] - 80
        py = 462 - global_logo_img.size[1] - 30
        img.alpha_composite(global_logo_img, (px, py))
        
    final_img = img.convert("RGB")
    final_img.save(bg_path)
    final_img.save(preview_path)
    print(f"Rebuilt {theme_name} successfully with logo on the right.")

build_theme("1", r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\ARC Raiders_Press Kit_v.1.3.0\Keyart\ARC_Keyart_11.jpg")
