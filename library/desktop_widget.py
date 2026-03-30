import tkinter as tk
from threading import Thread
import time
from PIL import Image, ImageTk, ImageDraw
from library import config
import os
import ruamel.yaml

class DesktopWidget:
    def __init__(self, display_instance):
        self.display = display_instance
        
        self.cfg = config.CONFIG_DATA.get("config", {})
        self.scale = float(self.cfg.get("DESKTOP_WIDGET_SCALE", 100)) / 100.0
        self.alpha = float(self.cfg.get("DESKTOP_WIDGET_ALPHA", 100)) / 100.0
        self.on_top = self.cfg.get("DESKTOP_WIDGET_ON_TOP", True)
        self.locked = self.cfg.get("DESKTOP_WIDGET_LOCKED", False)
        
        self.radius = int(self.cfg.get("DESKTOP_WIDGET_RADIUS", 0))
        self.transparent_bg = self.cfg.get("DESKTOP_WIDGET_TRANSPARENT_BG", False)
        
        Thread(target=self._run_widget, daemon=True).start()

    def _save_position(self, x, y):
        main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(main_dir, "config.yaml")
        try:
            with open(config_path, "rt", encoding='utf8') as stream:
                yaml = ruamel.yaml.YAML()
                yaml.preserve_quotes = True
                full_cfg = yaml.load(stream)
            
            full_cfg['config']['DESKTOP_WIDGET_X'] = x
            full_cfg['config']['DESKTOP_WIDGET_Y'] = y
            
            with open(config_path, "w", encoding='utf-8') as file:
                yaml.dump(full_cfg, file)
        except Exception:
            pass

    def _run_widget(self):
        root = tk.Tk()
        root.title("Turing Desktop Widget")
        root.overrideredirect(True) # Quitar bordes
        
        if self.on_top:
            root.attributes("-topmost", True) # Siempre arriba
        else:
            root.lower() # Al fondo
            
        if self.alpha < 1.0:
            root.attributes("-alpha", self.alpha)
            
        trans_color = '#000000' if self.transparent_bg else '#ff00ff'
        
        try:
            root.attributes("-transparentcolor", trans_color)
            root.configure(bg=trans_color)
        except:
            root.configure(bg='black')
        
        saved_x = self.cfg.get("DESKTOP_WIDGET_X", 100)
        saved_y = self.cfg.get("DESKTOP_WIDGET_Y", 100)
        root.geometry(f"+{saved_x}+{saved_y}")
        
        self.label = tk.Label(root, bg=trans_color, borderwidth=0, highlightthickness=0)
        self.label.pack(expand=True, fill="both")
        
        self.x, self.y = 0, 0
        def start_move(event):
            if self.locked: return
            self.x = event.x
            self.y = event.y

        def stop_move(event):
            if self.locked: return
            if self.x is not None and self.y is not None:
                self._save_position(root.winfo_x(), root.winfo_y())
            self.x = None
            self.y = None

        def do_move(event):
            if self.locked or self.x is None or self.y is None: return
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = root.winfo_x() + deltax
            y = root.winfo_y() + deltay
            root.geometry(f"+{x}+{y}")

        self.label.bind("<ButtonPress-1>", start_move)
        self.label.bind("<ButtonRelease-1>", stop_move)
        self.label.bind("<B1-Motion>", do_move)
        
        def close_widget(event):
            if not self.locked:
                root.destroy()
            
        self.label.bind("<Double-Button-1>", close_widget)

        def _update():
            if hasattr(self.display, 'screen_image') and self.display.screen_image is not None:
                try:
                    with self.display.lcd.update_queue_mutex:
                        img = self.display.screen_image.copy()
                    
                    if abs(self.scale - 1.0) > 0.01:
                        new_w = int(img.size[0] * self.scale)
                        new_h = int(img.size[1] * self.scale)
                        # Usar bicubic para los reescalados, o dejar que la mascara se aplique sin antialias conflictivo
                        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        
                    w, h = img.size
                    
                    if self.radius > 0:
                        mask = Image.new("L", img.size, 0)
                        draw = ImageDraw.Draw(mask)
                        draw.rounded_rectangle((0, 0, w, h), radius=self.radius, fill=255)
                        
                        final = Image.new("RGB", img.size, trans_color)
                        final.paste(img, mask=mask)
                        img = final
                        
                    if root.winfo_width() != w or root.winfo_height() != h:
                        if root.winfo_width() <= 1:
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
