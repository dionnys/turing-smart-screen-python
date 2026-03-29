import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import urllib.request
from io import BytesIO

def create_theme(v_num, bg_src, logo_url, use_dark_text=False):
    theme_name = f"ARC_Raiders_v{v_num}"
    theme_dir = os.path.join(r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python\res\themes", theme_name)
    os.makedirs(theme_dir, exist_ok=True)
    
    bg_path = os.path.join(theme_dir, "background.png")
    preview_path = os.path.join(theme_dir, "preview.png")
    
    # 1. Background
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
    
    # 2. Logo Fetch and Overlay
    try:
        req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        logo_bytes = response.read()
        logo_img = Image.open(BytesIO(logo_bytes)).convert("RGBA")
        
        desired_w = 400
        logo_w, logo_h = logo_img.size
        # We need to crop or scale. The footer logo from previous is just the logo block. Let's scale it.
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
    
    # 3. Write Full theme.yaml
    text_c = "20, 20, 20" if use_dark_text else "255, 255, 255"
    bar_c = "246, 10, 8"  # ARC Raiders Orange
    yaml_content = f"""---
author: "@dionnys"

display:
  DISPLAY_SIZE: 9.2"
  DISPLAY_ORIENTATION: landscape
  width: 1920
  height: 462
  background: 'background.png'

static_images:
  BACKGROUND:
    PATH:  background.png
    X: 0
    Y: 0
    WIDTH: 1920
    HEIGHT: 462

static_text:
  CPU:
   TEXT: CPU
   X: 1120
   Y: 44
   FONT_SIZE: 34
   FONT_COLOR: {text_c}
   BACKGROUND_IMAGE: background.png
  GPU:
   TEXT: GPU
   X: 1120
   Y: 85
   FONT_SIZE: 34
   FONT_COLOR: {text_c}
   BACKGROUND_IMAGE: background.png
  RAM:
   TEXT: RAM
   X: 1120
   Y: 126
   FONT_SIZE: 34
   FONT_COLOR: {text_c}
   BACKGROUND_IMAGE: background.png

STATS:
  CPU:
    PERCENTAGE:
      INTERVAL: 1
      TEXT:
        SHOW: True
        SHOW_UNIT: False
        X: 1204
        Y: 40
        WIDTH: 73
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: {text_c}
        BACKGROUND_IMAGE: background.png
      GRAPH:
        SHOW: True
        X: 1296
        Y: 40
        WIDTH: 374
        HEIGHT: 30
        MIN_VALUE: 0
        MAX_VALUE: 100
        BAR_COLOR: {bar_c}
        BAR_OUTLINE: False
        BACKGROUND_COLOR: 0, 0, 0
    TEMPERATURE:
      INTERVAL: 5
      TEXT:
        SHOW: True
        SHOW_UNIT: False
        X: 1780
        Y: 40
        WIDTH: 73
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: {text_c}
        BACKGROUND_IMAGE: background.png

  GPU:
    INTERVAL: 1
    PERCENTAGE:
      GRAPH:
        SHOW: True
        X: 1296
        Y: 84
        WIDTH: 374
        HEIGHT: 30
        MIN_VALUE: 0
        MAX_VALUE: 100
        BAR_COLOR: {bar_c}
        BAR_OUTLINE: False
        BACKGROUND_COLOR: 0, 0, 0
      TEXT:
        SHOW: True
        SHOW_UNIT: False
        X: 1204
        Y: 81
        WIDTH: 73
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: {text_c}
        BACKGROUND_IMAGE: background.png
    TEMPERATURE:
      TEXT:
        SHOW: True
        SHOW_UNIT: False
        X: 1780
        Y: 81
        WIDTH: 73
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: {text_c}
        BACKGROUND_IMAGE: background.png

  RAM:
    INTERVAL: 1
    PERCENTAGE:
      GRAPH:
        SHOW: True
        X: 1296
        Y: 128
        WIDTH: 374
        HEIGHT: 30
        MIN_VALUE: 0
        MAX_VALUE: 100
        BAR_COLOR: {bar_c}
        BAR_OUTLINE: False
        BACKGROUND_COLOR: 0, 0, 0
      TEXT:
        SHOW: True
        SHOW_UNIT: False
        X: 1204
        Y: 125
        WIDTH: 73
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: {text_c}
        BACKGROUND_IMAGE: background.png
"""
    yaml_path = os.path.join(theme_dir, "theme.yaml")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
        
    print(f"Created {theme_name}")

# Let's generate both versions using two different keyarts!
# V1: The base one (using ARC_Keyart_11.jpg)
create_theme(
    v_num="1",
    bg_src=r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\ARC Raiders_Press Kit_v.1.3.0\Keyart\ARC_Keyart_11.jpg",
    logo_url="https://sht-vod.dn.nexoncdn.co.kr/arcraiders/app-assets/footer_arcraiders.BxG0HyYX.png",
    use_dark_text=False
)

# V2: The dam one (using ARC_Keyart_02.jpg)
create_theme(
    v_num="2",
    bg_src=r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\ARC Raiders_Press Kit_v.1.3.0\Keyart\ARC_Keyart_02.jpg",
    logo_url="https://sht-vod.dn.nexoncdn.co.kr/arcraiders/app-assets/footer_arcraiders.BxG0HyYX.png",
    use_dark_text=False
)

# Clean up older broken theme to prevent confusion for user
old_theme = r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python\res\themes\ARC_Raiders"
if os.path.exists(old_theme):
    try:
        shutil.rmtree(old_theme)
        print("Removed old empty theme.")
    except:
        pass

print("Done generating 2 versions of Arc Raiders themes!")
