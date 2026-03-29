import os
import glob

base_dir = r"C:\Users\dionnys\Downloads\game_ARC Raiders-Embark品牌媒体工具包"
gifs = []
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.lower().endswith('.gif'):
            gifs.append(os.path.join(root, file))

for g in gifs:
    print(g)

# Also check the english press kit just in case
en_dir = r"C:\Users\dionnys\Downloads\ARC Raiders_Press Kit"
for root, dirs, files in os.walk(en_dir):
    for file in files:
        if file.lower().endswith('.gif'):
            gifs.append(os.path.join(root, file))
            print("Found in EN:", os.path.join(root, file))
