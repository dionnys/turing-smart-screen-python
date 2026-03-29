import os
import re

# Lee el tema maestro que programamos a mano (ARC_Raiders)
master_theme_path = os.path.join("res", "themes", "ARC_Raiders", "theme.yaml")
with open(master_theme_path, "r", encoding="utf-8") as f:
    master_yaml = f.read()

themes_dir = os.path.join("res", "themes")
fixed_count = 0

print("Buscando temas rotos y vacíos...")

for theme_name in os.listdir(themes_dir):
    theme_path = os.path.join(themes_dir, theme_name)
    if not os.path.isdir(theme_path) or theme_name == "ARC_Raiders":
        continue
        
    yaml_path = os.path.join(theme_path, "theme.yaml")
    if not os.path.exists(yaml_path):
        continue
        
    # Leer el theme.yaml de destino
    with open(yaml_path, "r", encoding="utf-8") as f:
        target_content = f.read()
        
    # Si el archivo tiene menos de 80 líneas, significa que es un cascarón vacío de XuanFang
    if len(target_content.splitlines()) < 80:
        # Extraer el nombre real de la imagen de fondo (ej: 'theme_res_1002872.png')
        bg_match = re.search(r"background:\s*['\"]?(.*?\.png)['\"]?", target_content)
        if bg_match:
            bg_name = bg_match.group(1)
            
            # Reemplazar la foto de fondo genérica por la del tema en el código maestro
            new_yaml = master_yaml.replace("background.png", bg_name)
            
            # Sobreescribir el tema roto con toda nuestra inmensa programación
            with open(yaml_path, "w", encoding="utf-8") as f:
                f.write(new_yaml)
                
            print(f"Tema reparado: {theme_name} (Fondo enlazado: {bg_name})")
            fixed_count += 1

print("--------------------------------------------------")
print(f"¡Magia completada! Se repararon {fixed_count} temas rotos exitosamente clonando la estructura de ARC Raiders.")
