# SPDX-License-Identifier: GPL-3.0-or-later
#
# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/dionnys/turing-smart-screen-python/
#
# Copyright (C) 2021 dionnys (dionnys)
# Copyright (C) 2022 Rollbacke
# Copyright (C) 2022 Ebag333
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

import os
import queue
import sys
import threading
import time
from pathlib import Path
import yaml

from library.log import logger


def load_yaml(configfile):
    with open(configfile, "rt", encoding='utf8') as stream:
        yamlconfig = yaml.safe_load(stream)
        return yamlconfig


PATH = sys.path[0]
MAIN_DIRECTORY = Path(__file__).parent.parent.resolve()
FONTS_DIR = str(MAIN_DIRECTORY / "res" / "fonts") + "/"
CONFIG_DATA = load_yaml(MAIN_DIRECTORY / "config.yaml")
THEME_DEFAULT = load_yaml(MAIN_DIRECTORY / "res/themes/default.yaml")
THEME_DATA = None


def copy_default(default, theme):
    """recursively supply default values into a dict of dicts of dicts ...."""
    for k, v in default.items():
        if k not in theme:
            theme[k] = v
        if type(v) == type({}):
            copy_default(default[k], theme[k])


def load_theme():
    global THEME_DATA
    try:
        theme_path = Path("res/themes/" + CONFIG_DATA['config']['THEME'])
        logger.info("Loading theme %s from %s" % (CONFIG_DATA['config']['THEME'], theme_path / "theme.yaml"))
        THEME_DATA = load_yaml(MAIN_DIRECTORY / theme_path / "theme.yaml")
        THEME_DATA['PATH'] = str(MAIN_DIRECTORY / theme_path) + "/"
    except:
        logger.error("Theme not found or contains errors!")
        try:
            sys.exit(0)
        except:
            os._exit(0)

    copy_default(THEME_DEFAULT, THEME_DATA)


def check_theme_compatible(display_size: str):
    # Check if theme is compatible with hardware revision
    if display_size != THEME_DATA['display'].get("DISPLAY_SIZE", '3.5"'):
        logger.error("The selected theme " + CONFIG_DATA['config'][
            'THEME'] + " is not compatible with your display revision " + CONFIG_DATA["display"]["REVISION"])
        try:
            sys.exit(0)
        except:
            os._exit(0)


# Load theme on import
load_theme()

# Queue containing the serial requests to send to the screen
update_queue = queue.Queue()

_CONFIG_PATH = MAIN_DIRECTORY / "config.yaml"


def reload_config():
    """Recarga config.yaml en CONFIG_DATA sin reemplazar la referencia al dict.
    Todos los módulos que ya tienen 'from library import config' verán los nuevos
    valores porque actualizamos el mismo objeto en memoria."""
    global CONFIG_DATA
    try:
        fresh = load_yaml(_CONFIG_PATH)
        CONFIG_DATA.clear()
        CONFIG_DATA.update(fresh)
        logger.debug("config.yaml recargado automáticamente.")
    except Exception as e:
        logger.warning(f"Error recargando config.yaml: {e}")


def _start_config_watcher():
    """Hilo daemon que vigila config.yaml y recarga cuando detecta cambios."""
    _last_mtime = [0.0]  # lista para mutabilidad en closure

    def _watch():
        while True:
            try:
                mtime = os.stat(_CONFIG_PATH).st_mtime
                if mtime != _last_mtime[0]:
                    if _last_mtime[0] != 0.0:  # ignorar la primera lectura
                        reload_config()
                    _last_mtime[0] = mtime
            except Exception:
                pass
            time.sleep(1)  # verificar cada segundo

    t = threading.Thread(target=_watch, daemon=True, name="config-watcher")
    t.start()


_start_config_watcher()
