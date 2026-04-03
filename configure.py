#!/usr/bin/env python
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

# This file is the system monitor configuration GUI

from library.pythoncheck import check_python_version
check_python_version()

import glob
import os
import platform
import subprocess
import sys
import webbrowser
import requests
import babel

try:
    import tkinter.ttk as ttk
    from tkinter import *
    from PIL import ImageTk
    import psutil
    import ruamel.yaml
    import sv_ttk
    from pathlib import Path
    from PIL import Image
    from serial.tools.list_ports import comports
    from tktooltip import ToolTip
except Exception as e:
    print("""Import error: %s
Please follow start guide to install required packages: https://github.com/dionnys/turing-smart-screen-python/wiki/System-monitor-:-how-to-start
Or the troubleshooting page: https://github.com/dionnys/turing-smart-screen-python/wiki/Troubleshooting#all-os-tkinter-dependency-not-installed""" % str(
        e))
    try:
        sys.exit(0)
    except:
        os._exit(0)

from library.sensors.sensors_python import sensors_fans, is_cpu_fan

TURING_MODEL = "Turing Smart Screen"
USBPCMONITOR_MODEL = "UsbPCMonitor"
XUANFANG_MODEL = "XuanFang rev. B & flagship"
KIPYE_MODEL = "Kipye Qiye Smart Display"
WEACT_MODEL = "WeAct Studio Display FS V1"
SIMULATED_MODEL = "Simulated screen"

SIZE_3_5_INCH = "3.5\""
SIZE_5_INCH = "5\""
SIZE_8_8_INCH = "8.8\""
SIZE_9_2_INCH = "9.2\""
SIZE_2_1_INCH = "2.1\""  # Only for retro compatibility
SIZE_2_x_INCH = "2.1\" / 2.8\""
SIZE_0_96_INCH = "0.96\""

size_list = (SIZE_0_96_INCH, SIZE_2_x_INCH, SIZE_3_5_INCH, SIZE_5_INCH, SIZE_8_8_INCH, SIZE_9_2_INCH)

# Maps between config.yaml values and GUI description
revision_and_size_to_model_map = {
    ('A', SIZE_3_5_INCH): TURING_MODEL,  # Can also be UsbPCMonitor 3.5, does not matter since protocol is the same
    ('A', SIZE_5_INCH): USBPCMONITOR_MODEL,
    ('B', SIZE_3_5_INCH): XUANFANG_MODEL,
    ('C', SIZE_2_x_INCH): TURING_MODEL,
    ('C', SIZE_5_INCH): TURING_MODEL,
    ('C', SIZE_8_8_INCH): TURING_MODEL,
    ('C', SIZE_9_2_INCH): TURING_MODEL,
    ('D', SIZE_3_5_INCH): KIPYE_MODEL,
    ('WEACT_A', SIZE_3_5_INCH): WEACT_MODEL,
    ('WEACT_B', SIZE_0_96_INCH): WEACT_MODEL,
    ('SIMU', SIZE_0_96_INCH): SIMULATED_MODEL,
    ('SIMU', SIZE_2_x_INCH): SIMULATED_MODEL,
    ('SIMU', SIZE_3_5_INCH): SIMULATED_MODEL,
    ('SIMU', SIZE_5_INCH): SIMULATED_MODEL,
    ('SIMU', SIZE_8_8_INCH): SIMULATED_MODEL,
    ('SIMU', SIZE_9_2_INCH): SIMULATED_MODEL,
}
model_and_size_to_revision_map = {
    (TURING_MODEL, SIZE_3_5_INCH): 'A',
    (USBPCMONITOR_MODEL, SIZE_3_5_INCH): 'A',
    (USBPCMONITOR_MODEL, SIZE_5_INCH): 'A',
    (XUANFANG_MODEL, SIZE_3_5_INCH): 'B',
    (TURING_MODEL, SIZE_2_x_INCH): 'C',
    (TURING_MODEL, SIZE_5_INCH): 'C',
    (TURING_MODEL, SIZE_8_8_INCH): 'C',
    (TURING_MODEL, SIZE_9_2_INCH): 'C',
    (KIPYE_MODEL, SIZE_3_5_INCH): 'D',
    (WEACT_MODEL, SIZE_3_5_INCH): 'WEACT_A',
    (WEACT_MODEL, SIZE_0_96_INCH): 'WEACT_B',
    (SIMULATED_MODEL, SIZE_0_96_INCH): 'SIMU',
    (SIMULATED_MODEL, SIZE_2_x_INCH): 'SIMU',
    (SIMULATED_MODEL, SIZE_3_5_INCH): 'SIMU',
    (SIMULATED_MODEL, SIZE_5_INCH): 'SIMU',
    (SIMULATED_MODEL, SIZE_8_8_INCH): 'SIMU',
    (SIMULATED_MODEL, SIZE_9_2_INCH): 'SIMU',
}

import ctypes
import locale

import sys
from pathlib import Path
if getattr(sys, 'frozen', False):
    MAIN_DIRECTORY = str(Path(sys.executable).parent.resolve()) + "/"
else:
    MAIN_DIRECTORY = str(Path(__file__).parent.resolve()) + "/"

try:
    lang_code = locale.getlocale()[0] or "en"
except:
    lang_code = "en"
if lang_code is None:
    lang_code = "en"

# MAGIC: Force APP_LANGUAGE override manually
try:
    import ruamel.yaml
    with open(MAIN_DIRECTORY + "config.yaml", "rt", encoding='utf8') as stream:
        early_config, _, _ = ruamel.yaml.util.load_yaml_guess_indent(stream)
        if 'APP_LANGUAGE' in early_config['config']:
            lang_code = early_config['config']['APP_LANGUAGE']
except:
    pass

# Detect if we should use Spanish
USE_ES = "es" in lang_code.lower()

import json
import os
try:
    with open(MAIN_DIRECTORY + '/locales/es.json', 'r', encoding='utf-8') as f:
        LANG_DICT = json.load(f)
except:
    LANG_DICT = {'Author: ': 'Creador: '}

def T(english_text):
    if USE_ES:
        return LANG_DICT.get(english_text, english_text)
    return english_text

hw_lib_map = {"AUTO": T("Automatic"), "LHM": "LibreHardwareMonitor (admin.)", "PYTHON": "Python libraries",
              "STUB": "Fake random data", "STATIC": "Fake static data"}
reverse_map = {False: "classic", True: "reverse"}
weather_unit_map = {"metric": "metric - °C", "imperial": "imperial - °F", "standard": "standard - °K"}
weather_lang_map = {"sq": "Albanian", "af": "Afrikaans", "ar": "Arabic", "az": "Azerbaijani", "eu": "Basque",
                    "be": "Belarusian", "bg": "Bulgarian", "ca": "Catalan", "zh_cn": "Chinese Simplified",
                    "zh_tw": "Chinese Traditional", "hr": "Croatian", "cz": "Czech", "da": "Danish", "nl": "Dutch",
                    "en": "English", "fi": "Finnish", "fr": "French", "gl": "Galician", "de": "German", "el": "Greek",
                    "he": "Hebrew", "hi": "Hindi", "hu": "Hungarian", "is": "Icelandic", "id": "Indonesian",
                    "it": "Italian", "ja": "Japanese", "kr": "Korean", "ku": "Kurmanji (Kurdish)", "la": "Latvian",
                    "lt": "Lithuanian", "mk": "Macedonian", "no": "Norwegian", "fa": "Persian (Farsi)", "pl": "Polish",
                    "pt": "Portuguese", "pt_br": "Português Brasil", "ro": "Romanian", "ru": "Russian", "sr": "Serbian",
                    "sk": "Slovak", "sl": "Slovenian", "sp": "Spanish", "sv": "Swedish", "th": "Thai", "tr": "Turkish",
                    "ua": "Ukrainian", "vi": "Vietnamese", "zu": "Zulu"}

