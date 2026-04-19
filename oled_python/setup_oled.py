#!/usr/bin/env python3
import subprocess
import re
import os
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106, ssd1306, ssd1309
from PIL import ImageFont, Image, ImageDraw

CONFIG_FILE = "/home/moode/ddplayer_oled.conf"
MAIN_SCRIPT = "/home/moode/ddplayer_oled.py"

subprocess.run(["sudo", "systemctl", "stop", "ddplayer-oled"], capture_output=True)

fPath = "/usr/share/fonts/truetype/Monocraft.ttf"

DISPLAY_TYPES = [
    {"name": "Option 1 - sh1106",  "type": "sh1106",  "cls": sh1106},
    {"name": "Option 2 - ssd1306", "type": "ssd1306", "cls": ssd1306},
    {"name": "Option 3 - ssd1309", "type": "ssd1309", "cls": ssd1309},
]

CONTRAST_VARIANTS = [10, 30, 50, 100, 150, 200, 255]

FONT_VARIANTS = [
    {"font_large": 20, "font_small": 9},
    {"font_large": 18, "font_small": 9},
    {"font_large": 16, "font_small": 8},
]

def load_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    config[k.strip()] = v.strip()
    return config

def save_config(display_type, contrast, font_large, font_small):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"DISPLAY_TYPE={display_type}\n")
        f.write(f"DISPLAY_CONTRAST={contrast}\n")
        f.write(f"FONT_LARGE={font_large}\n")
        f.write(f"FONT_SMALL={font_small}\n")

def apply_config(display_type, contrast, font_large, font_small):
    with open(MAIN_SCRIPT, "r") as f:
        content = f.read()
    content = re.sub(r'DISPLAY_TYPE\s*=\s*"[^"]*"',  f'DISPLAY_TYPE     = "{display_type}"', content)
    content = re.sub(r'DISPLAY_CONTRAST\s*=\s*\d+',   f'DISPLAY_CONTRAST = {contrast}',       content)
    content = re.sub(r'FONT_LARGE\s*=\s*\d+',         f'FONT_LARGE       = {font_large}',      content)
    content = re.sub(r'FONT_SMALL\s*=\s*\d+',         f'FONT_SMALL       = {font_small}',      content)
    with open(MAIN_SCRIPT, "w") as f:
        f.write(content)

def make_device(cls):
    serial = i2c(port=1, address=0x3C)
    return cls(serial, width=128, height=64)

def show_test(device, contrast, font_large, font_small, label):
    device.contrast(contrast)
    fL = ImageFont.truetype(fPath, font_large)
    fS = ImageFont.truetype(fPath, font_small)
    img = Image.new("1", (128, 64), 0)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0),(127,63)], outline=1)
    draw.text((2, 2),  "192.168.1.100  ETH",  font=fS, fill=1)
    draw.text((2, 13), "23:59:59",             font=fL, fill=1)
    draw.text((2, 13+font_large+2), "12.04.2025", font=fS, fill=1)
    draw.text((2, 54), "DF:SHARP   OPTICAL",  font=fS, fill=1)
    device.display(img.convert(device.mode))
    print(f"  {label}")

# Show current config if exists
old_config = load_config()
if old_config:
    print("=== Current settings ===")
    print(f"  DISPLAY_TYPE     = {old_config.get('DISPLAY_TYPE','?')}")
    print(f"  DISPLAY_CONTRAST = {old_config.get('DISPLAY_CONTRAST','?')}")
    print(f"  FONT_LARGE       = {old_config.get('FONT_LARGE','?')}")
    print(f"  FONT_SMALL       = {old_config.get('FONT_SMALL','?')}")
    print("")

# STEP 1 - display type
print("=== Step 1: Display type ===")
device = None
for i, d in enumerate(DISPLAY_TYPES):
    if device:
        try: device.cleanup()
        except: pass
    device = make_device(d["cls"])
    show_test(device, 50, 20, 9, f"{d['name']} ({i+1}/{len(DISPLAY_TYPES)})")
    input("Enter - next")

for i, d in enumerate(DISPLAY_TYPES):
    print(f"  {i+1}: {d['name']}")
choice = input("\nEnter best option number: ")
best_type = DISPLAY_TYPES[int(choice)-1]
try: device.cleanup()
except: pass
device = make_device(best_type["cls"])
print(f"Selected: {best_type['name']}\n")

# STEP 2 - contrast
print("=== Step 2: Contrast ===")
for i, c in enumerate(CONTRAST_VARIANTS):
    show_test(device, c, 20, 9, f"Option {i+1} - contrast={c} ({i+1}/{len(CONTRAST_VARIANTS)})")
    input("Enter - next")

for i, c in enumerate(CONTRAST_VARIANTS):
    print(f"  {i+1}: contrast={c}")
choice = input("\nEnter best option number: ")
best_contrast = CONTRAST_VARIANTS[int(choice)-1]
print(f"Selected: contrast={best_contrast}\n")

# STEP 3 - font size
print("=== Step 3: Font size ===")
for i, f in enumerate(FONT_VARIANTS):
    show_test(device, best_contrast, f["font_large"], f["font_small"],
              f"Option {i+1} - font_large={f['font_large']} font_small={f['font_small']} ({i+1}/{len(FONT_VARIANTS)})")
    input("Enter - next")

for i, f in enumerate(FONT_VARIANTS):
    print(f"  {i+1}: font_large={f['font_large']} font_small={f['font_small']}")
choice = input("\nEnter best option number: ")
best_fonts = FONT_VARIANTS[int(choice)-1]
print(f"Selected: font_large={best_fonts['font_large']} font_small={best_fonts['font_small']}\n")

# Summary
print("=== New settings ===")
print(f"  DISPLAY_TYPE     = {best_type['type']}")
print(f"  DISPLAY_CONTRAST = {best_contrast}")
print(f"  FONT_LARGE       = {best_fonts['font_large']}")
print(f"  FONT_SMALL       = {best_fonts['font_small']}")

if old_config:
    print("")
    answer = input("Keep new settings? (Y/N): ").strip().upper()
    if answer != "Y":
        print("Keeping old settings.")
        best_type_val   = old_config.get("DISPLAY_TYPE", best_type["type"])
        best_contrast   = int(old_config.get("DISPLAY_CONTRAST", best_contrast))
        best_fonts_large = int(old_config.get("FONT_LARGE", best_fonts["font_large"]))
        best_fonts_small = int(old_config.get("FONT_SMALL", best_fonts["font_small"]))
        apply_config(best_type_val, best_contrast, best_fonts_large, best_fonts_small)
        save_config(best_type_val, best_contrast, best_fonts_large, best_fonts_small)
        device.cleanup()
        subprocess.run(["sudo", "systemctl", "start", "ddplayer-oled"], capture_output=True)
        print("Service started.")
        exit()

try:
    apply_config(best_type["type"], best_contrast, best_fonts["font_large"], best_fonts["font_small"])
    save_config(best_type["type"], best_contrast, best_fonts["font_large"], best_fonts["font_small"])
    print("Settings saved!")
except Exception as e:
    print(f"Error: {e}")

device.cleanup()
subprocess.run(["sudo", "systemctl", "start", "ddplayer-oled"], capture_output=True)
print("Service started.")