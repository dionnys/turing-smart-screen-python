"""Script temporal para generar background_transparent.png en el tema ARC_Raiders."""
from PIL import Image
img = Image.new('RGBA', (1920, 462), (0, 0, 0, 0))
img.save(r'res\themes\ARC_Raiders\background_transparent.png')
print("background_transparent.png creado (1920x462, RGBA puro)")
