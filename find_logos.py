import glob
from PIL import Image

pngs = glob.glob(r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit\ARC Raiders_Press Kit_v.1.3.0\Keyart\*.png")
for p in pngs:
    try:
        img = Image.open(p)
        print(f"{p.split('\\')[-1]}: mode={img.mode}, size={img.size}")
    except Exception as e:
        pass
