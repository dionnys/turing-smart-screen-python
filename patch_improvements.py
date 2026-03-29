import os, sys, json, re

MAIN_DIRECTORY = r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python"

# 1. configure.py (JSON Locales + Winreg AutoStart)
configure_py_path = os.path.join(MAIN_DIRECTORY, "configure.py")
with open(configure_py_path, "r", encoding="utf-8") as f:
    conf_code = f.read()

replacement_lang = "import json\nimport os\ntry:\n    with open(MAIN_DIRECTORY + '/locales/es.json', 'r', encoding='utf-8') as f:\n        LANG_DICT = json.load(f)\nexcept:\n    LANG_DICT = {'Author: ': 'Creador: '}"

conf_code = re.sub(
    r"LANG_DICT\s*=\s*\{.*?\}", 
    lambda _: replacement_lang, 
    conf_code, 
    flags=re.DOTALL
)

autostart_logic_read = """        # Cargar estado de inicio en Windows (si la tarea existe)
        if sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ)
                winreg.QueryValueEx(key, "TuringSmartScreen")
                self.autostart_var.set(True)
                winreg.CloseKey(key)
            except:
                self.autostart_var.set(False)"""

autostart_logic_write = """        # Guardar cambio de auto-inicio en Windows
        if sys.platform == "win32":
            try:
                import winreg
                import sys, os
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
                if self.autostart_var.get():
                    exe_path = os.path.join(MAIN_DIRECTORY, "main.exe")
                    if os.path.exists(exe_path):
                        target = f'"{exe_path}"'
                    else:
                        py_path = os.path.join(MAIN_DIRECTORY, "main.py")
                        target = f'"{sys.executable}" "{py_path}"'
                    winreg.SetValueEx(key, "TuringSmartScreen", 0, winreg.REG_SZ, target)
                else:
                    winreg.DeleteValue(key, "TuringSmartScreen")
                winreg.CloseKey(key)
            except Exception as e:
                pass"""

conf_code = re.sub(r"        # Cargar estado de inicio en Windows.*?self\.autostart_var\.set\(False\)", lambda _: autostart_logic_read, conf_code, flags=re.DOTALL)
conf_code = re.sub(r"        # Guardar cambio de auto-inicio en Windows.*?print\(\"Failed to toggle autostart:\", e\)", lambda _: autostart_logic_write, conf_code, flags=re.DOTALL)

with open(configure_py_path, "w", encoding="utf-8") as f:
    f.write(conf_code)
    
# 2. scheduler.py (COM Port Anti-Crash Catch)
scheduler_path = os.path.join(MAIN_DIRECTORY, "library", "scheduler.py")
with open(scheduler_path, "r", encoding="utf-8") as f:
    sched_code = f.read()

sched_code = sched_code.replace(
    "if f:\n            f(*args)",
    "if f:\n            try:\n                f(*args)\n            except Exception as e:\n                print(f'I/O Port Disconnected: {e}')"
)

with open(scheduler_path, "w", encoding="utf-8") as f:
    f.write(sched_code)

print("Patch operations completed!")
