#!/bin/bash
echo "=== DDPlayer OLED installer ==="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Устанавливаем зависимости..."
sudo apt install -y python3-pip python3-pil i2c-tools
pip3 install luma.oled python-mpd2 RPi.GPIO --break-system-packages

echo "Скачиваем шрифт..."
wget -q -O /tmp/Monocraft.ttf "https://github.com/IdreesInc/Monocraft/releases/download/v3.0/Monocraft.ttf"
sudo cp /tmp/Monocraft.ttf /usr/share/fonts/truetype/
sudo fc-cache -f

echo "Копируем скрипты..."
cp "$SCRIPT_DIR/ddplayer_oled.py" /home/moode/
cp "$SCRIPT_DIR/setup_oled.py" /home/moode/
cp "$SCRIPT_DIR/adafruit_font.py" /home/moode/

echo "Устанавливаем права..."
chown moode:moode /home/moode/ddplayer_oled.py
chown moode:moode /home/moode/setup_oled.py
chown moode:moode /home/moode/adafruit_font.py

echo "Устанавливаем сервис..."
sudo cp "$SCRIPT_DIR/ddplayer-oled.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ddplayer-oled

echo ""
echo "=== Установка завершена ==="
echo "Запускаем настройку дисплея..."
python3 /home/moode/setup_oled.py

echo ""
echo "Запускаем сервис..."
sudo systemctl start ddplayer-oled
sudo systemctl status ddplayer-oled