THEMES_DIR = MAIN_DIRECTORY + 'res/themes'

circular_mask = Image.open(MAIN_DIRECTORY + "res/backgrounds/circular-mask.png")

def get_theme_data(name: str):
    dir = os.path.join(THEMES_DIR, name)
    # checking if it is a directory
    if os.path.isdir(dir):
        # Check if a theme.yaml file exists
        theme = os.path.join(dir, 'theme.yaml')
        if os.path.isfile(theme):
            # Get display size from theme.yaml
            with open(theme, "rt", encoding='utf8') as stream:
                theme_data, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(stream)
                return theme_data
    return None


def get_themes(size: str):
    themes = []
    for filename in os.listdir(THEMES_DIR):
        theme_data = get_theme_data(filename)
        if theme_data and theme_data['display'].get("DISPLAY_SIZE", '3.5"') == size:
            themes.append(filename)
    return sorted(themes, key=str.casefold)


def get_theme_size(name: str) -> str:
    theme_data = get_theme_data(name)
    return theme_data['display'].get("DISPLAY_SIZE", '3.5"')


def get_com_ports():
    com_ports_names = [T("Automatic detection")]  # Add manual entry on top for automatic detection
    com_ports = comports()
    for com_port in com_ports:
        com_ports_names.append(com_port.name)
    return com_ports_names


def get_net_if():
    if_list = list(psutil.net_if_addrs().keys())
    if_list.insert(0, T("None"))  # Add manual entry on top for unavailable/not selected interface
    return if_list


def get_fans():
    fan_list = list()
    auto_detected_cpu_fan = T("None")
    for name, entries in sensors_fans().items():
        for entry in entries:
            fan_list.append("%s/%s (%d%% - %d RPM)" % (name, entry.label, entry.percent, entry.current))
            if (is_cpu_fan(entry.label) or is_cpu_fan(name)) and auto_detected_cpu_fan == "None":
                auto_detected_cpu_fan = "Auto-detected: %s/%s" % (name, entry.label)

    fan_list.insert(0, auto_detected_cpu_fan)  # Add manual entry on top if auto-detection succeeded
    return fan_list


