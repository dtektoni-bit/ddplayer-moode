#!/usr/bin/env python3
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106, ssd1306, ssd1309
from PIL import ImageFont, Image, ImageDraw

fBold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fReg  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

DISPLAY_TYPES = [
    {"name": "Вариант 1 — sh1106",  "type": "sh1106",  "cls": sh1106},
    {"name": "Вариант 2 — ssd1306", "type": "ssd1306", "cls": ssd1306},
    {"name": "Вариант 3 — ssd1309", "type": "ssd1309", "cls": ssd1309},
]

CONTRAST_VARIANTS = [10, 30, 50, 100, 150, 200, 255]

FONT_VARIANTS = [
    {"font_large": 20, "font_small": 9},
    {"font_large": 18, "font_small": 9},
    {"font_large": 16, "font_small": 8},
]

def make_device(cls):
    serial = i2c(port=1, address=0x3C)
    return cls(serial, width=128, height=64)

def show_test(device, contrast, font_large, font_small, label):
    device.contrast(contrast)
    fL = ImageFont.truetype(fBold, font_large)
    fS = ImageFont.truetype(fReg,  font_small)
    img = Image.new("1", (128, 64), 0)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0),(127,63)], outline=1)
    draw.text((2, 2),  "192.168.1.100  ETH",  font=fS, fill=1)
    draw.text((2, 13), "23:59:59",             font=fL, fill=1)
    draw.text((2, 13+font_large+2), "12.04.2025", font=fS, fill=1)
    draw.text((2, 54), "DF:SHARP   OPTICAL",  font=fS, fill=1)
    device.display(img.convert(device.mode))
    print(f"  {label}")

# ШАГ 1 — тип дисплея
print("=== Шаг 1: Тип дисплея ===")
device = None
for i, d in enumerate(DISPLAY_TYPES):
    if device:
        try: device.cleanup()
        except: pass
    device = make_device(d["cls"])
    show_test(device, 50, 20, 9, f"{d['name']} ({i+1}/{len(DISPLAY_TYPES)})")
    input("Enter — следующий вариант")

for i, d in enumerate(DISPLAY_TYPES):
    print(f"  {i+1}: {d['name']}")
choice = input("\nВведи номер лучшего варианта: ")
best_type = DISPLAY_TYPES[int(choice)-1]
try: device.cleanup()
except: pass
device = make_device(best_type["cls"])
print(f"Выбрано: {best_type['name']}\n")

# ШАГ 2 — контраст
print("=== Шаг 2: Контраст ===")
for i, c in enumerate(CONTRAST_VARIANTS):
    show_test(device, c, 20, 9, f"Вариант {i+1} — contrast={c} ({i+1}/{len(CONTRAST_VARIANTS)})")
    input("Enter — следующий вариант")

for i, c in enumerate(CONTRAST_VARIANTS):
    print(f"  {i+1}: contrast={c}")
choice = input("\nВведи номер лучшего варианта: ")
best_contrast = CONTRAST_VARIANTS[int(choice)-1]
print(f"Выбрано: contrast={best_contrast}\n")

# ШАГ 3 — размер шрифта
print("=== Шаг 3: Размер шрифта ===")
for i, f in enumerate(FONT_VARIANTS):
    show_test(device, best_contrast, f["font_large"], f["font_small"],
              f"Вариант {i+1} — font_large={f['font_large']} font_small={f['font_small']} ({i+1}/{len(FONT_VARIANTS)})")
    input("Enter — следующий вариант")

for i, f in enumerate(FONT_VARIANTS):
    print(f"  {i+1}: font_large={f['font_large']} font_small={f['font_small']}")
choice = input("\nВведи номер лучшего варианта: ")
best_fonts = FONT_VARIANTS[int(choice)-1]
print(f"Выбрано: font_large={best_fonts['font_large']} font_small={best_fonts['font_small']}\n")

# Записываем в ddplayer_oled.py
try:
    import re
    with open("ddplayer_oled.py", "r") as f:
        content = f.read()
    content = re.sub(r'DISPLAY_TYPE\s*=\s*"[^"]*"',  f'DISPLAY_TYPE     = "{best_type["type"]}"',       content)
    content = re.sub(r'DISPLAY_CONTRAST\s*=\s*\d+',   f'DISPLAY_CONTRAST = {best_contrast}',             content)
    content = re.sub(r'FONT_LARGE\s*=\s*\d+',         f'FONT_LARGE       = {best_fonts["font_large"]}',  content)
    content = re.sub(r'FONT_SMALL\s*=\s*\d+',         f'FONT_SMALL       = {best_fonts["font_small"]}',  content)
    with open("ddplayer_oled.py", "w") as f:
        f.write(content)
    print("Готово! Настройки сохранены в ddplayer_oled.py")
    print(f"  DISPLAY_TYPE     = {best_type['type']}")
    print(f"  DISPLAY_CONTRAST = {best_contrast}")
    print(f"  FONT_LARGE       = {best_fonts['font_large']}")
    print(f"  FONT_SMALL       = {best_fonts['font_small']}")
except:
    print("ddplayer_oled.py не найден — настройки не сохранены")

device.cleanup()
