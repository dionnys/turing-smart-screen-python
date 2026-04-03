#!/usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
#
# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/dionnys/turing-smart-screen-python/
#
# Copyright (C) 2021 dionnys (dionnys)
# Copyright (C) 2022 Rollbacke
# Copyright (C) 2022 Ebag333
# Copyright (C) 2022 w1ld3r
# Copyright (C) 2022 Charles Ferguson (gerph)
# Copyright (C) 2022 Russ Nelson (RussNelson)
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

# This file is the system monitor main program to display HW sensors on your screen using themes (see README)

from library.pythoncheck import check_python_version
print(">>> Iniciando main.py...")
check_python_version()

import glob
import os
import sys

# Auto-elevate privileges on Windows
if sys.platform == 'win32':
    import ctypes
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    if not is_admin():
        # Relaunch script/exe with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)
        sys.exit(0)

    # Hide the console window to keep it running purely in the background
    hWnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hWnd:
        ctypes.windll.user32.ShowWindow(hWnd, 0)

    # Prevent multiple instances
    mutex_name = "turing_smart_screen_python_mutex"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        sys.exit(0)

try:
    import atexit
    import locale
    import platform
    import signal
    import subprocess
    import time
    from pathlib import Path
    from PIL import Image

    if platform.system() == 'Windows':
        import win32api
        import win32con
        import win32gui

    from library.log import logger
    import library.scheduler as scheduler

except Exception as e:
    print("""Import error: %s
Please follow start guide to install required packages: https://github.com/dionnys/turing-smart-screen-python/wiki/System-monitor-:-how-to-start
Or the troubleshooting page: https://github.com/dionnys/turing-smart-screen-python/wiki/Troubleshooting#all-os-tkinter-dependency-not-installed""" % str(
        e))
    try:
        sys.exit(0)
    except:
        os._exit(0)

try:
    import pystray
except:
    # If pystray cannot be loaded do not stop the program, just ignore it. The tray icon will not be displayed.
    pass

import sys
from pathlib import Path
if getattr(sys, 'frozen', False):
    MAIN_DIRECTORY = str(Path(sys.executable).parent.resolve()) + "/"
else:
    MAIN_DIRECTORY = str(Path(__file__).parent.resolve()) + "/"