class TuringConfigWindow:
    def __init__(self):
        self.window = Tk()
        self.window.title(T('Turing Smart Screen configuration'))
        self.window.geometry("840x820")
        self.window.iconphoto(True, PhotoImage(file=MAIN_DIRECTORY + "res/icons/monitor-icon-17865/64.png"))
        # When window gets focus again, reload theme preview in case it has been updated by theme editor
        self.window.bind("<FocusIn>", self.on_theme_change)
        self.window.after(0, self.on_fan_speed_update)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Subwindow for weather/ping config.
        self.more_config_window = MoreConfigWindow(self)

        # Make TK look better with Sun Valley ttk theme
        sv_ttk.set_theme("light")

        self.theme_preview_img = None
        self.theme_preview = ttk.Label(self.window)
        self.theme_preview.place(x=10, y=10)

        self.theme_author = ttk.Label(self.window)

        self.sysmon_label1 = ttk.Label(self.window, text=T('Display configuration'), font='bold')
        self.sysmon_label1.place(x=370, y=0)

        self.model_label = ttk.Label(self.window, text=T('Smart screen model'))
        self.model_label.place(x=370, y=35)
        self.model_cb = ttk.Combobox(self.window, values=list(dict.fromkeys((revision_and_size_to_model_map.values()))),
                                     state='readonly')
        self.model_cb.bind('<<ComboboxSelected>>', self.on_model_change)
        self.model_cb.place(x=550, y=30, width=250)

        self.size_label = ttk.Label(self.window, text=T('Smart screen size'))
        self.size_label.place(x=370, y=75)
        self.size_cb = ttk.Combobox(self.window, values=size_list, state='readonly')
        self.size_cb.bind('<<ComboboxSelected>>', self.on_size_change)
        self.size_cb.place(x=550, y=70, width=250)

        self.com_label = ttk.Label(self.window, text=T('COM port'))
        self.com_label.place(x=370, y=115)
        self.com_cb = ttk.Combobox(self.window, values=get_com_ports(), state='readonly')
        self.com_cb.place(x=550, y=110, width=250)

        self.orient_label = ttk.Label(self.window, text=T('Orientation'))
        self.orient_label.place(x=370, y=155)
        self.orient_cb = ttk.Combobox(self.window, values=list(reverse_map.values()), state='readonly')
        self.orient_cb.place(x=550, y=150, width=250)

        self.brightness_string = StringVar()
        self.brightness_label = ttk.Label(self.window, text=T('Brightness'))
        self.brightness_label.place(x=370, y=195)
        self.brightness_slider = ttk.Scale(self.window, from_=0, to=100, orient=HORIZONTAL,
                                           command=self.on_brightness_change)
        self.brightness_slider.place(x=600, y=195, width=180)
        self.brightness_val_label = ttk.Label(self.window, textvariable=self.brightness_string)
        self.brightness_val_label.place(x=550, y=195)
        self.brightness_warning_label = ttk.Label(self.window,
                                                  text="⚠ Turing 3.5\" displays can get hot at high brightness!",
                                                  foreground='#ff8c00')

        self.sysmon_label2 = ttk.Label(self.window, text=T('Turing Smart Screen Configuration'), font='bold')
        self.sysmon_label2.place(x=370, y=260)

        self.theme_label = ttk.Label(self.window, text=T('Theme'))
        self.theme_label.place(x=370, y=300)
        self.theme_cb = ttk.Combobox(self.window, state='readonly')
        self.theme_cb.place(x=550, y=295, width=250)
        self.theme_cb.bind('<<ComboboxSelected>>', self.on_theme_change)

        self.hwlib_label = ttk.Label(self.window, text=T('Hardware monitoring'))
        self.hwlib_label.place(x=370, y=340)
        if sys.platform != "win32":
            del hw_lib_map["LHM"]  # LHM is for Windows platforms only
        self.hwlib_cb = ttk.Combobox(self.window, values=list(hw_lib_map.values()), state='readonly')
        self.hwlib_cb.place(x=550, y=335, width=250)
        self.hwlib_cb.bind('<<ComboboxSelected>>', self.on_hwlib_change)

        self.eth_label = ttk.Label(self.window, text=T('Ethernet interface'))
        self.eth_label.place(x=370, y=380)
        self.eth_cb = ttk.Combobox(self.window, values=get_net_if(), state='readonly')
        self.eth_cb.place(x=550, y=375, width=250)

        self.wl_label = ttk.Label(self.window, text=T('Wi-Fi interface'))
        self.wl_label.place(x=370, y=420)
        self.wl_cb = ttk.Combobox(self.window, values=get_net_if(), state='readonly')
        self.wl_cb.place(x=550, y=415, width=250)

        # For Windows platform only
        self.lhm_admin_warning = ttk.Label(self.window,
                                           text=T("❌ Restart as admin. or select another Hardware monitoring"),
                                           foreground='#f00')
        # For platform != Windows
        self.cpu_fan_label = ttk.Label(self.window, text=T('CPU fan (？)'))
        self.cpu_fan_label.config(foreground="#a3a3ff", cursor="hand2")
        self.cpu_fan_cb = ttk.Combobox(self.window, values=get_fans(), state='readonly')

        self.tooltip = ToolTip(self.cpu_fan_label,
                               msg="If \"None\" is selected, CPU fan was not auto-detected.\n"
                                   "Manually select your CPU fan from the list.\n\n"
                                   "Fans missing from the list? Install lm-sensors package\n"
                                   "and run 'sudo sensors-detect' command, then reboot.")

        self.autostart_var = BooleanVar()
        self.autostart_checkbox = ttk.Checkbutton(self.window, text=T("Run monitor at Windows startup"), variable=self.autostart_var)

        self.tray_hidden_var = BooleanVar()
        self.tray_hidden_checkbox = ttk.Checkbutton(self.window, text=T("Hide system tray icon"), variable=self.tray_hidden_var)

        self.show_date_time_var = BooleanVar()
        self.show_date_time_checkbox = ttk.Checkbutton(self.window, text=T("Show Time & Date everywhere"), variable=self.show_date_time_var)

        self.show_weather_var = BooleanVar()
        self.show_weather_checkbox = ttk.Checkbutton(self.window, text=T("Show Weather everywhere"), variable=self.show_weather_var)

        self.show_arc_hud_var = BooleanVar()
        self.show_arc_hud_checkbox = ttk.Checkbutton(self.window, text=T("Show VIP HUD (Flag/Hostname/IP)"), variable=self.show_arc_hud_var)

        # HUD Text Type and Flag Selector (REORGANIZED)
        # Column 1: App Settings & HUD (Stacked Vertically)
        if sys.platform == "win32":
            self.autostart_checkbox.place(x=370, y=485)
            self.tray_hidden_checkbox.place(x=370, y=515)
            self.show_date_time_checkbox.place(x=370, y=545)
            self.show_weather_checkbox.place(x=370, y=575)
            self.show_arc_hud_checkbox.place(x=370, y=605)
        else:
            self.tray_hidden_checkbox.place(x=370, y=485)
            self.show_date_time_checkbox.place(x=370, y=515)
            self.show_weather_checkbox.place(x=370, y=545)
            self.show_arc_hud_checkbox.place(x=370, y=575)

        # HUD Inputs (Shifted right slightly but still in the same vertical block)
        self.arc_hud_type_label = ttk.Label(self.window, text=T("HUD Text:"))
        self.arc_hud_type_label.place(x=370, y=650)
        self.arc_hud_type_cb = ttk.Combobox(self.window, values=["HOSTNAME", "IP"], state='readonly')
        self.arc_hud_type_cb.place(x=500, y=645, width=100)

        self.arc_hud_flag_label = ttk.Label(self.window, text=T("Flag (ISO):"))
        self.arc_hud_flag_label.place(x=370, y=685)
        self.arc_hud_flag_entry = ttk.Entry(self.window)
        self.arc_hud_flag_entry.place(x=500, y=680, width=100)

        # Selector de Interfaz de App Language (Movido a la zona roja)
        self.widget_config_btn = ttk.Button(self.window, text=T("Widget"),
                                           command=lambda: self.on_widget_config_click())
        self.widget_config_btn.place(x=650, y=485, height=45, width=150)

        # Selector de Interfaz de App Language
        self.app_lang_label = ttk.Label(self.window, text="Interface / Idioma:")
        self.app_lang_label.place(x=650, y=550)
        self.app_lang_cb = ttk.Combobox(self.window, values=["English", "Español"], state='readonly')
        self.app_lang_cb.place(x=650, y=580, width=150)
        self.app_lang_cb.bind('<<ComboboxSelected>>', self.on_app_lang_change)

        self.lhm_admin_warning = ttk.Label(self.window, text="❌ " + T("Run as Administrator to enable this sensor"), foreground="red")
        self.lhm_admin_warning.place(x=370, y=725)
        
        # Botonera inferior (Centered for 840px width)
        self.weather_ping_btn = ttk.Button(self.window, text=T("Weather & ping"), command=lambda: self.on_weatherping_click())
        self.weather_ping_btn.place(x=20, y=760, width=155)

        self.open_theme_folder_btn = ttk.Button(self.window, text=T("Browse themes"), command=lambda: self.on_open_theme_folder_click())
        self.open_theme_folder_btn.place(x=185, y=760, width=155)

        self.edit_theme_btn = ttk.Button(self.window, text=T("Editor"), command=lambda: self.on_theme_editor_click())
        self.edit_theme_btn.place(x=350, y=760, width=155)

        self.save_btn = ttk.Button(self.window, text=T("Save settings"), command=lambda: self.on_save_click())
        self.save_btn.place(x=515, y=760, width=155)

        self.save_run_btn = ttk.Button(self.window, text=T("Save and launch"), command=lambda: self.on_saverun_click())
        self.save_run_btn.place(x=680, y=760, width=155)

        self.config = None
        
        # Subwindow for Widget Config
        self.widget_config_window = WidgetConfigWindow(self)
        
        self.load_config_values()
        self.check_core_temp_suggestion()

    def check_core_temp_suggestion(self):
        import tkinter.messagebox as messagebox
        import winreg, os
        if self.config and self.config.get('config', {}).get('HW_SENSORS') == 'LHM':
            loc = None
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Core Temp") as key:
                    loc, _ = winreg.QueryValueEx(key, "InstallLocation")
            except: pass
            if not loc and not os.path.exists(r"C:\Program Files\Core Temp\Core Temp.exe") and not os.path.exists(r"C:\Program Files (x86)\Core Temp\Core Temp.exe"):
                messagebox.showinfo("Recomendación de Lectura", 
                    "Para capturar correctamente la temperatura real de procesadores recientes (AMD Ryzen/Intel) "
                    "sin que la seguridad de Windows te lo devuelva en 0°C, sugerimos instalar el programa libre 'Core Temp'.\n\n"
                    "¡Una vez instalado, el monitor Turing se conectará a él automáticamente y lo lanzará de fondo!")

    def on_close(self):
        """Guarda y cierra directamente sin pedir confirmación."""
        self.save_config_values()
        self.window.destroy()

    def run(self):
        self.window.mainloop()

    def load_theme_preview(self):
        theme_data = get_theme_data(self.theme_cb.get())

        try:
            theme_preview = Image.open(MAIN_DIRECTORY + "res/themes/" + self.theme_cb.get() + "/preview.png")

            if theme_data['display'].get("DISPLAY_SIZE", '3.5"') == SIZE_2_1_INCH:
                # This is a circular screen: apply a circle mask over the preview
                theme_preview.paste(circular_mask, mask=circular_mask)
        except:
            theme_preview = Image.open(MAIN_DIRECTORY + "res/docs/no-preview.png")
        finally:
            theme_preview.thumbnail((320, 480), Image.Resampling.LANCZOS)
            self.theme_preview_img = ImageTk.PhotoImage(theme_preview)
            self.theme_preview.config(image=self.theme_preview_img)

            if theme_data is not None:
                author_name = theme_data.get('author', 'unknown')
            else:
                author_name = 'unknown'
            self.theme_author.config(text=T("Author: ") + author_name)
            if author_name.startswith("@"):
                self.theme_author.config(foreground="#a3a3ff", cursor="hand2")
                self.theme_author.bind("<Button-1>",
                                       lambda e: webbrowser.open_new_tab("https://github.com/" + author_name[1:]))
            else:
                self.theme_author.config(foreground="#a3a3a3", cursor="")
                self.theme_author.unbind("<Button-1>")
            self.theme_author.place(x=10, y=self.theme_preview_img.height() + 15)

    def load_config_values(self):
        with open(MAIN_DIRECTORY + "config.yaml", "rt", encoding='utf8') as stream:
            self.config, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(stream)

        # Check if theme is valid
        if get_theme_data(self.config['config']['THEME']) is None:
            # Theme from config.yaml is not valid: use first theme available default size 3.5"
            self.config['config']['THEME'] = get_themes(SIZE_3_5_INCH)[0]

        try:
            self.theme_cb.set(self.config['config']['THEME'])
        except:
            self.theme_cb.set("")

        # App Language GUI injection
        try:
            lang_val = self.config['config'].get('APP_LANGUAGE', 'en')
            self.app_lang_cb.set("Español" if "es" in lang_val.lower() else "English")
        except:
            self.app_lang_cb.set("English")

        self.load_theme_preview()

        try:
            self.hwlib_cb.set(hw_lib_map[self.config['config']['HW_SENSORS']])
        except:
            self.hwlib_cb.current(0)

        try:
            if self.config['config']['ETH'] == "":
                self.eth_cb.current(0)
            else:
                self.eth_cb.set(self.config['config']['ETH'])
        except:
            self.eth_cb.current(0)

        try:
            if self.config['config']['WLO'] == "":
                self.wl_cb.current(0)
            else:
                self.wl_cb.set(self.config['config']['WLO'])
        except:
            self.wl_cb.current(0)

        try:
            if self.config['config']['COM_PORT'] == "AUTO":
                self.com_cb.current(0)
            else:
                self.com_cb.set(self.config['config']['COM_PORT'])
        except:
            self.com_cb.current(0)

        # Guess display size from theme in the configuration
        size = get_theme_size(self.config['config']['THEME'])
        size = size.replace(SIZE_2_1_INCH, SIZE_2_x_INCH)   # If a theme is for 2.1" then it also is for 2.8"
        try:
            self.size_cb.set(size)
        except:
            self.size_cb.current(0)

        # Guess model from revision and size
        revision = self.config['display']['REVISION']
        try:
            self.model_cb.set(revision_and_size_to_model_map[(revision, size)])
        except:
            self.model_cb.current(0)

        try:
            self.orient_cb.set(reverse_map[self.config['display']['DISPLAY_REVERSE']])
        except:
            self.orient_cb.current(0)

        try:
            self.brightness_slider.set(int(self.config['display']['BRIGHTNESS']))
        except:
            self.brightness_slider.set(50)

        try:
            if self.config['config']['CPU_FAN'] == "AUTO":
                self.cpu_fan_cb.current(0)
            else:
                self.cpu_fan_cb.set(self.config['config']['CPU_FAN'])
        except:
            self.cpu_fan_cb.current(0)

        try:
            self.tray_hidden_var.set(self.config['config'].get('TRAY_ICON_HIDDEN', False))
        except:
            self.tray_hidden_var.set(False)

        try:
            self.show_date_time_var.set(self.config['config'].get('GLOBAL_SHOW_DATETIME', False))
        except:
            self.show_date_time_var.set(False)

        try:
            self.show_weather_var.set(self.config['config'].get('GLOBAL_SHOW_WEATHER', False))
        except:
            self.show_weather_var.set(False)

        try:
            self.show_arc_hud_var.set(self.config['config'].get('SHOW_ARC_VIP_HUD', True))
        except:
            self.show_arc_hud_var.set(True)

        try:
            self.arc_hud_type_cb.set(self.config['config'].get('ARC_HUD_TEXT_TYPE', 'HOSTNAME'))
        except:
            self.arc_hud_type_cb.set("HOSTNAME")

        try:
            self.arc_hud_flag_entry.delete(0, END)
            self.arc_hud_flag_entry.insert(0, self.config['config'].get('ARC_HUD_COUNTRY', 've'))
        except:
            pass

        try:
            self.show_arc_hud_var.set(self.config.get('config', {}).get('SHOW_ARC_VIP_HUD', self.config.get('config', {}).get('SHOW_ARC_VIP_HUD', self.config.get('config', {}).get('ARC_HUD_VIP', True))))
    
        except:
            pass

        # Reload content on screen
        self.on_model_change()
        self.on_size_change()
        self.on_theme_change()
        self.on_brightness_change()
        self.on_hwlib_change()

        # Load configuration to sub-window as well
        self.more_config_window.load_config_values(self.config)

        # Cargar estado de inicio en Windows (si la tarea existe)
        if sys.platform == "win32":
            try:
                import subprocess
                check_cmd = ['schtasks', '/Query', '/TN', 'TURZX_Monitor_Autostart']
                result = subprocess.run(check_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    self.autostart_var.set(True)
                else:
                    self.autostart_var.set(False)
            except:
                self.autostart_var.set(False)

    def save_config_values(self):
        self.config['config']['THEME'] = self.theme_cb.get()
        self.config['config']['HW_SENSORS'] = [k for k, v in hw_lib_map.items() if v == self.hwlib_cb.get()][0]
        if self.eth_cb.current() == 0:
            self.config['config']['ETH'] = ""
        else:
            self.config['config']['ETH'] = self.eth_cb.get()
        if self.wl_cb.current() == 0:
            self.config['config']['WLO'] = ""
        else:
            self.config['config']['WLO'] = self.wl_cb.get()
        if self.com_cb.current() == 0:
            self.config['config']['COM_PORT'] = "AUTO"
        else:
            self.config['config']['COM_PORT'] = self.com_cb.get()
        if self.cpu_fan_cb.current() == 0:
            self.config['config']['CPU_FAN'] = "AUTO"
        else:
            self.config['config']['CPU_FAN'] = self.cpu_fan_cb.get().split(' ')[0]
        self.config['display']['REVISION'] = model_and_size_to_revision_map[(self.model_cb.get(), self.size_cb.get())]
        self.config['display']['DISPLAY_REVERSE'] = [k for k, v in reverse_map.items() if v == self.orient_cb.get()][0]
        self.config['display']['BRIGHTNESS'] = int(self.brightness_slider.get())
        
        self.config['config']['TRAY_ICON_HIDDEN'] = self.tray_hidden_var.get()
        self.config['config']['GLOBAL_SHOW_DATETIME'] = self.show_date_time_var.get()
        self.config['config']['GLOBAL_SHOW_WEATHER'] = self.show_weather_var.get()
        self.config['config']['SHOW_ARC_VIP_HUD'] = self.show_arc_hud_var.get()

        
        # Guardar lenguaje en YAML
        self.config['config']['APP_LANGUAGE'] = "es" if self.app_lang_cb.get() == "Español" else "en"

        with open(MAIN_DIRECTORY + "config.yaml", "w", encoding='utf-8') as file:
            ruamel.yaml.YAML().dump(self.config, file)

        # Conectar el Checkbox "VIP HUD" al theme.yaml de forma robusta
        try:
            theme_file = MAIN_DIRECTORY + "res/themes/ARC_Raiders/theme.yaml"
            if os.path.exists(theme_file):
                with open(theme_file, "r", encoding="utf8") as f:
                    theme_cfg, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(f)
                
                show_hud = self.show_arc_hud_var.get()
                custom_stats = theme_cfg.get('STATS', {}).get('CUSTOM', {})
                
                if 'UserFlag' in custom_stats:
                    if 'IMAGE' in custom_stats['UserFlag']:
                        custom_stats['UserFlag']['IMAGE']['SHOW'] = show_hud
                    custom_stats['UserFlag']['COUNTRY_CODE'] = self.arc_hud_flag_entry.get().lower()[:2]
                
                if 'UserProfile' in custom_stats:
                    if 'TEXT' in custom_stats['UserProfile']:
                        custom_stats['UserProfile']['TEXT']['SHOW'] = show_hud
                
                if 'PublicIP' in custom_stats:
                    if 'TEXT' in custom_stats['PublicIP']:
                        # Forzar siempre False para la IP redundante de abajo
                        custom_stats['PublicIP']['TEXT']['SHOW'] = False
                



                with open(theme_file, "w", encoding="utf8") as f:
                    yaml = ruamel.yaml.YAML()
                    yaml.indent(mapping=ind, sequence=ind, offset=bsi)
                    yaml.dump(theme_cfg, f)
        except Exception:
            pass

        # Guardar cambio de auto-inicio en Windows
        if sys.platform == "win32":
            # Limpiar clave de registro antigua para evitar conflictos si existe
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "TuringSmartScreen")
                winreg.CloseKey(key)
            except Exception:
                pass
                
            try:
                import ctypes
                import subprocess
                import sys, os
                
                check_cmd = ['schtasks', '/Query', '/TN', 'TURZX_Monitor_Autostart']
                result = subprocess.run(check_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                task_exists = (result.returncode == 0)
                
                if self.autostart_var.get() and not task_exists:
                    if getattr(sys, 'frozen', False):
                        main_exe_dir = os.path.dirname(sys.executable)
                        exe_path = os.path.join(main_exe_dir, "main.exe")
                    else:
                        exe_path = os.path.join(MAIN_DIRECTORY, "main.exe")
                        
                    if os.path.exists(exe_path):
                        target = f'\\"{exe_path}\\"'
                    else:
                        py_path = os.path.join(MAIN_DIRECTORY, "main.py")
                        target = f'\\"{sys.executable}\\" \\"{py_path}\\"'
                        
                    params = f'/Create /F /TN "TURZX_Monitor_Autostart" /TR "{target}" /SC ONLOGON /RL HIGHEST'
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", "schtasks.exe", params, None, 0)
                    
                elif not self.autostart_var.get() and task_exists:
                    params = f'/Delete /TN "TURZX_Monitor_Autostart" /F'
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", "schtasks.exe", params, None, 0)
            except Exception as e:
                pass

    def save_additional_config(self, ping: str, api_key: str, lat: str, long: str, unit: str, lang: str):
        self.config['config']['PING'] = ping
        self.config['config']['WEATHER_API_KEY'] = api_key
        self.config['config']['WEATHER_LATITUDE'] = lat
        self.config['config']['WEATHER_LONGITUDE'] = long
        self.config['config']['WEATHER_UNITS'] = unit
        self.config['config']['WEATHER_LANGUAGE'] = lang

        with open(MAIN_DIRECTORY + "config.yaml", "w", encoding='utf-8') as file:
            ruamel.yaml.YAML().dump(self.config, file)

    def on_app_lang_change(self, event=None):
        global USE_ES
        USE_ES = (self.app_lang_cb.get() == "Español")
        
        self.window.title(T('Turing Smart Screen configuration'))
        self.sysmon_label1.config(text=T('Display configuration'))
        self.model_label.config(text=T('Smart screen model'))
        self.size_label.config(text=T('Smart screen size'))
        self.com_label.config(text=T('COM port'))
        self.orient_label.config(text=T('Orientation'))
        self.brightness_label.config(text=T('Brightness'))
        self.brightness_warning_label.config(text=T('⚠ Turing 3.5" displays can get hot at high brightness!'))
        self.sysmon_label2.config(text=T('Turing Smart Screen Configuration'))
        self.theme_label.config(text=T('Theme'))
        
        global hw_lib_map
        old_hw_val = self.hwlib_cb.get()
        is_auto_hw = old_hw_val == hw_lib_map["AUTO"]
        hw_lib_map["AUTO"] = T("Automatic")
        if sys.platform != "win32" and "LHM" in hw_lib_map:
            del hw_lib_map["LHM"]
        self.hwlib_cb.config(values=list(hw_lib_map.values()))
        if is_auto_hw:
            self.hwlib_cb.set(hw_lib_map["AUTO"])
            
        self.hwlib_label.config(text=T('Hardware monitoring'))
        self.eth_label.config(text=T('Ethernet interface'))
        self.wl_label.config(text=T('Wi-Fi interface'))
        self.lhm_admin_warning.config(text=T("❌ Restart as admin. or select another Hardware monitoring"))
        self.cpu_fan_label.config(text=T('CPU fan (？)'))
        self.autostart_checkbox.config(text=T("Run monitor at Windows startup"))
        self.tray_hidden_checkbox.config(text=T("Hide system tray icon"))
        self.show_date_time_checkbox.config(text=T("Show Time & Date everywhere"))
        self.show_weather_checkbox.config(text=T("Show Weather everywhere"))
        self.show_arc_hud_checkbox.config(text=T("Show VIP HUD (Flag/Hostname/IP)"))
        self.arc_hud_type_label.config(text=T("HUD Text:"))
        self.arc_hud_flag_label.config(text=T("Flag (ISO):"))
        self.widget_config_btn.config(text=T("Desktop Widget"))
        self.widget_config_window.update_texts()
        self.weather_ping_btn.config(text=T("Weather & ping"))
        self.open_theme_folder_btn.config(text=T("Open themes\nfolder"))
        self.edit_theme_btn.config(text=T("Edit theme"))
        self.save_btn.config(text=T("Save settings"))
        self.save_run_btn.config(text=T("Save and run"))
        
        old_com = self.com_cb.get()
        self.com_cb.config(values=get_com_ports())
        if old_com in ["Automatic detection", "Detección automática"]:
            self.com_cb.set(T("Automatic detection"))

        old_eth = self.eth_cb.get()
        self.eth_cb.config(values=get_net_if())
        if old_eth in ["None", "Ninguno"]:
            self.eth_cb.set(T("None"))

        old_wl = self.wl_cb.get()
        self.wl_cb.config(values=get_net_if())
        if old_wl in ["None", "Ninguno"]:
            self.wl_cb.set(T("None"))

        self.show_hide_brightness_warning()
        self.load_theme_preview()
        
        self.more_config_window.update_texts()

    def on_theme_change(self, e=None):
        self.load_theme_preview()

    def on_widget_config_click(self):
        self.widget_config_window.load_config(self.config)
        self.widget_config_window.show()

    def on_weatherping_click(self):
        self.more_config_window.show()

    def on_open_theme_folder_click(self):
        path = f'"{MAIN_DIRECTORY}res/themes"'
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def on_theme_editor_click(self):
        subprocess.Popen(
            f'"{MAIN_DIRECTORY}{glob.glob("theme-editor.*", root_dir=MAIN_DIRECTORY)[0]}" "{self.theme_cb.get()}"',
            shell=True)

    def on_save_click(self):
        self.save_config_values()

    def on_saverun_click(self):
        self.save_config_values()
        subprocess.Popen(f'"{MAIN_DIRECTORY}{glob.glob("main.*", root_dir=MAIN_DIRECTORY)[0]}"', shell=True)
        self.window.destroy()

    def on_brightness_change(self, e=None):
        self.brightness_string.set(str(int(self.brightness_slider.get())) + "%")
        self.show_hide_brightness_warning()

    def on_model_change(self, e=None):
        self.show_hide_brightness_warning()
        model = self.model_cb.get()
        if model == SIMULATED_MODEL:
            self.com_cb.configure(state="disabled", foreground="#C0C0C0")
            self.orient_cb.configure(state="disabled", foreground="#C0C0C0")
            self.brightness_slider.configure(state="disabled")
            self.brightness_val_label.configure(foreground="#C0C0C0")
        else:
            self.com_cb.configure(state="readonly", foreground="#000")
            self.orient_cb.configure(state="readonly", foreground="#000")
            self.brightness_slider.configure(state="normal")
            self.brightness_val_label.configure(foreground="#000")

    def on_size_change(self, e=None):
        size = self.size_cb.get()
        size = size.replace(SIZE_2_x_INCH, SIZE_2_1_INCH)  # For '2.1" / 2.8"' size, keep '2.1"' as size to get themes for
        themes = get_themes(size)
        self.theme_cb.config(values=themes)

        if not self.theme_cb.get() in themes:
            # The selected theme does not exist anymore / is not allowed for this screen model : select 1st theme avail.
            self.theme_cb.set(themes[0])

        self.show_hide_brightness_warning()

    def on_hwlib_change(self, e=None):
        hwlib = [k for k, v in hw_lib_map.items() if v == self.hwlib_cb.get()][0]
        if hwlib == "STUB" or hwlib == "STATIC":
            self.eth_cb.configure(state="disabled", foreground="#C0C0C0")
            self.wl_cb.configure(state="disabled", foreground="#C0C0C0")
        else:
            self.eth_cb.configure(state="readonly", foreground="#000")
            self.wl_cb.configure(state="readonly", foreground="#000")

        if sys.platform == "win32":
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if (hwlib == "LHM" or hwlib == "AUTO") and not is_admin:
                self.lhm_admin_warning.place(x=370, y=725)
                self.save_run_btn.state(["disabled"])
            else:
                self.lhm_admin_warning.place_forget()
                self.save_run_btn.state(["!disabled"])
        else:
            if hwlib == "PYTHON" or hwlib == "AUTO":
                self.cpu_fan_label.place(x=370, y=460)
                self.cpu_fan_cb.place(x=550, y=455, width=250)
            else:
                self.cpu_fan_label.place_forget()
                self.cpu_fan_cb.place_forget()

    def show_hide_brightness_warning(self, e=None):
        if int(self.brightness_slider.get()) > 50 and self.model_cb.get() == TURING_MODEL and self.size_cb.get() == SIZE_3_5_INCH:
            # Show warning for Turing Smart screen 3.5 with high brightness
            self.brightness_warning_label.place(x=370, y=225)
        else:
            self.brightness_warning_label.place_forget()

    def on_fan_speed_update(self):
        # Update fan speed periodically
        prev_value = self.cpu_fan_cb.current()  # Save currently selected index
        self.cpu_fan_cb.config(values=get_fans())
        if prev_value != -1:
            self.cpu_fan_cb.current(prev_value)  # Force select same index to refresh displayed value
        self.window.after(500, self.on_fan_speed_update)


class WidgetConfigWindow:
    def __init__(self, main_window):
        self.window = Toplevel()
        self.window.withdraw()
        self.window.title(T('Desktop Widget settings'))
        self.window.geometry("450x360")
        self.main_window = main_window

        self.enable_var = BooleanVar()
        self.enable_cb = ttk.Checkbutton(self.window, text=T("Enable Desktop Widget"), variable=self.enable_var)
        self.enable_cb.place(x=20, y=10)

        self.on_top_var = BooleanVar()
        self.on_top_cb = ttk.Checkbutton(self.window, text=T("Always on top"), variable=self.on_top_var)
        self.on_top_cb.place(x=20, y=40)

        self.locked_var = BooleanVar()
        self.locked_cb = ttk.Checkbutton(self.window, text=T("Lock position (prevent dragging)"), variable=self.locked_var)
        self.locked_cb.place(x=20, y=70)

        self.transparent_bg_var = BooleanVar()
        self.transparent_bg_cb = ttk.Checkbutton(self.window, text=T("Hide black background (Floating HUD mode)"), variable=self.transparent_bg_var)
        self.transparent_bg_cb.place(x=20, y=100)

        self.show_border_var = BooleanVar()
        self.show_border_cb = ttk.Checkbutton(self.window, text=T("Mostrar marco interior (Border)"), variable=self.show_border_var)
        self.show_border_cb.place(x=20, y=130)

        ttk.Label(self.window, text=T("Scale / Size:")).place(x=20, y=170)
        self.scale_cb = ttk.Combobox(self.window, values=["25%", "50%", "75%", "100%", "125%", "150%"])
        self.scale_cb.place(x=230, y=165)

        ttk.Label(self.window, text=T("Opacity (entire window):")).place(x=20, y=200)
        self.alpha_cb = ttk.Combobox(self.window, values=["10%", "30%", "50%", "75%", "90%", "100%"])
        self.alpha_cb.place(x=230, y=195)

        ttk.Label(self.window, text=T("Rounded Corners Radius:")).place(x=20, y=230)
        self.radius_cb = ttk.Combobox(self.window, values=["0", "10", "15", "25", "35", "50"])
        self.radius_cb.place(x=230, y=225)

        self.save_btn = ttk.Button(self.window, text=T("Save & Apply (Needs Restart)"), command=self.save)
        self.save_btn.place(x=120, y=290, width=200, height=40)

        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
    def load_config(self, cfg):
        self.enable_var.set(cfg['config'].get('ENABLE_DESKTOP_WIDGET', False))
        self.on_top_var.set(cfg['config'].get('DESKTOP_WIDGET_ON_TOP', True))
        self.locked_var.set(cfg['config'].get('DESKTOP_WIDGET_LOCKED', False))
        self.transparent_bg_var.set(cfg['config'].get('DESKTOP_WIDGET_TRANSPARENT_BG', cfg['config'].get('DESKTOP_WIDGET_NO_BG', False)))
        self.show_border_var.set(cfg['config'].get('DESKTOP_WIDGET_SHOW_BORDER', False))
        
        scale_val = cfg['config'].get("DESKTOP_WIDGET_SCALE", 100)
        try:
           self.scale_cb.set(f"{scale_val}%")
        except:
           self.scale_cb.set("100%")
           
        alpha_val = cfg['config'].get("DESKTOP_WIDGET_ALPHA", 100)
        try:
           self.alpha_cb.set(f"{alpha_val}%")
        except:
           self.alpha_cb.set("100%")

        radius_val = cfg['config'].get("DESKTOP_WIDGET_RADIUS", 0)
        try:
           self.radius_cb.set(str(radius_val))
        except:
           self.radius_cb.set("0")

    def show(self):
        self.window.deiconify()
        self.window.grab_set()

    def hide(self):
        self.window.grab_release()
        self.window.withdraw()

    def update_texts(self):
        self.window.title(T('Desktop Widget settings'))
        self.enable_cb.config(text=T("Enable Desktop Widget"))
        self.on_top_cb.config(text=T("Always on top"))
        self.locked_cb.config(text=T("Lock position (prevent dragging)"))
        self.transparent_bg_cb.config(text=T("Hide black background (Floating HUD mode)"))
        self.show_border_cb.config(text=T("Mostrar marco interior (Border)") if "es" in lang_code.lower() else "Show inner outline/border")
        self.save_btn.config(text=T("Save & Apply (Needs Restart)"))

    def save(self):
        cfg = self.main_window.config
        cfg['config']['ENABLE_DESKTOP_WIDGET'] = self.enable_var.get()
        cfg['config']['DESKTOP_WIDGET_ON_TOP'] = self.on_top_var.get()
        cfg['config']['DESKTOP_WIDGET_LOCKED'] = self.locked_var.get()
        cfg['config']['DESKTOP_WIDGET_TRANSPARENT_BG'] = self.transparent_bg_var.get()
        cfg['config']['DESKTOP_WIDGET_SHOW_BORDER'] = self.show_border_var.get()
        if 'DESKTOP_WIDGET_NO_BG' in cfg['config']:
            del cfg['config']['DESKTOP_WIDGET_NO_BG']
        import re
        def clean_int(val, default):
            try:
                digits = re.sub(r'\D', '', str(val))
                return int(digits) if digits else default
            except Exception:
                return default

        cfg['config']['DESKTOP_WIDGET_SCALE'] = clean_int(self.scale_cb.get(), 100)
        cfg['config']['DESKTOP_WIDGET_ALPHA'] = clean_int(self.alpha_cb.get(), 100)
        cfg['config']['DESKTOP_WIDGET_RADIUS'] = clean_int(self.radius_cb.get(), 0)
        
        import ruamel.yaml
        with open(MAIN_DIRECTORY + "config.yaml", "w", encoding='utf-8') as file:
            ruamel.yaml.YAML().dump(cfg, file)
        
        self.hide()


class MoreConfigWindow:
    def __init__(self, main_window: TuringConfigWindow):
        self.window = Toplevel()
        self.window.withdraw()
        self.window.title(T('Configure weather & ping'))
        self.window.geometry("750x680")

        self.main_window = main_window

        # Make TK look better with Sun Valley ttk theme
        sv_ttk.set_theme("light")

        self.ping_label = ttk.Label(self.window, text=T('Hostname to ping'))
        self.ping_label.place(x=10, y=10)
        self.ping_entry = ttk.Entry(self.window)
        self.ping_entry.place(x=220, y=5, width=250)

        self.weather_label = ttk.Label(self.window, text=T('Weather forecast (OpenWeatherMap API)'), font='bold')
        self.weather_label.place(x=10, y=70)

        self.weather_info_label = ttk.Label(self.window,
                                       text=T('To display weather forecast on themes that support it, you need an OpenWeatherMap "One Call API 3.0" key.\nYou will get 1,000 API calls per day for free. This program is configured to stay under this threshold (~300 calls/day).'))
        self.weather_info_label.place(x=10, y=100)
        self.weather_api_link_label = ttk.Label(self.window,
                                           text=T("Click here to subscribe to OpenWeatherMap One Call API 3.0."))
        self.weather_api_link_label.place(x=10, y=140)
        self.weather_api_link_label.config(foreground="#a3a3ff", cursor="hand2")
        self.weather_api_link_label.bind("<Button-1>",
                                    lambda e: webbrowser.open_new_tab("https://openweathermap.org/api"))

        self.api_label = ttk.Label(self.window, text=T('OpenWeatherMap API key'))
        self.api_label.place(x=10, y=170)
        self.api_entry = ttk.Entry(self.window)
        self.api_entry.place(x=200, y=165, width=300)

        self.latlong_label = ttk.Label(self.window,
                                  text=T("You can use online services to get your latitude/longitude e.g. latlong.net (click here)"))
        self.latlong_label.place(x=10, y=210)
        self.latlong_label.config(foreground="#a3a3ff", cursor="hand2")
        self.latlong_label.bind("<Button-1>",
                           lambda e: webbrowser.open_new_tab("https://www.latlong.net/"))

        self.lat_label = ttk.Label(self.window, text=T('Latitude'))
        self.lat_label.place(x=10, y=250)
        self.lat_entry = ttk.Entry(self.window, validate='key',
                                   validatecommand=(self.window.register(self.validateCoord), '%P'))
        self.lat_entry.place(x=90, y=245, width=100)

        self.long_label = ttk.Label(self.window, text=T('Longitude'))
        self.long_label.place(x=280, y=250)
        self.long_entry = ttk.Entry(self.window, validate='key',
                                    validatecommand=(self.window.register(self.validateCoord), '%P'))
        self.long_entry.place(x=350, y=245, width=100)

        self.unit_label = ttk.Label(self.window, text=T('Units'))
        self.unit_label.place(x=10, y=290)
        self.unit_cb = ttk.Combobox(self.window, values=list(weather_unit_map.values()), state='readonly')
        self.unit_cb.place(x=190, y=285, width=250)

        self.lang_label = ttk.Label(self.window, text=T('Language'))
        self.lang_label.place(x=10, y=330)
        self.lang_cb = ttk.Combobox(self.window, values=list(weather_lang_map.values()), state='readonly')
        self.lang_cb.place(x=190, y=325, width=250)

        self.citysearch1_label = ttk.Label(self.window, text=T('Location search'), font='bold')
        self.citysearch1_label.place(x=80, y=370)

        self.citysearch2_label = ttk.Label(self.window, text=T('Enter location to automatically get coordinates (latitude/longitude).\nFor example "Berlin" "London, GB", "London, Quebec".\nRemember to set valid API key and pick language first!'))
        self.citysearch2_label.place(x=10, y=396)

        self.citysearch3_label = ttk.Label(self.window, text=T("Enter location"))
        self.citysearch3_label.place(x=10, y=474)
        self.citysearch_entry = ttk.Entry(self.window)
        self.citysearch_entry.place(x=220, y=470, width=220)
        self.citysearch_btn = ttk.Button(self.window, text=T("Search"), command=lambda: self.on_search_click())
        self.citysearch_btn.place(x=455, y=468, height=40, width=175)

        self.citysearch4_label = ttk.Label(self.window, text=T("Select location\n(use after Search)"))
        self.citysearch4_label.place(x=10, y=540)
        self.citysearch_cb = ttk.Combobox(self.window, values=[], state='readonly')
        self.citysearch_cb.place(x=180, y=544, width=320)
        self.citysearch_btn2 = ttk.Button(self.window, text=T("Fill in lat/long"), command=lambda: self.on_filllatlong_click())
        self.citysearch_btn2.place(x=515, y=540, height=40, width=175)

        self.citysearch_warn_label = ttk.Label(self.window, text="")
        self.citysearch_warn_label.place(x=20, y=600)
        self.citysearch_warn_label.config(foreground="#ff0000")

        self.save_btn = ttk.Button(self.window, text=T("Save settings"), command=lambda: self.on_save_click())
        self.save_btn.place(x=580, y=620, height=50, width=140)

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._city_entries = []

    def validateCoord(self, coord: str):
        if not coord:
            return True
        try:
            float(coord)
        except:
            return False
        return True

    def show(self):
        self.window.deiconify()

    def on_closing(self):
        self.window.withdraw()

    def load_config_values(self, config):
        self.config = config

        try:
            self.ping_entry.insert(0, self.config['config']['PING'])
        except:
            self.ping_entry.insert(0, "8.8.8.8")

        try:
            self.api_entry.insert(0, self.config['config']['WEATHER_API_KEY'])
        except:
            pass

        try:
            self.lat_entry.insert(0, self.config['config']['WEATHER_LATITUDE'])
        except:
            self.lat_entry.insert(0, "45.75")

        try:
            self.long_entry.insert(0, self.config['config']['WEATHER_LONGITUDE'])
        except:
            self.long_entry.insert(0, "45.75")

        try:
            self.unit_cb.set(weather_unit_map[self.config['config']['WEATHER_UNITS']])
        except:
            self.unit_cb.set(0)

        try:
            self.lang_cb.set(weather_lang_map[self.config['config']['WEATHER_LANGUAGE']])
        except:
            self.lang_cb.set(weather_lang_map["en"])

    def update_texts(self):
        self.window.title(T('Configure weather & ping'))
        self.ping_label.config(text=T('Hostname to ping'))
        self.weather_label.config(text=T('Weather forecast (OpenWeatherMap API)'))
        self.weather_info_label.config(text=T('To display weather forecast on themes that support it, you need an OpenWeatherMap "One Call API 3.0" key.\nYou will get 1,000 API calls per day for free. This program is configured to stay under this threshold (~300 calls/day).'))
        self.weather_api_link_label.config(text=T("Click here to subscribe to OpenWeatherMap One Call API 3.0."))
        self.api_label.config(text=T('OpenWeatherMap API key'))
        self.latlong_label.config(text=T("You can use online services to get your latitude/longitude e.g. latlong.net (click here)"))
        self.lat_label.config(text=T('Latitude'))
        self.long_label.config(text=T('Longitude'))
        self.unit_label.config(text=T('Units'))
        self.lang_label.config(text=T('Language'))
        self.citysearch1_label.config(text=T('Location search'))
        self.citysearch2_label.config(text=T('Enter location to automatically get coordinates (latitude/longitude).\nFor example "Berlin" "London, GB", "London, Quebec".\nRemember to set valid API key and pick language first!'))
        self.citysearch3_label.config(text=T("Enter location"))
        self.citysearch_btn.config(text=T("Search"))
        self.citysearch4_label.config(text=T("Select location\n(use after Search)"))
        self.citysearch_btn2.config(text=T("Fill in lat/long"))
        self.save_btn.config(text=T("Save settings"))
    
    def citysearch_show_warning(self, warning):
        self.citysearch_warn_label.config(text=warning)
		
    def on_search_click(self):
        OPENWEATHER_GEOAPI_URL = "http://api.openweathermap.org/geo/1.0/direct"
        api_key = self.api_entry.get()
        lang = [k for k, v in weather_lang_map.items() if v == self.lang_cb.get()][0]
        city = self.citysearch_entry.get()

        if len(api_key) == 0 or len(city) == 0:
            self.citysearch_show_warning("API key and city name cannot be empty.")
            return

        try:
            request = requests.get(OPENWEATHER_GEOAPI_URL, timeout=5, params={"appid": api_key, "lang": lang, 
                                   "q": city, "limit": 10})
        except:
            self.citysearch_show_warning("Error fetching OpenWeatherMap Geo API")
            return

        if request.status_code == 401:
            self.citysearch_show_warning("Invalid OpenWeatherMap API key.")
            return
        elif request.status_code != 200:
            self.citysearch_show_warning(f"Error #{request.status_code} fetching OpenWeatherMap Geo API.")
            return
        
        self._city_entries = []
        cb_entries = []
        for entry in request.json():
            name = entry['name']
            state = entry.get('state', None)
            lat = entry['lat']
            long = entry['lon']
            country_code = entry['country'].upper()
            babel_lang = 'es' if lang == 'sp' else lang
            try:
                country = babel.Locale(babel_lang).territories.get(country_code, country_code)
            except:
                country = country_code
            if state is not None:
                full_name = f"{name}, {state}, {country}"
            else:
                full_name = f"{name}, {country}"
            self._city_entries.append({"full_name": full_name, "lat": str(lat), "long": str(long)})
            cb_entries.append(full_name)

        self.citysearch_cb.config(values = cb_entries)
        if len(cb_entries) == 0:
            self.citysearch_show_warning("No given city found.")
        else:
            self.citysearch_cb.current(0)
            self.citysearch_show_warning("Select your city now from list and apply \"Fill in lat/long\".")

    def on_filllatlong_click(self):
        if len(self._city_entries) == 0:
            self.citysearch_show_warning("No city selected or no search results.")
            return
        city = [i for i in self._city_entries if i['full_name'] == self.citysearch_cb.get()][0]
        self.lat_entry.delete(0, END)
        self.lat_entry.insert(0, city['lat'])
        self.long_entry.delete(0, END)
        self.long_entry.insert(0, city['long'])
        self.citysearch_show_warning(f"Lat/long values filled for {city['full_name']}")

    def on_save_click(self):
        self.save_config_values()
        self.on_closing()

    def save_config_values(self):
        ping = self.ping_entry.get()
        api_key = self.api_entry.get()
        lat = self.lat_entry.get()
        long = self.long_entry.get()
        unit = [k for k, v in weather_unit_map.items() if v == self.unit_cb.get()][0]
        lang = [k for k, v in weather_lang_map.items() if v == self.lang_cb.get()][0]

        self.main_window.save_additional_config(ping, api_key, lat, long, unit, lang)


if __name__ == "__main__":
    configurator = TuringConfigWindow()
    configurator.run()
