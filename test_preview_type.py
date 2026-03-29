import os
import ruamel.yaml

MAIN_DIRECTORY = r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python"
THEMES_DIR = os.path.join(MAIN_DIRECTORY, 'res/themes')

def get_theme_data(name: str):
    dir = os.path.join(THEMES_DIR, name)
    theme = os.path.join(dir, 'theme.yaml')
    with open(theme, "rt", encoding='utf8') as stream:
        theme_data, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(stream)
        return theme_data

target_themes = ["Assassin's Creed", "9.2inch_Cyberpunk", "9.2inch_TechnologyX", "ARC_Raiders_v1"]

for theme_name in target_themes:
    try:
        data = get_theme_data(theme_name)
        if data and 'display' in data:
            val = data['display'].get("DISPLAY_SIZE", '3.5"')
            print(f"[{theme_name}] DISPLAY_SIZE -> Type: {type(val)}, Repr: {repr(val)}")
        else:
            print(f"[{theme_name}] DISPLAY_SIZE not found!")
    except Exception as e:
        print(f"[{theme_name}] Error: {e}")
