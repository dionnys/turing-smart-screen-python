import os
import glob

themes_dir = os.path.join("res", "themes")
dummy_generated = [
    "9.2inch_Assassins_Creed", "9.2inch_BLUE", "9.2inch_TechnologyX",
    "APEX", "Assassin's Creed", "BLUE", "Darius", "Dragon Ball", "Earth Theme",
    "GUNDAM", "Jyanme", "kirby", "METROID", "Pink data", "Ranni",
    "SPY FAMILY", "Technology X"
]

for folder in dummy_generated:
    folder_path = os.path.join(themes_dir, folder)
    if os.path.isdir(folder_path):
        yaml_path = os.path.join(folder_path, "theme.yaml")
        pngs = glob.glob(os.path.join(folder_path, "theme_res_*.png"))
        if len(pngs) > 0:
            largest_png = max(pngs, key=os.path.getsize)
            bg_name = os.path.basename(largest_png)
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                f.write("display:\n")
                f.write("  DISPLAY_SIZE: '9.2\"'\n")
                f.write("  width: 1920\n")
                f.write("  height: 462\n")
                f.write(f"  background: '{bg_name}'\n")
            print(f"Fixed theme.yaml for {folder}")
