import re

with open('/tmp/glcdfont.c') as f:
    content = f.read()

bytes_list = re.findall(r'0x([0-9a-fA-F]{2})', content)
font_data = [int(b, 16) for b in bytes_list]

out = "# Adafruit GFX classic 5x7 bitmap font\n"
out += "# Converted from glcdfont.c\n\n"
out += "FONT_DATA = [\n"
for b in font_data:
    out += "    " + str(b) + ",\n"
out += "]\n\n"

out += '''def draw_char(draw, x, y, char, scale=1):
    idx = ord(char)
    if idx * 5 >= len(FONT_DATA):
        return 6 * scale
    base = idx * 5
    for col in range(5):
        col_data = FONT_DATA[base + col]
        for row in range(7):
            if col_data & (1 << row):
                for sy in range(scale):
                    for sx in range(scale):
                        draw.point((x + col*scale + sx, y + row*scale + sy), fill=1)
    return 6 * scale

def draw_text(draw, x, y, text, scale=1):
    cx = x
    for char in text:
        cx += draw_char(draw, cx, y, char, scale)
    return cx - x

def text_width(text, scale=1):
    return len(text) * 6 * scale

def text_height(scale=1):
    return 7 * scale
'''

with open('/home/moode/adafruit_font.py', 'w') as f:
    f.write(out)
print("Done!")