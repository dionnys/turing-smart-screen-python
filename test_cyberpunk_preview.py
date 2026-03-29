import os
import ruamel.yaml

MAIN_DIRECTORY = r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python"
THEMES_DIR = os.path.join(MAIN_DIRECTORY, 'res/themes')

def test_yaml(theme_name):
    theme = os.path.join(THEMES_DIR, theme_name, 'theme.yaml')
    with open(theme, "rt", encoding='utf8') as stream:
        try:
            data, _, _ = ruamel.yaml.util.load_yaml_guess_indent(stream)
            print(f"{theme_name} -> SUCCESS. Keys: {list(data.keys()) if data else 'None'}")
        except Exception as e:
            print(f"{theme_name} -> FAILED: {e}")

test_yaml("9.2inch_Cyberpunk")
test_yaml("9.2inch_BLUE")
test_yaml("9.2inch_TechnologyX")
