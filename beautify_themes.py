import os

MAIN_DIRECTORY = r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python"

for i in range(1, 4):
    theme_dir = os.path.join(MAIN_DIRECTORY, f"res/themes/ARC_Raiders_v{i}")
    yaml_path = os.path.join(theme_dir, "theme.yaml")
    
    if not os.path.exists(theme_dir): continue
    
    yaml_content = f"""---
author: "@dionnys"

display:
  DISPLAY_SIZE: 9.2"
  DISPLAY_ORIENTATION: landscape
  width: 1920
  height: 462
  background: 'background.png'

static_images:
  BACKGROUND:
    PATH:  background.png
    X: 0
    Y: 0
    WIDTH: 1920
    HEIGHT: 462

static_text:
  CPU:
   TEXT: CPU
   X: 1120
   Y: 44
   FONT_SIZE: 34
   FONT_COLOR: 255, 255, 255
   FONT: racespace/RACESPACEREGULAR-Extended.otf
   BACKGROUND_IMAGE: background.png
  GPU:
   TEXT: GPU
   X: 1120
   Y: 85
   FONT_SIZE: 34
   FONT_COLOR: 255, 255, 255
   FONT: racespace/RACESPACEREGULAR-Extended.otf
   BACKGROUND_IMAGE: background.png
  RAM:
   TEXT: RAM
   X: 1120
   Y: 126
   FONT_SIZE: 34
   FONT_COLOR: 255, 255, 255
   FONT: racespace/RACESPACEREGULAR-Extended.otf
   BACKGROUND_IMAGE: background.png
  VRAM:
   TEXT: VRAM
   X: 1120
   Y: 167
   FONT_SIZE: 34
   FONT_COLOR: 255, 255, 255
   FONT: racespace/RACESPACEREGULAR-Extended.otf
   BACKGROUND_IMAGE: background.png

STATS:
  CPU:
    PERCENTAGE:
      INTERVAL: 1
      TEXT:
        SHOW: True
        SHOW_UNIT: True
        X: 1204
        Y: 40
        WIDTH: 100
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: 255, 255, 255
        FONT: racespace/RACESPACEREGULAR-Extended.otf
        BACKGROUND_IMAGE: background.png
      GRAPH:
        SHOW: True
        X: 1306
        Y: 48
        WIDTH: 374
        HEIGHT: 16
        MIN_VALUE: 0
        MAX_VALUE: 100
        BAR_COLOR: 246, 10, 8
        BAR_OUTLINE: False
        BACKGROUND_COLOR: 35, 35, 35
    TEMPERATURE:
      INTERVAL: 5
      TEXT:
        SHOW: True
        SHOW_UNIT: True
        X: 1780
        Y: 40
        WIDTH: 100
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: 255, 255, 255
        FONT: racespace/RACESPACEREGULAR-Extended.otf
        BACKGROUND_IMAGE: background.png

  GPU:
    INTERVAL: 1
    PERCENTAGE:
      GRAPH:
        SHOW: True
        X: 1306
        Y: 89
        WIDTH: 374
        HEIGHT: 16
        MIN_VALUE: 0
        MAX_VALUE: 100
        BAR_COLOR: 246, 10, 8
        BAR_OUTLINE: False
        BACKGROUND_COLOR: 35, 35, 35
      TEXT:
        SHOW: True
        SHOW_UNIT: True
        X: 1204
        Y: 81
        WIDTH: 100
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: 255, 255, 255
        FONT: racespace/RACESPACEREGULAR-Extended.otf
        BACKGROUND_IMAGE: background.png
    TEMPERATURE:
      TEXT:
        SHOW: True
        SHOW_UNIT: True
        X: 1780
        Y: 81
        WIDTH: 100
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: 255, 255, 255
        FONT: racespace/RACESPACEREGULAR-Extended.otf
        BACKGROUND_IMAGE: background.png
    MEMORY_USED:
      TEXT:
        SHOW: True
        SHOW_UNIT: True
        X: 1204
        Y: 164
        WIDTH: 130
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: 255, 255, 255
        FONT: racespace/RACESPACEREGULAR-Extended.otf
        BACKGROUND_IMAGE: background.png

  MEMORY:
    INTERVAL: 1
    PERCENTAGE:
      GRAPH:
        SHOW: True
        X: 1306
        Y: 130
        WIDTH: 374
        HEIGHT: 16
        MIN_VALUE: 0
        MAX_VALUE: 100
        BAR_COLOR: 246, 10, 8
        BAR_OUTLINE: False
        BACKGROUND_COLOR: 35, 35, 35
      TEXT:
        SHOW: True
        SHOW_UNIT: True
        X: 1204
        Y: 122
        WIDTH: 100
        HEIGHT: 37
        ANCHOR: mm
        FONT_SIZE: 34
        FONT_COLOR: 255, 255, 255
        FONT: racespace/RACESPACEREGULAR-Extended.otf
        BACKGROUND_IMAGE: background.png
"""
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

print("Beautiful data styles applied to all themes!")
