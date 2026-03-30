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

from library import config
from library.lcd.lcd_comm import Orientation
from library.lcd.lcd_comm_rev_a import LcdCommRevA
from library.lcd.lcd_comm_rev_b import LcdCommRevB
from library.lcd.lcd_comm_rev_c import LcdCommRevC
from library.lcd.lcd_comm_rev_d import LcdCommRevD
from library.lcd.lcd_comm_weact_a import LcdCommWeActA
from library.lcd.lcd_comm_weact_b import LcdCommWeActB
from library.lcd.lcd_simulated import LcdSimulated
from library.lcd.lcd_virtual import LcdVirtual
from library.log import logger


def _get_full_path(path, name):
    if name:
        return path + name
    else:
        return None


def _get_theme_orientation() -> Orientation:
    orientation = config.THEME_DATA["display"].get("DISPLAY_ORIENTATION", "portrait")
    if orientation == 'portrait':
        if config.CONFIG_DATA["display"].get("DISPLAY_REVERSE", False):
            return Orientation.REVERSE_PORTRAIT
        else:
            return Orientation.PORTRAIT
    elif orientation == 'landscape':
        if config.CONFIG_DATA["display"].get("DISPLAY_REVERSE", False):
            return Orientation.REVERSE_LANDSCAPE
        else:
            return Orientation.LANDSCAPE
    else:
        logger.warning(f"Orientation '{orientation}' unknown, using portrait")
        return Orientation.PORTRAIT


def _get_theme_size() -> tuple[int, int]:
    if config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '0.96"':
        return 80, 160
    if config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '2.1"':
        return 480, 480
    elif config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '3.5"':
        return 320, 480
    elif config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '5"':
        return 480, 800
    elif config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '8.8"':
        return 480, 1920
    elif config.THEME_DATA["display"].get("DISPLAY_SIZE", '') == '9.2"':
        return 462, 1920
    else:
        logger.warning(
            f'Cannot find valid DISPLAY_SIZE property in selected theme {config.CONFIG_DATA["config"]["THEME"]}, defaulting to 3.5"')
        return 320, 480


