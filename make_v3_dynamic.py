import os
from PIL import Image, ImageSequence, ImageDraw, ImageFont
import urllib.request
from io import BytesIO

theme_name = "ARC_Raiders_v3"
theme_dir = os.path.join(r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python\res\themes", theme_name)
os.makedirs(theme_dir, exist_ok=True)

bg_path = os.path.join(theme_dir, "background.png")
preview_path = os.path.join(theme_dir, "preview.png")

gif_path = r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\game_ARC Raiders-Embark品牌媒体工具包\LPYQKYAMVQHYN.info\ARC_Raiders_Reveal_GIF_BossFight.gif"
if not os.path.exists(gif_path):
    gif_path = r"C:\Users\dionnys\Downloads\game_ARC Raiders-Embark品牌媒体工具包\LPYQKYAMVQHYN.info\ARC_Raiders_Reveal_GIF_BossFight.gif"

orig_img = Image.open(gif_path)
# Get the middle frame of the boss fight so it's action packed!
frames = [frame.copy() for frame in ImageSequence.Iterator(orig_img)]
mid_frame = len(frames) // 2
img = frames[mid_frame].convert("RGBA")

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

# Logo overlay
logo_url = "https://sht-vod.dn.nexoncdn.co.kr/arcraiders/app-assets/footer_arcraiders.BxG0HyYX.png"
try:
    req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
    logo_bytes = urllib.request.urlopen(req).read()
    logo_img = Image.open(BytesIO(logo_bytes)).convert("RGBA")
    desired_w = 400
    lw, lh = logo_img.size
    ratio = desired_w / lw
    logo_img = logo_img.resize((desired_w, int(lh * ratio)), Image.Resampling.LANCZOS)
    px = (1920 - logo_img.size[0]) // 2
    py = (462 - logo_img.size[1]) // 2
    img.alpha_composite(logo_img, (px, py))
except:
    pass
    
final_img = img.convert("RGB")
final_img.save(bg_path)
final_img.save(preview_path)

print("V3 Dynamic (Action) theme generated!")
