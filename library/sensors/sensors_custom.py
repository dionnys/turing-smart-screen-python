# SPDX-License-Identifier: GPL-3.0-or-later
#
# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/dionnys/turing-smart-screen-python/
#
# Copyright (C) 2021 dionnys (dionnys)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This file allows to add custom data source as sensors and display them in System Monitor themes
# There is no limitation on how much custom data source classes can be added to this file
# See CustomDataExample theme for the theme implementation part

import math
import platform
from abc import ABC, abstractmethod
from typing import List


# Custom data classes must be implemented in this file, inherit the CustomDataSource and implement its 2 methods
class CustomDataSource(ABC):
    @abstractmethod
    def as_numeric(self) -> float:
        # Numeric value will be used for graph and radial progress bars
        # If there is no numeric value, keep this function empty
        pass

    @abstractmethod
    def as_string(self) -> str:
        # Text value will be used for text display and radial progress bar inner text
        # Numeric value can be formatted here to be displayed as expected
        # It is also possible to return a text unrelated to the numeric value
        # If this function is empty, the numeric value will be used as string without formatting
        pass

    @abstractmethod
    def last_values(self) -> List[float]:
        # List of last numeric values will be used for plot graph
        # If you do not want to draw a line graph or if your custom data has no numeric values, keep this function empty
        pass


# Example for a custom data class that has numeric and text values
class ExampleCustomNumericData(CustomDataSource):
    # This list is used to store the last 10 values to display a line graph
    last_val = [math.nan] * 10  # By default, it is filed with math.nan values to indicate there is no data stored

    def as_numeric(self) -> float:
        # Numeric value will be used for graph and radial progress bars
        # Here a Python function from another module can be called to get data
        # Example: self.value = my_module.get_rgb_led_brightness() / audio.system_volume() ...
        self.value = 75.845

        # Store the value to the history list that will be used for line graph
        self.last_val.append(self.value)
        # Also remove the oldest value from history list
        self.last_val.pop(0)

        return self.value

    def as_string(self) -> str:
        # Text value will be used for text display and radial progress bar inner text.
        # Numeric value can be formatted here to be displayed as expected
        # It is also possible to return a text unrelated to the numeric value
        # If this function is empty, the numeric value will be used as string without formatting
        # Example here: format numeric value: add unit as a suffix, and keep 1 digit decimal precision
        return f'{self.value:>5.1f}%'
        # Important note! If your numeric value can vary in size, be sure to display it with a default size.
        # E.g. if your value can range from 0 to 9999, you need to display it with at least 4 characters every time.
        # --> return f'{self.as_numeric():>4}%'
        # Otherwise, part of the previous value can stay displayed ("ghosting") after a refresh

    def last_values(self) -> List[float]:
        # List of last numeric values will be used for plot graph
        return self.last_val


# Example for a custom data class that only has text values
class ExampleCustomTextOnlyData(CustomDataSource):
    def as_numeric(self) -> float:
        # If there is no numeric value, keep this function empty
        pass

    def as_string(self) -> str:
        # If a custom data class only has text values, it won't be possible to display graph or radial bars
        return "Python: " + platform.python_version()

    def last_values(self) -> List[float]:
        # If a custom data class only has text values, it won't be possible to display line graph
        pass

import mmap
import struct

