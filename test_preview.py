import os
import ruamel.yaml
from PIL import Image

MAIN_DIRECTORY = r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python"
THEMES_DIR = os.path.join(MAIN_DIRECTORY, 'res/themes')

def get_theme_data(name: str):
    dir = os.path.join(THEMES_DIR, name)
    theme = os.path.join(dir, 'theme.yaml')
    with open(theme, "rt", encoding='utf8') as stream:
        theme_data, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(stream)
        return theme_data

theme_name = "Assassin's Creed"
try:
    data = get_theme_data(theme_name)
    print("Keys found in theme_data:", data.keys() if data else "None")
except Exception as e:
    print(f"Error loading theme_data: {e}")

try:
    img_path = os.path.join(THEMES_DIR, theme_name, "preview.png")
    print(f"Does preview.png exist? {os.path.exists(img_path)}")
    img = Image.open(img_path)
    print("Image loaded successfully.")
    
    # Try the configure.py dangerous line
    if data and 'display' in data:
        size = data['display'].get("DISPLAY_SIZE", '3.5"')
        print(f"Display size: {size}")
    else:
        print("display key not found in data!")
except Exception as e:
    print(f"Error loading image logic: {e}")