if __name__ == "__main__":

    # Apply system locale to this program
    locale.setlocale(locale.LC_ALL, '')

    logger.debug("Using Python %s" % sys.version)


    def wait_for_empty_queue(timeout: int = 5):
        # Waiting for all pending request to be sent to display
        logger.info("Waiting for all pending request to be sent to display (%ds max)..." % timeout)

        wait_time = 0
        while not scheduler.is_queue_empty() and wait_time < timeout:
            time.sleep(0.1)
            wait_time = wait_time + 0.1

        logger.debug("(Waited %.1fs)" % wait_time)

    def clean_stop(tray_icon=None):
        # Turn screen and LEDs off before stopping
        try:
            from library.display import display
            display.turn_off()
        except:
            pass

        # Do not stop the program now in case data transmission was in progress
        # Instead, ask the scheduler to empty the action queue before stopping
        scheduler.STOPPING = True

        # Waiting for all pending request to be sent to display
        wait_for_empty_queue(5)

        # Remove tray icon just before exit
        if tray_icon:
            tray_icon.visible = False
            try:
                tray_icon.stop()
            except:
                pass

        # We force the exit to avoid waiting for other scheduled tasks: they may have a long delay!
        import os
        os._exit(0)


    def on_signal_caught(signum, frame=None):
        logger.info("Caught signal %d, exiting" % signum)
        import threading
        threading.Thread(target=clean_stop).start()


    def on_configure_tray(tray_icon, item):
        logger.info("Configure from tray icon")
        subprocess.Popen(f'"{MAIN_DIRECTORY}{glob.glob("configure.*", root_dir=MAIN_DIRECTORY)[0]}"', shell=True)
        import threading
        threading.Thread(target=clean_stop, args=(tray_icon,)).start()


    def on_exit_tray(tray_icon, item):
        logger.info("Exit from tray icon")
        import threading
        threading.Thread(target=clean_stop, args=(tray_icon,)).start()


    def on_clean_exit(*args):
        logger.info("Program will now exit")
        import threading
        threading.Thread(target=clean_stop).start()


    if platform.system() == "Windows":
        def on_win32_ctrl_event(event):
            """Handle Windows console control events (like Ctrl-C)."""
            if event in (win32con.CTRL_C_EVENT, win32con.CTRL_BREAK_EVENT, win32con.CTRL_CLOSE_EVENT):
                logger.debug("Caught Windows control event %s, exiting" % event)
                clean_stop()
            return 0


        def on_win32_wm_event(hWnd, msg, wParam, lParam):
            """Handle Windows window message events (like ENDSESSION, CLOSE, DESTROY)."""
            logger.debug("Caught Windows window message event %s" % msg)
            if msg == win32con.WM_POWERBROADCAST:
                # WM_POWERBROADCAST is used to detect computer going to/resuming from sleep
                if wParam == win32con.PBT_APMSUSPEND:
                    logger.info("Computer is going to sleep, display will turn off")
                    try:
                        from library.display import display
                        display.turn_off()
                    except:
                        pass
                elif wParam == win32con.PBT_APMRESUMEAUTOMATIC:
                    logger.info("Computer is resuming from sleep, display will turn on")
                    try:
                        from library.display import display
                        display.turn_on()
                        # Some models have troubles displaying back the previous bitmap after being turned off/on
                        display.display_static_images()
                        display.display_static_text()
                    except:
                        pass
            else:
                # For any other events, the program will stop
                logger.info("Program will now exit")
                clean_stop()

    # Create a tray icon for the program, with an Exit entry in menu
    try:
        from library.config import CONFIG_DATA
        tray_icon = None
        import locale
        try:
            lang_code = locale.getlocale()[0] or "en"
        except:
            lang_code = "en"
        lang_code = CONFIG_DATA['config'].get('APP_LANGUAGE', lang_code)
        USE_ES = "es" in str(lang_code).lower()
        cfg_text = "Configurar" if USE_ES else "Configure"
        exit_text = "Salir" if USE_ES else "Exit"

        if not CONFIG_DATA['config'].get('TRAY_ICON_HIDDEN', False):
            tray_icon = pystray.Icon(
                name='Turing Smart Screen',
                title='Turing Smart Screen',
                icon=Image.open(MAIN_DIRECTORY + "res/icons/monitor-icon-17865/64.png"),
                menu=pystray.Menu(
                    pystray.MenuItem(
                        text=cfg_text,
                        action=on_configure_tray),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(
                        text=exit_text,
                        action=on_exit_tray)
                )
            )

            # For platforms != macOS, display the tray icon now with non-blocking function
            if platform.system() != "Darwin":
                tray_icon.run_detached()
                logger.info("Tray icon has been displayed")
    except Exception as ex:
        tray_icon = None
        logger.warning(f"Tray icon is not supported on your platform or failed to load: {ex}")

    # Set the different stopping event handlers, to send a complete frame to the LCD before exit
    atexit.register(on_clean_exit)
    signal.signal(signal.SIGINT, on_signal_caught)
    signal.signal(signal.SIGTERM, on_signal_caught)
    is_posix = os.name == 'posix'
    if is_posix:
        signal.signal(signal.SIGQUIT, on_signal_caught)
    if platform.system() == "Windows":
        win32api.SetConsoleCtrlHandler(on_win32_ctrl_event, True)

    # Initialize the display
    logger.info("Initialize display")
    from library.display import display
    display.initialize_display()

    # Start serial queue handler
    scheduler.QueueHandler()

    # Create all static images
    from library.display import display
    display.display_static_images()

    # Create all static texts
    display.display_static_text()

    # Wait for static images/text to be displayed before starting monitoring (to avoid filling the queue while waiting)
    wait_for_empty_queue(10)

    # Start sensor scheduled reading. Avoid starting them all at the same time to optimize load
    logger.info("Starting system monitoring")
    import library.stats as stats

    scheduler.CPUPercentage(); time.sleep(0.25)
    scheduler.CPUFrequency(); time.sleep(0.25)
    scheduler.CPULoad(); time.sleep(0.25)
    scheduler.CPUTemperature(); time.sleep(0.25)
    scheduler.CPUFanSpeed(); time.sleep(0.25)
    if stats.Gpu.is_available():
        scheduler.GpuStats(); time.sleep(0.25)
    scheduler.MemoryStats(); time.sleep(0.25)
    scheduler.DiskStats(); time.sleep(0.25)
    scheduler.NetStats(); time.sleep(0.25)
    scheduler.DateStats(); time.sleep(0.25)
    scheduler.SystemUptimeStats(); time.sleep(0.25)
    scheduler.CustomStats(); time.sleep(0.25)
    scheduler.WeatherStats(); time.sleep(0.25)
    scheduler.PingStats(); time.sleep(0.25)

    # MAGIC: Turno Automático de Brillo (Día y Noche)
    import threading
    import datetime
    from library import config
    
    def auto_brightness_loop():
        is_night_mode = False
        while not scheduler.STOPPING:
            current_hour = datetime.datetime.now().hour
            is_night = current_hour >= 22 or current_hour < 7
            
            if is_night and not is_night_mode:
                try:
                    display.lcd.SetBrightness(0) # Apagón nocturno a las 22:00
                except: pass
                is_night_mode = True
            elif not is_night and is_night_mode:
                try:
                    display.lcd.SetBrightness(config.CONFIG_DATA["display"]["BRIGHTNESS"]) # Brillo normal de día a las 07:00
                except: pass
                is_night_mode = False
            
            time.sleep(30) # Chequeo cada 30 segundos
            
    threading.Thread(target=auto_brightness_loop, daemon=True, name="NightModeCheck").start()


    # OS-specific tasks
    if tray_icon and platform.system() == "Darwin":  # macOS-specific
        from AppKit import NSBundle, NSApp, NSApplicationActivationPolicyProhibited

        # Hide Python Launcher icon from macOS dock
        info = NSBundle.mainBundle().infoDictionary()
        info["LSUIElement"] = "1"
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)

        # For macOS: display the tray icon now with blocking function
        tray_icon.run()

    def fallback_main_loop():
        """Bucle principal de respaldo (sin widget) para mantener el proceso vivo y procesar eventos de Windows."""
        if platform.system() == "Windows":
            # Crear una ventana oculta solo para recibir eventos (apagado, suspensión, etc.)
            hinst = win32api.GetModuleHandle(None)
            wndclass = win32gui.WNDCLASS()
            wndclass.hInstance = hinst
            wndclass.lpszClassName = "turingEventWndClass"
            messageMap = {
                win32con.WM_QUERYENDSESSION: on_win32_wm_event,
                win32con.WM_ENDSESSION: on_win32_wm_event,
                win32con.WM_QUIT: on_win32_wm_event,
                win32con.WM_DESTROY: on_win32_wm_event,
                win32con.WM_CLOSE: on_win32_wm_event,
                win32con.WM_POWERBROADCAST: on_win32_wm_event
            }
            wndclass.lpfnWndProc = messageMap

            try:
                myWindowClass = win32gui.RegisterClass(wndclass)
                hwnd = win32gui.CreateWindowEx(
                    win32con.WS_EX_LEFT,
                    myWindowClass,
                    "turingEventWnd",
                    0, 
                    0, 0, 0, 0,
                    0,
                    0,
                    hinst,
                    None
                )
            except Exception as e:
                logger.error("Exception while creating event window: %s" % str(e))

        import gc
        counter = 0
        while not scheduler.STOPPING:
            if platform.system() == "Windows":
                win32gui.PumpWaitingMessages()
            
            # Optimización de memoria: ejecutar GC cada 60 segundos
            counter += 1
            if counter % 120 == 0:
                gc.collect()
            
            time.sleep(0.5)

    # Lógica de Inicio de Bucle Principal (Main Thread)
    # ── IMPORTANTE: Las GUIs (PyQt6/Tkinter) DEBEN correr en el hilo principal ──
    if getattr(display, "desktop_widget", None):
        # Si el widget está activo, él toma el control del hilo principal.
        # Pero antes, lanzamos el listener de eventos de Windows en un hilo separado
        # para no perder la detección de Sleep/Resume.
        if platform.system() == "Windows":
            import threading
            threading.Thread(target=fallback_main_loop, daemon=True, name="WinEventThread").start()
        
        # El widget corre aquí (bloquea el hilo principal)
        display.desktop_widget.run()
    else:
        # Si no hay widget, usamos el bucle estándar en el hilo principal.
        fallback_main_loop()
