import os
import ctypes

if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    print("¡ATENCIÓN! No estás como Administrador. Los sensores saldrán vacíos.")

import clr
clr.AddReference(os.getcwd() + "\\external\\LibreHardwareMonitor\\LibreHardwareMonitorLib.dll")
clr.AddReference(os.getcwd() + "\\external\\LibreHardwareMonitor\\HidSharp.dll")
from LibreHardwareMonitor import Hardware

handle = Hardware.Computer()
handle.IsCpuEnabled = True
handle.IsMotherboardEnabled = True
handle.Open()

with open("debug.txt", "w", encoding="utf-8") as f:
    for hardware in handle.Hardware:
        hardware.Update()
        f.write(f"Hardware: {hardware.Name} (Type: {hardware.HardwareType})\n")
        for sensor in hardware.Sensors:
            f.write(f"  [{sensor.SensorType}] {sensor.Name}: {sensor.Value}\n")
        for subh in hardware.SubHardware:
            subh.Update()
            f.write(f"  SubHardware: {subh.Name} (Type: {subh.HardwareType})\n")
            for sensor in subh.Sensors:
                f.write(f"    [{sensor.SensorType}] {sensor.Name}: {sensor.Value}\n")
        f.write("\n")
        
print("Archivo debug.txt generado con éxito.")
