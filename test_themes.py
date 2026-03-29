import yaml, os

size = "9.2\""
themes = []

for entry in os.scandir('res/themes'):
    if not entry.name.startswith('.') and entry.is_dir():
        p = os.path.join(entry.path, 'theme.yaml')
        if os.path.isfile(p):
            with open(p, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and ('DISPLAY_SIZE' not in data or str(data['DISPLAY_SIZE']) == size):
                    themes.append(entry.name)
                elif data and 'DISPLAY_SIZE' in data:
                    print(f"Mismatched size in {entry.name}: {data['DISPLAY_SIZE']}")

print('Themes found for 9.2":', themes)