class RTSSFPSData(CustomDataSource):
    last_val = [math.nan] * 10

    def as_numeric(self) -> float:
        try:
            # Abrimos la Memoria Compartida de RTSS (RivaTuner / MSI Afterburner)
            shm = mmap.mmap(-1, 0, "RTSSSharedMemoryV2", access=mmap.ACCESS_READ)
            header = shm[:32]
            sig, ver, app_size, app_count, _, _, osd_size, osd_count = struct.unpack('<8I', header)
            
            if sig == 0x53535452: # Firma binaria 'RTSS'
                offset = 32 + (osd_size * osd_count)
                active_fps = 0.0
                
                for _ in range(app_count):
                    entry = shm[offset : offset + app_size]
                    pid = struct.unpack('<I', entry[0:4])[0]
                    
                    if pid != 0:
                        # El cálculo de framerate de RTSS se calcula como 1 millón de microsegundos sobre el frametime
                        frametime = struct.unpack('<I', entry[276:280])[0]
                        if frametime > 0:
                            fps = 1000000.0 / frametime
                            if fps > active_fps:
                                active_fps = fps
                    
                    offset += app_size
                
                self.value = active_fps
            else:
                self.value = 0.0
                
            shm.close()
        except Exception:
            # Si da error, RTSS no está abierto o no hay juegos
            self.value = 0.0

        self.last_val.append(self.value)
        self.last_val.pop(0)
        return self.value

    def as_string(self) -> str:
        return f'{int(self.as_numeric()):>3} FPS'

    def last_values(self) -> List[float]:
        return self.last_val

class MotherboardFanRPM(CustomDataSource):
    def as_numeric(self) -> float:
        try:
            import library.config as config
            if config.CONFIG_DATA["config"].get("HW_SENSORS", "AUTO") in ["LHM", "AUTO"]:
                import library.sensors.sensors_librehardwaremonitor as lhm
                temp = lhm.Cpu.temperature()
                if temp and temp > 0:
                    # Simulamos el % del ventilador guiado por la temperatura (min 30C = 0%, max 90C = 100%)
                    return min(max((temp - 30) * 1.66, 20.0), 100.0)
            return 0.0
        except Exception:
            return 0.0

    def as_string(self) -> str:
        val = int(self.as_numeric())
        return f'{val}'

    def last_values(self) -> List[float]:
        return []

class MotherboardPumpRPM(CustomDataSource):
    def as_numeric(self) -> float:
        try:
            import library.config as config
            if config.CONFIG_DATA["config"].get("HW_SENSORS", "AUTO") in ["LHM", "AUTO"]:
                import library.sensors.sensors_librehardwaremonitor as lhm
                temp = lhm.Gpu.stats()[4]
                if temp and temp > 0:
                    # Simulamos el % de la bomba guiada por el GPU (min 30C = 30%, max 80C = 100%)
                    return min(max((temp - 30) * 1.66 + 30.0, 30.0), 100.0)
            return 0.0
        except Exception:
            return 0.0

    def as_string(self) -> str:
        val = int(self.as_numeric())
        return f'{val}'

    def last_values(self) -> List[float]:
        return []

class UserProfile(CustomDataSource):
    def as_numeric(self) -> float:
        return 0.0

    def as_string(self) -> str:
        import socket
        import library.config as config
        
        hud_type = config.CONFIG_DATA.get('config', {}).get('ARC_HUD_TEXT_TYPE', 'HOSTNAME')
        
        if hud_type == "IP":
            # If IP is requested, we try to use the cached IP from PublicIP sensor if available
            try:
                from library.sensors.sensors_custom import PublicIP
                return PublicIP().as_string().replace("IP: ", "")
            except:
                return "IP Unknown"
        
        try:
            return socket.gethostname().upper()
        except:
            return "HOST"

    def last_values(self) -> List[float]:
        return []

class UserFlag(CustomDataSource):
    _last_country = None
    
    def as_numeric(self) -> float:
        return 0.0

    def as_string(self) -> str:
        import os
        import urllib.request
        import library.config as config
        
        theme_data = config.THEME_DATA['STATS']['CUSTOM'].get('UserFlag', {})
        country = theme_data.get('COUNTRY_CODE', 've').lower()
        
        cache_dir = "res/flags"
        if not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir)
            except:
                pass
            
        flag_path = os.path.join(cache_dir, f"{country}.png")
        
        # Download the requested flag locally over http mapping dynamically
        if not os.path.exists(flag_path) or UserFlag._last_country != country:
            try:
                url = f"https://flagcdn.com/w40/{country}.png"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    with open(flag_path, 'wb') as f:
                        f.write(response.read())
                UserFlag._last_country = country
            except Exception:
                pass
                
        return flag_path if os.path.exists(flag_path) else ""

    def last_values(self) -> List[float]:
        return []

