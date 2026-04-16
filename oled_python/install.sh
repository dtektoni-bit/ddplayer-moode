#!/bin/bash
echo "=== DDPlayer OLED installer ==="

# Зависимости
echo "Устанавливаем зависимости..."
sudo apt install -y python3-pip python3-pil i2c-tools
pip3 install luma.oled python-mpd2 RPi.GPIO --break-system-packages

# Шрифт Monocraft
echo "Скачиваем шрифт..."
wget -q -O /tmp/Monocraft.ttf "https://github.com/IdreesInc/Monocraft/releases/download/v3.0/Monocraft.ttf"
sudo cp /tmp/Monocraft.ttf /usr/share/fonts/truetype/
sudo fc-cache -f

# Копируем скрипты
echo "Копируем скрипты..."
cp "$(dirname "$0")/ddplayer_oled.py" /home/moode/
cp "$(dirname "$0")/setup_oled.py" /home/moode/

# Systemd сервис
echo "Устанавливаем сервис..."
sudo cp "$(dirname "$0")/ddplayer-oled.service" /etc/systemd/system/
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
