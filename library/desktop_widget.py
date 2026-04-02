import os
import threading
import ruamel.yaml
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from library import config


class DesktopWidget:
    """
    Widget de escritorio para el Turing Smart Screen.

    Funciona de forma completamente independiente del hardware:
    - Si hay pantalla física (LCD real): renderiza el espejo del canvas de dibujo.
    - Si no hay pantalla (LcdVirtual): renderiza el canvas RGBA en memoria.

    La transparencia real funciona via PyQt6 (WA_TranslucentBackground +
    canvas RGBA puro). Si PyQt6 no está instalado, usa tkinter con
    transparentcolor como fallback.
    """

    def __init__(self, display_instance):
        self.display = display_instance

        self.cfg = config.CONFIG_DATA.get("config", {})
        self.scale = float(self.cfg.get("DESKTOP_WIDGET_SCALE", 100)) / 100.0
        self.alpha = float(self.cfg.get("DESKTOP_WIDGET_ALPHA", 100)) / 100.0
        self.on_top = self.cfg.get("DESKTOP_WIDGET_ON_TOP", True)
        self.locked = self.cfg.get("DESKTOP_WIDGET_LOCKED", False)
        self.radius = int(self.cfg.get("DESKTOP_WIDGET_RADIUS", 0))
        self.transparent_bg = self.cfg.get("DESKTOP_WIDGET_TRANSPARENT_BG", False)


    # ── Helpers ──────────────────────────────────────────────────────────

    def _get_canvas(self):
        """
        Retorna el canvas RGBA actual del sistema de renderizado, sin importar
        si el backend es físico (widget_canvas shadow-renderer) o virtual
        (LcdVirtual.screen_image).

        Priority:
        1. display.widget_canvas  — shadow-renderer sobre LCD físico/simulado
        2. display.lcd.screen_image — LcdVirtual (canvas RGBA nativo)
        3. display.screen_image  — espejo RGB del LCD físico (fallback opaco)
        """
        d = self.display

        if getattr(d, "widget_canvas", None) is not None:
            return d.widget_canvas

        lcd = getattr(d, "lcd", None)
        if lcd is not None and hasattr(lcd, "screen_image"):
            return lcd.screen_image

        if getattr(d, "screen_image", None) is not None:
            return d.screen_image

        return None

    def _get_mutex(self):
        """Retorna el mutex del LCD si existe, sino un lock dummy."""
        lcd = getattr(self.display, "lcd", None)
        if lcd is not None and hasattr(lcd, "update_queue_mutex"):
            return lcd.update_queue_mutex
        return threading.Lock()

    def _save_position(self, x, y):
        main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(main_dir, "config.yaml")
        try:
            with open(config_path, "rt", encoding="utf8") as stream:
                yaml = ruamel.yaml.YAML()
                yaml.preserve_quotes = True
                full_cfg = yaml.load(stream)

            full_cfg["config"]["DESKTOP_WIDGET_X"] = x
            full_cfg["config"]["DESKTOP_WIDGET_Y"] = y

            with open(config_path, "w", encoding="utf-8") as file:
                yaml.dump(full_cfg, file)
        except Exception:
            pass

    def _apply_scale_and_radius(self, img: Image.Image) -> Image.Image:
        """Aplica escala y bordes redondeados (si corresponde) a una imagen RGBA."""
        from PIL import ImageFilter

        scaled = False
        if abs(self.scale - 1.0) > 0.01:
            new_w = int(img.size[0] * self.scale)
            new_h = int(img.size[1] * self.scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            scaled = True

        # Post-escala: sharpen suave para recuperar nitidez de texto y bordes
        # Solo cuando hay reducción real — UnsharpMask (radius, percent, threshold)
        if scaled and self.scale < 0.99:
            # Separar alpha para no sharpenear el canal de transparencia
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = rgb.filter(ImageFilter.UnsharpMask(radius=0.6, percent=110, threshold=2))
            r2, g2, b2 = rgb.split()
            img = Image.merge("RGBA", (r2, g2, b2, a))

        if self.radius > 0:
            w, h = img.size
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, w, h), radius=self.radius, fill=255)
            img = img.convert("RGBA")
            r, g, b, a = img.split()
            a = Image.composite(a, Image.new("L", img.size, 0), mask)
            img = Image.merge("RGBA", (r, g, b, a))

        return img

    # ── Backend selector ─────────────────────────────────────────────────

    def run(self):
        use_pyqt = False
        try:
            from PyQt6.QtWidgets import QApplication, QLabel, QWidget  # noqa: F401
            from PyQt6.QtCore import Qt, QTimer  # noqa: F401
            from PyQt6.QtGui import QImage, QPixmap  # noqa: F401
            use_pyqt = True
        except ImportError:
            use_pyqt = False

        if use_pyqt:
            self._run_widget_pyqt()
        else:
            self._run_widget_tkinter()

    # ── PyQt6 backend (preferido — transparencia real RGBA) ───────────────

    def _run_widget_pyqt(self):
        import sys
        from PyQt6.QtWidgets import QApplication, QLabel, QWidget
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QPixmap
        from PIL.ImageQt import ImageQt

        parent_self = self  # alias para closures

        class TranslucentWidget(QWidget):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._drag_pos = None

            def mousePressEvent(self, event):
                if parent_self.locked:
                    return
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_pos = (
                        event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    )

            def mouseMoveEvent(self, event):
                if parent_self.locked or not self._drag_pos:
                    return
                if event.buttons() == Qt.MouseButton.LeftButton:
                    self.move(event.globalPosition().toPoint() - self._drag_pos)

            def mouseReleaseEvent(self, event):
                if parent_self.locked:
                    return
                if event.button() == Qt.MouseButton.LeftButton:
                    parent_self._save_position(self.x(), self.y())
                    self._drag_pos = None

            def mouseDoubleClickEvent(self, event):
                if not parent_self.locked and event.button() == Qt.MouseButton.LeftButton:
                    self.close()

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        try:
            self.widget = TranslucentWidget()
            self.widget.setWindowTitle("Turing Desktop Widget")

            flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
            if self.on_top:
                flags |= Qt.WindowType.WindowStaysOnTopHint
            else:
                flags |= Qt.WindowType.WindowStaysOnBottomHint

            self.widget.setWindowFlags(flags)

            # ── Transparencia real: el widget tiene fondo 100 % transparente ──
            # WA_TranslucentBackground hace que el compositor de Windows respete
            # el canal alpha de cada pixel — no se agrega ningún fondo sólido.
            self.widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

            if self.alpha < 1.0:
                self.widget.setWindowOpacity(self.alpha)

            saved_x = self.cfg.get("DESKTOP_WIDGET_X", 100)
            saved_y = self.cfg.get("DESKTOP_WIDGET_Y", 100)
            self.widget.move(saved_x, saved_y)

            self.label = QLabel(self.widget)
            self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.label.move(0, 0)
            # label también transparente — solo dibujamos el pixmap
            self.label.setStyleSheet("background: transparent;")

            self._qimg_cache = None

            # Inicializar con el modo ACTUAL — evita el Clear() espúrio en el primer frame
            _initial_transp = config.CONFIG_DATA.get("config", {}).get("DESKTOP_WIDGET_TRANSPARENT_BG", False)
            _last_transp_mode = [_initial_transp]

            def _update():
                canvas = parent_self._get_canvas()
                if canvas is None:
                    return

                try:
                    # Leer transparent_bg dinámicamente desde CONFIG_DATA (live reload)
                    _transp = config.CONFIG_DATA.get("config", {}).get("DESKTOP_WIDGET_TRANSPARENT_BG", False)

                    # Si el modo cambió → refrescar fondo completo y esperar un frame
                    if _transp != _last_transp_mode[0]:
                        _last_transp_mode[0] = _transp
                        try:
                            # Re-dibujar imágenes y textos estáticos con el nuevo modo
                            parent_self.display.display_static_images()
                            parent_self.display.display_static_text()
                        except Exception:
                            pass
                        return  # esperar al siguiente frame con el fondo ya pintado

                    with parent_self._get_mutex():
                        img = canvas.copy()

                    img = img.convert("RGBA")

                    # Si NO queremos fondo transparente: fondo negro opaco
                    if not _transp:
                        bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
                        bg.paste(img, mask=img)
                        img = bg

                    img = parent_self._apply_scale_and_radius(img)
                    w, h = img.size

                    if self.widget.width() != w or self.widget.height() != h:
                        self.widget.resize(w, h)

                    self._qimg_cache = ImageQt(img)
                    pixmap = QPixmap.fromImage(self._qimg_cache)
                    self.label.resize(w, h)
                    self.label.setPixmap(pixmap)

                    if not parent_self.on_top:
                        self.widget.lower()

                except Exception:
                    pass

            self.timer = QTimer(self.widget)
            self.timer.timeout.connect(_update)
            self.timer.start(100)

            self.widget.show()
            app.exec()

        except Exception:
            pass

    # ── Tkinter backend (fallback) ────────────────────────────────────────

    def _run_widget_tkinter(self):
        root = tk.Tk()
        root.title("Turing Desktop Widget")
        root.overrideredirect(True)

        if self.on_top:
            root.attributes("-topmost", True)
        else:
            root.lower()

        if self.alpha < 1.0:
            root.attributes("-alpha", self.alpha)

        # En tkinter usamos un color chroma-key para "transparencia"
        # El negro puro (#000000) funciona mejor con la mayoría de temas.
        # Si el usuario quiere fondo transparente usamos negro chroma.
        # Si NO quiere transparencia, usamos magenta para evitar conflictos.
        if self.transparent_bg:
            trans_color = "#000000"
        else:
            trans_color = "#1a1a1a"  # Fondo casi negro, sin chroma-key

        try:
            if self.transparent_bg:
                root.attributes("-transparentcolor", trans_color)
            root.configure(bg=trans_color)
        except Exception:
            root.configure(bg="black")

        saved_x = self.cfg.get("DESKTOP_WIDGET_X", 100)
        saved_y = self.cfg.get("DESKTOP_WIDGET_Y", 100)
        root.geometry(f"+{saved_x}+{saved_y}")

        self.label = tk.Label(root, bg=trans_color, borderwidth=0, highlightthickness=0)
        self.label.pack(expand=True, fill="both")

        self._drag_x, self._drag_y = 0, 0

        def start_move(event):
            if self.locked:
                return
            self._drag_x = event.x
            self._drag_y = event.y

        def stop_move(event):
            if self.locked:
                return
            self._save_position(root.winfo_x(), root.winfo_y())
            self._drag_x = None
            self._drag_y = None

        def do_move(event):
            if self.locked or self._drag_x is None:
                return
            x = root.winfo_x() + (event.x - self._drag_x)
            y = root.winfo_y() + (event.y - self._drag_y)
            root.geometry(f"+{x}+{y}")

        def close_widget(event):
            if not self.locked:
                root.destroy()

        self.label.bind("<ButtonPress-1>", start_move)
        self.label.bind("<ButtonRelease-1>", stop_move)
        self.label.bind("<B1-Motion>", do_move)
        self.label.bind("<Double-Button-1>", close_widget)

        def _update():
            canvas = self._get_canvas()
            if canvas is not None:
                try:
                    with self._get_mutex():
                        img = canvas.copy()

                    # Para tkinter: si transparent_bg, pintar los pixels negros
                    # del canvas como negro exacto (el chroma-key los volverá transparentes)
                    if self.transparent_bg:
                        # Convertir a RGB — los píxeles con alpha 0 quedan negros (=chroma-key)
                        bg = Image.new("RGB", img.size, (0, 0, 0))
                        if img.mode == "RGBA":
                            bg.paste(img.convert("RGB"), mask=img.split()[3])
                        else:
                            bg = img.convert("RGB")
                        img = bg
                    else:
                        img = img.convert("RGB")

                    img = self._apply_scale_and_radius(img)
                    w, h = img.size

                    if root.winfo_width() != w or root.winfo_height() != h:
                        root.geometry(f"{w}x{h}")

                    self.tk_image = ImageTk.PhotoImage(img)
                    self.label.config(image=self.tk_image)
                    self.label.image = self.tk_image

                    if not self.on_top:
                        root.lower()

                except Exception:
                    pass

            root.after(100, _update)

        _update()
        root.mainloop()
