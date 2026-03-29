import os

themes_dir = os.path.join("res", "themes")
fixed = 0
for root, dirs, files in os.walk(themes_dir):
    if "theme.yaml" in files:
        p = os.path.join(root, "theme.yaml")
        try:
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            if "PATH: PATH:" in content or "background: \"PATH: " in content:
                content = content.replace("PATH: PATH:", "PATH:")
                content = content.replace("background: \"PATH: ", "background: \"")
                with open(p, "w", encoding="utf-8") as f:
                    f.write(content)
                print("Se corrigió el error de sintaxis en:", p)
                fixed += 1
        except Exception:
            pass

print("Archivos YAML mal formados corregidos:", fixed)
