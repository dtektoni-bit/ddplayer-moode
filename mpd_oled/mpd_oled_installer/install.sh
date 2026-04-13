#!/bin/bash

set -e

REPO_URL="https://github.com/dtektoni-bit/ddplayer-moode"
SRC_DIR="/tmp/ddplayer_moode_src"
OLED_DIR="$SRC_DIR/mpd_oled"
BINARY="/usr/local/bin/mpd_oled"
SERVICE="/etc/systemd/system/mpd_oled.service"

echo "=== DDPlayer moOde OLED Display installer ==="
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash install.sh"
    exit 1
fi

# Install dependencies
echo "[1/5] Installing dependencies..."
apt-get update -qq
apt-get install -y \
    git \
    build-essential \
    libi2c-dev \
    i2c-tools \
    libmpdclient-dev \
    libcurl4-openssl-dev \
    libjsoncpp-dev \
    libfftw3-dev \
    libasound2-dev

# Clone repo
echo "[2/5] Cloning repository..."
rm -rf "$SRC_DIR"
git clone --depth=1 "$REPO_URL" "$SRC_DIR"

# Build
echo "[3/5] Building mpd_oled..."
cd "$OLED_DIR"
PLAYER=MOODE make

# Install binary
echo "[4/5] Installing binary..."
cp mpd_oled "$BINARY"
chmod +x "$BINARY"

# Install service
echo "[5/5] Installing systemd service..."
cp mpd_oled.service "$SERVICE"
systemctl daemon-reload
systemctl enable mpd_oled
systemctl restart mpd_oled

echo ""
echo "=== Installation complete ==="
echo "Service status:"
systemctl status mpd_oled --no-pager
