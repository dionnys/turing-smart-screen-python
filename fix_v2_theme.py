import os
from PIL import Image, ImageDraw, ImageFont
import urllib.request
from io import BytesIO

def create_theme(v_num, bg_src, logo_url, use_dark_text=False):
    theme_name = f"ARC_Raiders_v{v_num}"
    theme_dir = os.path.join(r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python\res\themes", theme_name)
    os.makedirs(theme_dir, exist_ok=True)
    
    bg_path = os.path.join(theme_dir, "background.png")
    preview_path = os.path.join(theme_dir, "preview.png")
    
    # Background
    img = Image.open(bg_src)
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
    
    # Logo
    try:
        req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        logo_bytes = response.read()
        logo_img = Image.open(BytesIO(logo_bytes)).convert("RGBA")
        
        desired_w = 400
        logo_w, logo_h = logo_img.size
        ratio = desired_w / logo_w
        logo_img = logo_img.resize((desired_w, int(logo_h * ratio)), Image.Resampling.LANCZOS)
        logo_w, logo_h = logo_img.size
        
        pos_x = (1920 - logo_w) // 2
        pos_y = (462 - logo_h) // 2
        img.alpha_composite(logo_img, (pos_x, pos_y))
    except Exception as e:
        print("Logo fail:", e)
        
    final_img = img.convert("RGB")
    final_img.save(bg_path)
    final_img.save(preview_path)

# Let's override ARC_Raiders_v2 with ARC_Keyart_08.png
# AND make ARC_Raiders_v3 with ARC_Keyart_17.jpg to give user options!
# I'll just remake v2 for now with ARC_Keyart_08.png!

logo = "https://sht-vod.dn.nexoncdn.co.kr/arcraiders/app-assets/footer_arcraiders.BxG0HyYX.png"

create_theme(
    v_num="2",
    bg_src=r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\ARC Raiders_Press Kit_v.1.3.0\Keyart\ARC_Keyart_08.png",
    logo_url=logo,
    use_dark_text=False
)

create_theme(
    v_num="3",
    bg_src=r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\ARC Raiders_Press Kit_v.1.3.0\Keyart\ARC_Keyart_17.jpg",
    logo_url=logo,
    use_dark_text=False
)

print("Created V2 and V3 with better source images.")