class Display:
    def __init__(self):
        self.lcd = None
        width, height = _get_theme_size()
        if config.CONFIG_DATA["display"]["REVISION"] == "A":
            self.lcd = LcdCommRevA(com_port=config.CONFIG_DATA['config']['COM_PORT'],
                                   update_queue=config.update_queue)
        elif config.CONFIG_DATA["display"]["REVISION"] == "B":
            self.lcd = LcdCommRevB(com_port=config.CONFIG_DATA['config']['COM_PORT'],
                                   update_queue=config.update_queue)
        elif config.CONFIG_DATA["display"]["REVISION"] == "C":
            # Because of issue with Turing rev. C size auto-detection, manually configure screen width/height from theme
            self.lcd = LcdCommRevC(com_port=config.CONFIG_DATA['config']['COM_PORT'],
                                   update_queue=config.update_queue, display_width=width, display_height=height)
        elif config.CONFIG_DATA["display"]["REVISION"] == "D":
            self.lcd = LcdCommRevD(com_port=config.CONFIG_DATA['config']['COM_PORT'],
                                   update_queue=config.update_queue)
        elif config.CONFIG_DATA["display"]["REVISION"] == "WEACT_A":
            self.lcd = LcdCommWeActA(com_port=config.CONFIG_DATA['config']['COM_PORT'],
                                   update_queue=config.update_queue)
        elif config.CONFIG_DATA["display"]["REVISION"] == "WEACT_B":
            self.lcd = LcdCommWeActB(com_port=config.CONFIG_DATA['config']['COM_PORT'],
                                   update_queue=config.update_queue)
        elif config.CONFIG_DATA["display"]["REVISION"] == "SIMU":
            # Simulated display: always set width/height from theme
            self.lcd = LcdSimulated(display_width=width, display_height=height)
        else:
            logger.error("Unknown display revision '", config.CONFIG_DATA["display"]["REVISION"], "'")

        self.widget_enabled = config.CONFIG_DATA["config"].get("ENABLE_DESKTOP_WIDGET", False)
        self.screen_image = None

        if self.widget_enabled:
            # Delegar a LcdVirtual (canvas RGBA en memoria) cuando:
            #   1. lcd es None → revisión desconocida
            #   2. lcd es LcdSimulated → SIMU mode; el widget ES la pantalla virtual
            #   3. lcd tiene lcd_serial=None → hardware no conectado
            _no_hardware = (
                self.lcd is None or
                (hasattr(self.lcd, 'lcd_serial') and self.lcd.lcd_serial is None
                 and not isinstance(self.lcd, (LcdVirtual, LcdSimulated)))
            )
            if _no_hardware:
                width, height = _get_theme_size()
                logger.info("No physical display connected. Creating LcdVirtual for standalone widget mode.")
                self.lcd = LcdVirtual(display_width=width, display_height=height,
                                      update_queue=config.update_queue)
            self._setup_desktop_widget()

    def _setup_desktop_widget(self):
        from PIL import Image
        from library.desktop_widget import DesktopWidget

        self.widget_canvas = None

        # ── Modo LcdVirtual (widget standalone sin hardware) ────────────────
        # En modo virtual, el tema dibuja en el LcdVirtual.  Para lograr fondo
        # REALMENTE transparente interceptamos open_image y PIL.Image.new en
        # cada llamada de dibujo, igual que el shadow-renderer del LCD físico:
        #   · open_image  → si es el background del tema → Image transparente
        #   · PIL.Image.new('RGB',...) → convertir a RGBA transparente
        # Así solo quedan los píxeles de texto, barras y gráficos.
        if isinstance(self.lcd, LcdVirtual):
            import PIL.Image as _PIL_Image

            _bg_name = None
            if hasattr(config, 'THEME_DATA') and config.THEME_DATA:
                _bg_name = config.THEME_DATA.get('display', {}).get('background', '')

            _orig_open   = self.lcd.open_image
            _orig_new    = _PIL_Image.new
            _orig_disp   = self.lcd.DisplayPILImage

            def _virt_open_image(filepath):
                orig = _orig_open(filepath)
                _transp = config.CONFIG_DATA.get("config", {}).get("DESKTOP_WIDGET_TRANSPARENT_BG", False)
                if _bg_name and filepath.endswith(_bg_name) and _transp:
                    # Solo transparente: sustituir por versión alpha-vacía
                    import os
                    transp_path = filepath.replace(_bg_name, "background_transparent.png")
                    if os.path.exists(transp_path):
                        return _orig_open(transp_path).convert("RGBA")
                    return _PIL_Image.new("RGBA", orig.size, (0, 0, 0, 0))
                # Opaco o imagen normal: devolver el fondo real del tema
                return orig.convert("RGBA")

            def _virt_new(mode, size, color=0):
                _transp = config.CONFIG_DATA.get("config", {}).get("DESKTOP_WIDGET_TRANSPARENT_BG", False)
                # Solo en modo transparente: convertir RGB → RGBA vacío para que el fondo no bloquee
                if mode == 'RGB' and _transp:
                    return _orig_new("RGBA", size, (0, 0, 0, 0))
                # Modo opaco o modo no-RGB: dejar que el tema use sus propios colores
                return _orig_new(mode, size, color)

            def _virt_display(image, x=0, y=0, image_width=0, image_height=0):
                # Modo reemplazo (sin mask): los píxeles transparentes del nuevo frame
                # borran los píxeles opacos del frame anterior (evita acumulación de texto)
                image = image.convert("RGBA")
                with self.lcd.update_queue_mutex:
                    self.lcd.screen_image.paste(image, (x, y))

            def _make_transparent_wrapper(method_name):
                """Envuelve un método de dibujo del LCD:
                Siempre parchea open_image / Image.new / DisplayPILImage para
                controlar el fondo según el modo (transparente u opaco).
                """
                original_method = getattr(self.lcd.__class__, method_name)

                def _wrapper(*args, **kwargs):
                    # Parchear siempre — _virt_open_image y _virt_new leen el modo internamente
                    self.lcd.open_image       = _virt_open_image
                    self.lcd.DisplayPILImage  = _virt_display
                    _PIL_Image.new            = _virt_new
                    try:
                        original_method(self.lcd, *args, **kwargs)
                    except Exception:
                        pass
                    finally:
                        self.lcd.open_image      = _orig_open
                        self.lcd.DisplayPILImage = _orig_disp
                        _PIL_Image.new           = _orig_new

                return _wrapper

            for _m in ['DisplayText', 'DisplayProgressBar', 'DisplayLineGraph',
                       'DisplayRadialGraph', 'DisplayArcGraph', 'DisplayBitmap',
                       'DisplayRadialProgressBar']:
                if hasattr(self.lcd, _m):
                    setattr(self.lcd, _m, _make_transparent_wrapper(_m))

            # Interceptar DisplayPILImage directo (para imágenes estáticas del tema)
            def _intercept_direct_display(image, x=0, y=0, image_width=0, image_height=0):
                _transp = config.CONFIG_DATA.get("config", {}).get("DESKTOP_WIDGET_TRANSPARENT_BG", False)
                full_w = self.lcd.get_width()
                full_h = self.lcd.get_height()
                img_w  = image_width or image.size[0]
                img_h  = image_height or image.size[1]
                _is_fullscreen = (x == 0 and y == 0 and img_w >= full_w * 0.9 and img_h >= full_h * 0.9)

                if _is_fullscreen and _transp:
                    # Solo en transparente: omitir el fondo del tema
                    return

                # Pegar en modo reemplazo (opaco: fondo del tema; transparente: logos/íconos)
                image = image.convert("RGBA")
                with self.lcd.update_queue_mutex:
                    self.lcd.screen_image.paste(image, (x, y))

            self.lcd.DisplayPILImage = _intercept_direct_display

            # Interceptar Clear para resetear el canvas según el modo
            _orig_clear = self.lcd.Clear
            def _virt_clear():
                _transp = config.CONFIG_DATA.get("config", {}).get("DESKTOP_WIDGET_TRANSPARENT_BG", False)
                fill = (0, 0, 0, 0) if _transp else (0, 0, 0, 255)
                with self.lcd.update_queue_mutex:
                    self.lcd.screen_image = _PIL_Image.new(
                        "RGBA", (self.lcd.get_width(), self.lcd.get_height()), fill
                    )
            self.lcd.Clear = _virt_clear

            self.widget_canvas = None  # _get_canvas() lee lcd.screen_image directamente
            self.desktop_widget = DesktopWidget(self)
            return

        # ── Modo LCD físico / simulado (comportamiento original) ───────────
        self.original_display_pil_image = self.lcd.DisplayPILImage
        
        # We replace the intercept_display_image technique with a complete isolated double-render!
        def _execute_shadow_draw(method_name, *args, **kwargs):
            # Ejecutar el método original en la LCD física
            original_method = getattr(self.lcd.__class__, method_name)
            original_method(self.lcd, *args, **kwargs)
            
            # Ejecutar el método a la sombra en el canal de Widget
            import PIL.Image
            orig_open = self.lcd.open_image
            orig_display = self.lcd.DisplayPILImage
            orig_new = PIL.Image.new
            
            def mock_open(filepath):
                orig = orig_open(filepath)
                _transp = config.CONFIG_DATA.get("config", {}).get("DESKTOP_WIDGET_TRANSPARENT_BG", False)
                if not _transp:
                    return orig
                if getattr(config, 'THEME_DATA', {}):
                    bg_name = config.THEME_DATA.get('display', {}).get('background', 'background.png')
                    if filepath.endswith(bg_name):
                        # Usar background_transparent.png si existe en la carpeta del tema
                        import os
                        transp_path = filepath.replace(bg_name, "background_transparent.png")
                        if os.path.exists(transp_path):
                            return orig_open(transp_path).convert("RGBA")
                        # Fallback: imagen transparente en memoria
                        return PIL.Image.new("RGBA", orig.size, (0, 0, 0, 0))
                return orig.convert("RGBA")
                
            def mock_new(mode, size, color=0):
                if mode == 'RGB':
                    mode = 'RGBA'
                    color = (0, 0, 0, 0)
                return orig_new(mode, size, color)
                
            def mock_display(image, x=0, y=0, image_width=0, image_height=0):
                if self.widget_canvas is None:
                    self.widget_canvas = PIL.Image.new("RGBA", (self.lcd.get_width(), self.lcd.get_height()), (0, 0, 0, 0))
                # Modo reemplazo sin mask: borra texto anterior antes de dibujar el nuevo
                image = image.convert("RGBA")
                self.widget_canvas.paste(image, (x, y))
                
            # Parcheamos silenciosamente
            self.lcd.open_image = mock_open
            self.lcd.DisplayPILImage = mock_display
            PIL.Image.new = mock_new
            
            try:
                original_method(self.lcd, *args, **kwargs)
            except Exception:
                pass
            finally:
                # Restauramos la normalidad
                self.lcd.open_image = orig_open
                self.lcd.DisplayPILImage = orig_display
                PIL.Image.new = orig_new

        # Envolvemos todos los métodos de dibujo del objeto lcd
        def make_wrapper(method_name):
            def wrapper(*args, **kwargs):
                _execute_shadow_draw(method_name, *args, **kwargs)
            return wrapper
            
        for method in ['DisplayText', 'DisplayProgressBar', 'DisplayLineGraph', 'DisplayRadialGraph', 'DisplayArcGraph', 'DisplayBitmap']:
            if hasattr(self.lcd, method):
                setattr(self.lcd, method, make_wrapper(method))
                
        def intercept_display_image(image, x=0, y=0, image_width=0, image_height=0):
            if self.screen_image is None:
                self.screen_image = Image.new("RGB", (self.lcd.get_width(), self.lcd.get_height()), "black")
            
            _img_w = image_width or image.size[0]
            _img_h = image_height or image.size[1]
            if _img_w != image.size[0] or _img_h != image.size[1]:
                _cropped = image.crop((0, 0, _img_w, _img_h))
            else:
                _cropped = image
                
            with self.lcd.update_queue_mutex:
                self.screen_image.paste(_cropped, (x, y))

            # Transparencia: omitir fondos de pantalla completa del widget_canvas
            _transp = config.CONFIG_DATA.get("config", {}).get("DESKTOP_WIDGET_TRANSPARENT_BG", False)
            if _transp and x == 0 and y == 0:
                _fw = self.lcd.get_width()
                _fh = self.lcd.get_height()
                if _img_w >= _fw * 0.9 and _img_h >= _fh * 0.9:
                    self.original_display_pil_image(image, x, y, image_width, image_height)
                    return  # No pegar fondo en widget_canvas
                
            self.original_display_pil_image(image, x, y, image_width, image_height)
            
        self.lcd.DisplayPILImage = intercept_display_image
        
        self.original_clear = self.lcd.Clear
        def intercept_clear():
            if self.screen_image is not None:
                self.screen_image = Image.new("RGB", (self.lcd.get_width(), self.lcd.get_height()), "black")
            if getattr(self, "widget_canvas", None) is not None:
                self.widget_canvas = Image.new("RGBA", (self.lcd.get_width(), self.lcd.get_height()), (0, 0, 0, 0))
            self.original_clear()
        self.lcd.Clear = intercept_clear
        
        self.original_set_orientation = self.lcd.SetOrientation
        def intercept_set_orientation(*args, **kwargs):
            self.original_set_orientation(*args, **kwargs)
            if self.screen_image is not None:
                self.screen_image = Image.new("RGB", (self.lcd.get_width(), self.lcd.get_height()), "black")
            if getattr(self, "widget_canvas", None) is not None:
                self.widget_canvas = Image.new("RGBA", (self.lcd.get_width(), self.lcd.get_height()), (0, 0, 0, 0))
        self.lcd.SetOrientation = intercept_set_orientation
        
        self.desktop_widget = DesktopWidget(self)

    def initialize_display(self):
        # Reset screen in case it was in an unstable state (screen is also cleared)
        # Can be disabled by config. option. Assume true if key not present in config.yaml
        if config.CONFIG_DATA["display"].get("RESET_ON_STARTUP", True):
            self.lcd.Reset()
        else:
            logger.debug("RESET_ON_STARTUP is false: display will not be reset")

        # Send initialization commands
        self.lcd.InitializeComm()

        # Turn on display, set brightness and LEDs for supported HW
        self.turn_on()

        # Set orientation
        self.lcd.SetOrientation(_get_theme_orientation())

    def turn_on(self):
        # Turn screen on in case it was turned off previously
        self.lcd.ScreenOn()

        # Set brightness
        self.lcd.SetBrightness(config.CONFIG_DATA["display"]["BRIGHTNESS"])

        # Set backplate RGB LED color (for supported HW only)
        self.lcd.SetBackplateLedColor(config.THEME_DATA['display'].get("DISPLAY_RGB_LED", (255, 255, 255)))

    def turn_off(self):
        # Turn screen off
        self.lcd.ScreenOff()

        # Turn off backplate RGB LED
        self.lcd.SetBackplateLedColor(led_color=(0, 0, 0))

    def display_static_images(self):
        if config.THEME_DATA.get('static_images', False):
            for image in config.THEME_DATA['static_images']:
                logger.debug(f"Drawing Image: {image}")
                self.lcd.DisplayBitmap(
                    bitmap_path=config.THEME_DATA['PATH'] + config.THEME_DATA['static_images'][image].get("PATH"),
                    x=config.THEME_DATA['static_images'][image].get("X", 0),
                    y=config.THEME_DATA['static_images'][image].get("Y", 0),
                    width=config.THEME_DATA['static_images'][image].get("WIDTH", 0),
                    height=config.THEME_DATA['static_images'][image].get("HEIGHT", 0)
                )

    def display_static_text(self):
        if config.THEME_DATA.get('static_text', False):
            for text in config.THEME_DATA['static_text']:
                logger.debug(f"Drawing Text: {text}")
                self.lcd.DisplayText(
                    text=config.THEME_DATA['static_text'][text].get("TEXT"),
                    x=config.THEME_DATA['static_text'][text].get("X", 0),
                    y=config.THEME_DATA['static_text'][text].get("Y", 0),
                    width=config.THEME_DATA['static_text'][text].get("WIDTH", 0),
                    height=config.THEME_DATA['static_text'][text].get("HEIGHT", 0),
                    font=config.FONTS_DIR + config.THEME_DATA['static_text'][text].get("FONT",
                                                                                       "roboto-mono/RobotoMono-Regular.ttf"),
                    font_size=config.THEME_DATA['static_text'][text].get("FONT_SIZE", 10),
                    font_color=config.THEME_DATA['static_text'][text].get("FONT_COLOR", (0, 0, 0)),
                    background_color=config.THEME_DATA['static_text'][text].get("BACKGROUND_COLOR", (255, 255, 255)),
                    background_image=_get_full_path(config.THEME_DATA['PATH'],
                                                    config.THEME_DATA['static_text'][text].get("BACKGROUND_IMAGE",
                                                                                               None)),
                    align=config.THEME_DATA['static_text'][text].get("ALIGN", "left"),
                    anchor=config.THEME_DATA['static_text'][text].get("ANCHOR", "lt"),
                    outline_width=config.THEME_DATA['static_text'][text].get("FONT_OUTLINE", 2),
                    outline_color=config.THEME_DATA['static_text'][text].get("FONT_OUTLINE_COLOR", (0, 0, 0)),
                )


display = Display()
