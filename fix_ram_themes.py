import os

MAIN_DIRECTORY = r"C:\Users\dionnys\Documents\Devs\turing-smart-screen-python"

for i in range(1, 4):
    theme_yaml = os.path.join(MAIN_DIRECTORY, f"res/themes/ARC_Raiders_v{i}/theme.yaml")
    if os.path.exists(theme_yaml):
        with open(theme_yaml, "r", encoding="utf-8") as f:
            yaml_content = f.read()

        # Fix MEMORY stats section keys
        # Replace the incorrectly named block in MEMORY
        incorrect_memory_block = """  MEMORY:
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
        BACKGROUND_IMAGE: background.png"""
        
        correct_memory_block = """  MEMORY:
    INTERVAL: 1
    VIRTUAL:
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
      PERCENT_TEXT:
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
        BACKGROUND_IMAGE: background.png"""

        yaml_content = yaml_content.replace(incorrect_memory_block, correct_memory_block)
        
        with open(theme_yaml, "w", encoding="utf-8") as f:
            f.write(yaml_content)

print("RAM stats fixed!")
