import subprocess
import os

target = f'"{os.path.abspath("main.exe")}"'
print("Target:", target)
args = ["schtasks", "/Create", "/F", "/TN", "TURZX_Monitor_Autostart", "/SC", "ONLOGON", "/RL", "HIGHEST", "/TR", target]
result = subprocess.run(args, capture_output=True, text=True)
print("OUT:", result.stdout)
print("ERR:", result.stderr)
