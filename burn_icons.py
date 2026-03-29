import sys
import shutil
from PIL import Image

def make_trans(img, target_size=(40,40)):
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item
        lum = int(0.299 * r + 0.587 * g + 0.114 * b)
        # Cortar a rajatabla lo que sea oscuro y forzar blanco a lo claro
        if lum < 50:
            new_data.append((255, 255, 255, 0))
        else:
            alpha = min(255, lum * 3) # Multiplicador bestia para extra brillo
            new_data.append((255, 255, 255, alpha))
    img.putdata(new_data)
    return img.resize(target_size, Image.Resampling.LANCZOS)

def main():
    bd = r'c:\Users\dionnys\Documents\Devs\turing-smart-screen-python\res\themes\ARC_Raiders'
    
    import os
    if not os.path.exists(f'{bd}/background_original.png'):
        try:
            shutil.copyfile(f'{bd}/background.png', f'{bd}/background_original.png')
        except Exception:
            pass
            
    bg = Image.open(f'{bd}/background_original.png').convert('RGBA')
    
    # 2. Cargar los íconos de IA (transparentarlos y achicarlos)
    fan = Image.open(r'C:\Users\dionnys\.gemini\antigravity\brain\0342f2be-2b9d-4801-ab60-8a74bdf3a32f\white_fan_icon_1774709647876.png')
    pump = Image.open(r'C:\Users\dionnys\.gemini\antigravity\brain\0342f2be-2b9d-4801-ab60-8a74bdf3a32f\white_pump_icon_1774709665697.png')
    globe = Image.open(r'C:\Users\dionnys\.gemini\antigravity\brain\0342f2be-2b9d-4801-ab60-8a74bdf3a32f\white_globe_icon_1774712769222.png')
    
    fan = make_trans(fan, (40, 40))
    pump = make_trans(pump, (40, 40))
    
    # 3. Estamparlos permanentemente en el fondo de la pantalla (en el centro del medidor verde)
    bg.alpha_composite(fan, dest=(1320 - 18, 325 - 18))
    bg.alpha_composite(pump, dest=(1620 - 18, 325 - 18))
    
    # 4. Sobrescribir el Wallpaper principal!
    bg.convert("RGB").save(f'{bd}/background.png')
    print("¡Iconos estampados con éxito! Ahora reinicia main.py")

if __name__ == "__main__":
    main()
