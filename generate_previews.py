import os
import shutil

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
        import yaml
        yaml_path = os.path.join(folder_path, "theme.yaml")
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if data and 'display' in data and 'background' in data['display']:
                bg_name = data['display']['background']
                bg_path = os.path.join(folder_path, bg_name)
                preview_path = os.path.join(folder_path, "preview.png")
                
                if os.path.exists(bg_path) and not os.path.exists(preview_path):
                    shutil.copyfile(bg_path, preview_path)
                    print(f"Generated preview for {folder} from {bg_name}")
