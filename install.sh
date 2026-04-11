#!/bin/bash
# DDPlayer DAC — install script for Moode Audio
# Run from the root of the ddplayer-moode repository

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DRIVER_DIR="$SCRIPT_DIR/driver"
KERNEL_VER=$(uname -r)

echo "=== DDPlayer DAC installer for Moode ==="
echo "Kernel: $KERNEL_VER"
echo ""

# ── 1. Dependencies ──────────────────────────────────────────────────────────
echo "[1/5] Installing build dependencies..."
sudo apt-get install -y git gcc make flex bison libssl-dev bc

# ── 2. Kernel headers ────────────────────────────────────────────────────────
echo "[2/5] Checking kernel headers..."

HEADERS_DIR="/lib/modules/$KERNEL_VER/build"

if [ ! -d "$HEADERS_DIR" ]; then
    echo "Headers not found, installing..."
    PKG_NAME="linux-headers-$KERNEL_VER"
    COMMON_PKG=$(echo "$PKG_NAME" | sed 's/+rpt-rpi-[^ ]*/+rpt-common-rpi/')

    sudo apt-get install -y "$PKG_NAME" "$COMMON_PKG" || {
        echo "ERROR: Could not install kernel headers for $KERNEL_VER"
        echo "Try manually: sudo apt-cache search linux-headers | grep rpi"
        exit 1
    }
else
    echo "Headers already installed at $HEADERS_DIR"
fi

# ── 3. Compile driver ────────────────────────────────────────────────────────
echo "[3/5] Compiling kernel module..."
cd "$DRIVER_DIR"
make -C "$HEADERS_DIR" M="$DRIVER_DIR" modules

sudo mkdir -p "/lib/modules/$KERNEL_VER/kernel/sound/soc/bcm/"
sudo cp snd-soc-ddplayer-dac.ko "/lib/modules/$KERNEL_VER/kernel/sound/soc/bcm/"
sudo depmod -a
echo "Module installed."

# ── 4. Compile and install device tree overlay ───────────────────────────────
echo "[4/5] Compiling device tree overlay..."
dtc -@ -I dts -O dtb -o ddplayer-dac.dtbo ddplayer-dac.dts
sudo cp ddplayer-dac.dtbo /boot/overlays/
echo "Overlay installed to /boot/overlays/"

# ── 5. Done ──────────────────────────────────────────────────────────────────
echo ""
echo "[5/5] Done!"
echo ""
echo "=== Next steps in Moode UI ==="
echo "1. Configure → Audio → Audio Output"
echo "   → DT overlay field: ddplayer-dac"
echo "   → Click Save and reboot"
echo ""
echo "2. After reboot, select audio device:"
echo "   Configure → Audio → Audio Output → MPD"
echo "   → Audio Output Device: snd_rpi_ddplayer_dac"
echo ""
