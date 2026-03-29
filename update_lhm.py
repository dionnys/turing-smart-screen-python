import urllib.request
import zipfile
import os
import shutil

print("--------------------------------------------------")
print("Actualizando LibreHardwareMonitorLib.dll a v0.9.6...")
url = "https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/download/v0.9.6/LibreHardwareMonitor.zip"
urllib.request.urlretrieve(url, "LHM.zip")
with zipfile.ZipFile("LHM.zip", 'r') as zip_ref:
    zip_ref.extractall("LHM_Extracted")
    
import time
try:
    if os.path.exists("external/LibreHardwareMonitor/LibreHardwareMonitorLib.dll"):
        os.rename("external/LibreHardwareMonitor/LibreHardwareMonitorLib.dll", f"external/LibreHardwareMonitor/LibreHardwareMonitorLib.dll.{int(time.time())}.bak")
except Exception:
    pass
shutil.copy("LHM_Extracted/LibreHardwareMonitorLib.dll", "external/LibreHardwareMonitor/LibreHardwareMonitorLib.dll")
os.remove("LHM.zip")
shutil.rmtree("LHM_Extracted")
print("¡Actualizacion exitosa! Ya puedes volver a arrancar python main.py y el sensor leera tu Ryzen 9800X3D correctamente.")
print("--------------------------------------------------")
