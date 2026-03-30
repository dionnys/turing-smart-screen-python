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

"""
LcdVirtual: LCD headless/virtual completamente desacoplado del hardware físico.
No requiere puerto serial, no abre webserver, no hace I/O.
Mantiene un canvas RGBA en memoria (screen_image) al que los elementos del
tema pueden renderizar normalmente, y el DesktopWidget lee ese canvas.

Se usa como fallback cuando ENABLE_DESKTOP_WIDGET=True pero no hay pantalla
física conectada o el COM port no está disponible.
"""

from library.lcd.lcd_comm import LcdComm, Orientation
from PIL import Image

from typing import Optional, Tuple
import queue


class LcdVirtual(LcdComm):
    """
    LCD headless — existe solo en memoria.  Toda operación de dibujo
    escribe en self.screen_image (RGBA).  No hay serial ni red.
    """

    def __init__(
        self,
        display_width: int = 320,
        display_height: int = 480,
        update_queue: Optional[queue.Queue] = None,
    ):
        # No necesitamos com_port para nada, pero la base lo recibe
        LcdComm.__init__(self, "NONE", display_width, display_height, update_queue)
        self.orientation = Orientation.PORTRAIT
        # Canvas principal: completamente transparente en inicio
        self.screen_image = Image.new("RGBA", (display_width, display_height), (0, 0, 0, 0))

    # ── Métodos abstractos requeridos por LcdComm ────────────────────────

    @staticmethod
    def auto_detect_com_port() -> Optional[str]:
        return None

    def InitializeComm(self):
        # No hardware to initialize — virtual display lives entirely in memory
        pass

    def Reset(self):
        # No hardware to reset — noop for virtual display
        pass

    def Clear(self):
        with self.update_queue_mutex:
            self.screen_image = Image.new(
                "RGBA", (self.get_width(), self.get_height()), (0, 0, 0, 0)
            )

    def ScreenOff(self):
        # Virtual display has no backlight to control
        pass

    def ScreenOn(self):
        # Virtual display has no backlight to control
        pass

    def SetBrightness(self, level: int = 25):
        # Virtual display has no brightness hardware
        pass

    def SetBackplateLedColor(self, led_color: Tuple[int, int, int] = (255, 255, 255)):
        # Virtual display has no RGB LED hardware
        pass

    def SetOrientation(self, orientation: Orientation = Orientation.PORTRAIT):
        self.orientation = orientation
        with self.update_queue_mutex:
            self.screen_image = Image.new(
                "RGBA", (self.get_width(), self.get_height()), (0, 0, 0, 0)
            )

    def DisplayPILImage(
        self,
        image: Image.Image,
        x: int = 0,
        y: int = 0,
        image_width: int = 0,
        image_height: int = 0,
    ):
        if not image_width:
            image_width = image.size[0]
        if not image_height:
            image_height = image.size[1]

        # Respetar límites de pantalla
        image_width = min(image_width, self.get_width() - x)
        image_height = min(image_height, self.get_height() - y)

        if image_width <= 0 or image_height <= 0:
            return

        if image_width != image.size[0] or image_height != image.size[1]:
            image = image.crop((0, 0, image_width, image_height))

        # Convertir a RGBA para preservar transparencia
        image = image.convert("RGBA")

        with self.update_queue_mutex:
            self.screen_image.paste(image, (x, y), mask=image)

    # ── openSerial / closeSerial: no-ops seguros ─────────────────────────

    def openSerial(self):
        # No serial port to open — this override prevents the base-class blocking loop
        pass

    def closeSerial(self):
        # No serial port to close — noop for virtual display
        pass
