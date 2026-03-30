import os

with open("configure.py", "r", encoding="utf-8") as f:
    text = f.read()

LANG_DICT = {
    'Turing Smart Screen configuration': 'Configuración de Turing Smart Screen',
    'Display configuration': 'Configuración de pantalla',
    'Smart screen model': 'Modelo de pantalla',
    'Smart screen size': 'Tamaño de pantalla',
    'COM port': 'Puerto COM',
    'Orientation': 'Orientación',
    'Brightness': 'Brillo',
    'Turing Smart Screen Configuration': 'Configuración de Turing Smart Screen',
    'Theme': 'Tema',
    'Hardware monitoring': 'Sensor de hardware',
    'Ethernet interface': 'Interfaz Ethernet',
    'Wi-Fi interface': 'Interfaz Wi-Fi',
    'CPU fan (？)': 'Ventilador CPU (？)',
    'Run monitor at Windows startup': 'Iniciar monitor al encender Windows',
    'Hide system tray icon': 'Ocultar icono de bandeja',
    'Weather & ping': 'Clima y Ping',
    'Open themes\\nfolder': 'Abrir carpeta\\nde temas',
    'Edit theme': 'Editar tema',
    'Save settings': 'Guardar ajustes',
    'Save and run': 'Guardar y ejecutar',
    'Configure weather & ping': 'Configurar clima y ping',
    'Hostname / IP to ping': 'Hostname / IP a verificar (ping)',
    'Weather forecast (OpenWeatherMap API)': 'Pronóstico del clima (API OpenWeatherMap)',
    'To display weather forecast on themes that support it, you need an OpenWeatherMap "One Call API 3.0" key.\\nYou will get 1,000 API calls per day for free. This program is configured to stay under this threshold (~300 calls/day).': 'Para mostrar el clima necesitas una API Key de OpenWeatherMap "One Call API 3.0".\\nObtienes 1000 llamadas gratis al día. El programa gasta ~300 para no exceder el límite.',
    'Click here to subscribe to OpenWeatherMap One Call API 3.0.': 'Haz clic aquí para suscribirte a OpenWeatherMap One Call API 3.0.',
    'OpenWeatherMap API key': 'API Key gratuita',
    'You can use online services to get your latitude/longitude e.g. latlong.net (click here)': 'Puedes usar sitios web como latlong.net para obtener tu latitud/longitud (clic aquí)',
    'Latitude': 'Latitud',
    'Longitude': 'Longitud',
    'Units': 'Unidades',
    'Language': 'Idioma del clima',
    'Location search': 'Buscador de ubicación',
    'Enter location to automatically get coordinates (latitude/longitude).\\nFor example "Berlin" "London, GB", "London, Quebec".\\nRemember to set valid API key and pick language first!': 'Ingresa tu ubicación para buscar las coordenadas.\\nEjemplo: "Madrid", "Santiago, CL".\\n⚠️ ¡Primero ingresa tu API Key arriba!',
    'Enter location': 'Buscar nombre de ciudad',
    'Search': 'Buscar a nivel global',
    'Select location\\n(use after Search)': 'Elige la ciudad\\n(aparece tras buscar)',
    'Fill in lat/long': 'Autocompletar',
    '⚠ Turing 3.5" displays can get hot at high brightness!': '⚠ ¡Las pantallas de 3.5" se calientan mucho con el brillo al máximo!',
    '❌ Restart as admin. or select another Hardware monitoring': '❌ Reinicia el .exe como Administrador o usa otro Sensor',
    'Automatic detection': 'Detección automática',
    'Automatic': 'Automático',
    'None': 'Ninguno',
}

translation_block = f"""
import ctypes
import locale

try:
    lang_code = locale.getdefaultlocale()[0]
except:
    lang_code = "en"
if lang_code is None:
    lang_code = "en"

# Detect if we should use Spanish
USE_ES = "es" in lang_code.lower()

LANG_DICT = {repr(LANG_DICT)}

def T(english_text):
    if USE_ES:
        return LANG_DICT.get(english_text, english_text)
    return english_text

"""

parts = text.split('hw_lib_map = {"AUTO"', 1)

if len(parts) == 2:
    new_text = parts[0] + translation_block + 'hw_lib_map = {"AUTO"' + parts[1]
    
    for k in LANG_DICT.keys():
        new_text = new_text.replace(f"self.window.title('{k}')", f"self.window.title(T('{k}'))")
        
        # UI exact matches
        new_text = new_text.replace(f"text='{k}'", f"text=T('{k}')")
        new_text = new_text.replace(f'text="{k}"', f'text=T("{k}")')
        
    # Manual injections
    new_text = new_text.replace('com_ports_names = ["Automatic detection"]', 'com_ports_names = [T("Automatic detection")]')
    new_text = new_text.replace('if_list.insert(0, "None")', 'if_list.insert(0, T("None"))')
    new_text = new_text.replace('auto_detected_cpu_fan = "None"', 'auto_detected_cpu_fan = T("None")')
    new_text = new_text.replace('hw_lib_map = {"AUTO": "Automatic",', 'hw_lib_map = {"AUTO": T("Automatic"),')
    
    with open("configure.py", "w", encoding="utf-8") as f:
        f.write(new_text)
    print("Traducido exitosamente.")
else:
    print("Fallo dividiendo configure.py")