class PublicIP(CustomDataSource):
    _cached_ip = None
    _last_checked = 0
    
    def as_numeric(self) -> float:
        return 0.0

    def as_string(self) -> str:
        import time
        if PublicIP._cached_ip is None or time.time() - PublicIP._last_checked > 300:
            try:
                import urllib.request
                req = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    PublicIP._cached_ip = response.read().decode('utf-8').strip()
                PublicIP._last_checked = time.time()
            except:
                if PublicIP._cached_ip is None:
                    PublicIP._cached_ip = "IP Unknown"
        return f"{PublicIP._cached_ip}"

    def last_values(self) -> List[float]:
        return []

class CPUPower(CustomDataSource):
    def as_numeric(self) -> float:
        try:
            import mmap, ctypes
            # Core Temp Mapping Object (Memoria Compartida)
            shm = mmap.mmap(-1, 4096, "CoreTempMappingObject", access=mmap.ACCESS_READ)
            mem = shm.read()
            shm.close()

            # Estructura: Load(256*4) + fTemp(256*4) ... etc.
            # En la versión 1.19.5, la potencia (fPower) está distribuida en slots de 4 bytes.
            # El offset habitual para el consumo de Package en Ryzen es 2048 o 4000.
            
            pwr = ctypes.c_float.from_buffer_copy(mem, 2048).value
            
            if pwr <= 0.0 or pwr > 1000.0:
                # Buscamos en un rango más amplio si el offset estándar no devuelve nada
                for offset in range(1500, 4000, 4):
                    try:
                        val = ctypes.c_float.from_buffer_copy(mem, offset).value
                        if 10.0 < val < 500.0: # Un rango coherente para el 9800X3D
                            return val
                    except: continue
                
            return pwr if pwr > 0 else 0.0
        except Exception:
            return 0.0

    def as_string(self) -> str:
        val = self.as_numeric()
        return f'{val:>5.1f}W'

    def last_values(self) -> List[float]:
        return []

class GPUPower(CustomDataSource):
    def as_numeric(self) -> float:
        try:
            import library.sensors.sensors_librehardwaremonitor as lhm
            gpu = lhm.Gpu.get_gpu_to_use()
            if gpu:
                from LibreHardwareMonitor import Hardware as hw
                gpu.Update()
                for sensor in gpu.Sensors:
                    if sensor.SensorType == hw.SensorType.Power:
                        return float(sensor.Value)
            return 0.0
        except Exception:
            return 0.0

    def as_string(self) -> str:
        val = self.as_numeric()
        return f'{val:>5.1f}W'

    def last_values(self) -> List[float]:
        return []


class SystemVolume(CustomDataSource):
    """Lee el volumen maestro del sistema Windows via pycaw / Core Audio API."""

    def as_numeric(self) -> float:
        try:
            import comtypes
            comtypes.CoInitialize()
            from pycaw.pycaw import AudioUtilities
            
            devices = AudioUtilities.GetSpeakers()
            if not devices or not hasattr(devices, 'EndpointVolume'):
                return 0.0
                
            volume = devices.EndpointVolume
            if volume.GetMute():
                return 0.0
            return round(volume.GetMasterVolumeLevelScalar() * 100, 1)
        except Exception as e:
            from library.log import logger
            logger.debug(f"Volume numeric error: {e}")
            return 0.0

    def as_string(self) -> str:
        try:
            import comtypes
            comtypes.CoInitialize()
            from pycaw.pycaw import AudioUtilities
            
            devices = AudioUtilities.GetSpeakers()
            if not devices or not hasattr(devices, 'EndpointVolume'):
                return " N/A"
                
            volume = devices.EndpointVolume
            if volume.GetMute():
                return " MUTE"
            level = int(volume.GetMasterVolumeLevelScalar() * 100)
            return f"{level:>3}%VOL"
        except Exception as e:
            from library.log import logger
            logger.debug(f"Volume string error: {e}")
            return " N/A"

    def last_values(self) -> List[float]:
        return []
