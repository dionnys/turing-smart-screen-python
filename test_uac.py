import ctypes
import os
exe_path = os.path.abspath("main.exe")
target = f'\\"{exe_path}\\"'
params = f'/Create /F /TN "TURZX_Monitor_Autostart" /TR "{target}" /SC ONLOGON /RL HIGHEST'
print(params)
res = ctypes.windll.shell32.ShellExecuteW(None, "runas", "schtasks.exe", params, None, 0)
print(res)
