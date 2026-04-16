#!/bin/bash
echo "=== DDPlayer OLED installer ==="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Installing dependencies..."
sudo apt install -y python3-pip python3-pil i2c-tools
pip3 install luma.oled python-mpd2 RPi.GPIO --break-system-packages

echo "Downloading font..."
wget -q -O /tmp/Monocraft.ttf "https://github.com/IdreesInc/Monocraft/releases/download/v3.0/Monocraft.ttf"
sudo cp /tmp/Monocraft.ttf /usr/share/fonts/truetype/
sudo fc-cache -f

echo "Copying scripts..."
cp "$SCRIPT_DIR/ddplayer_oled.py" /home/moode/
cp "$SCRIPT_DIR/setup_oled.py" /home/moode/
cp "$SCRIPT_DIR/adafruit_font.py" /home/moode/

echo "Setting permissions..."
chown moode:moode /home/moode/ddplayer_oled.py
chown moode:moode /home/moode/setup_oled.py
chown moode:moode /home/moode/adafruit_font.py

echo "Installing service..."
sudo cp "$SCRIPT_DIR/ddplayer-oled.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ddplayer-oled

echo "Patching spotevent.sh..."
SPOTEVENT="/var/local/www/commandw/spotevent.sh"
if ! grep -q "seeked" "$SPOTEVENT"; then
    sudo python3 -c "
content = open('$SPOTEVENT').read()
content = content.replace(
    'PLAYER_EVENTS=(\nsession_connected\nsession_disconnected\ntrack_changed\n)',
    'PLAYER_EVENTS=(\nsession_connected\nsession_disconnected\ntrack_changed\nseeked\nplaying\npaused\n)'
)
handlers = '''
if [[ \$PLAYER_EVENT == \"seeked\" ]]; then
    echo \"position_ms=\${POSITION_MS}\" > /var/local/www/spotstate.txt
fi
if [[ \$PLAYER_EVENT == \"playing\" ]]; then
    echo \"state=playing\" >> /var/local/www/spotstate.txt
fi
if [[ \$PLAYER_EVENT == \"paused\" ]]; then
    echo \"state=paused\" > /var/local/www/spotstate.txt
    echo \"position_ms=\${POSITION_MS}\" >> /var/local/www/spotstate.txt
fi
if [[ \$PLAYER_EVENT == \"track_changed\" ]]; then
    echo \"\" > /var/local/www/spotstate.txt
fi
'''
if 'seeked' not in content:
    content = content + handlers
open('$SPOTEVENT', 'w').write(content)
"
    echo "spotevent.sh patched."
else
    echo "spotevent.sh already patched, skipping."
fi

echo ""
echo "=== Installation complete ==="
echo "Starting display setup..."
python3 /home/moode/setup_oled.py

echo ""
echo "Starting service..."
sudo systemctl start ddplayer-oled
sudo systemctl status ddplayer-oled
