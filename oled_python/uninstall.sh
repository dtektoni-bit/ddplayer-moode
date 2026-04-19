#!/bin/bash
echo "=== DDPlayer OLED uninstall ==="

sudo systemctl stop ddplayer-oled
sudo systemctl disable ddplayer-oled
sudo rm -f /etc/systemd/system/ddplayer-oled.service
sudo systemctl daemon-reload

rm -f /home/moode/ddplayer_oled.py
rm -f /home/moode/setup_oled.py
rm -f /home/moode/adafruit_font.py
rm -f /home/moode/make_font.py
rm -f /home/moode/screensaver.py
rm -f /home/moode/ddplayer_oled.conf

sudo rm -f /usr/share/fonts/truetype/Monocraft.ttf
sudo fc-cache -f

echo "=== Uninstalled ==="
