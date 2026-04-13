# DDPlayer OLED Display for moOde Audio

OLED status display for DDPlayer DAC running moOde Audio on Raspberry Pi 4.

Based on [dsivov/mpd_oled](https://github.com/dsivov/mpd_oled) (fork of [antiprism/mpd_oled](https://github.com/antiprism/mpd_oled)).

## Hardware

- Raspberry Pi 4
- DDPlayer DAC board (AK4490/PCM1794, AK4113 clock)
- SH1106 or SSD1309 128x64 I2C OLED display
- I2C address: `0x3c`, bus: `/dev/i2c-1`

## What it displays

**STOP screen:**
- IP address + network indicator
- Time (centered)
- Date
- Digital filter status (GPIO 22/27): `DF:SHARP` / `DF:SLOW` / `DF:SDSHARP` / `DF:SDSLOW`
- Input source (GPIO 4/17): `OPTICAL` / `COAX` / `NETWORK READY`

**PLAY screen:**
- Samplerate / bit depth (e.g. `44/16`)
- Digital filter status
- PLAY / PAUSE
- Track type (flac, mp3...)
- Remaining time (countdown)
- Artist
- Title + Album (scrolling)
- Progress bar

## Requirements

- moOde Audio on Raspberry Pi 4 (64-bit, Debian Bookworm)
- DDPlayer DAC driver installed
- I2C enabled in `/boot/firmware/config.txt`: `dtparam=i2c_arm=on`

## Installation

```bash
wget https://raw.githubusercontent.com/dtektoni-bit/ddplayer-moode/main/mpd_oled/mpd_oled_installer/install.sh
sudo bash install.sh
```

The script will:
1. Install required packages
2. Clone and compile the source code natively on your Pi
3. Install the binary to `/usr/local/bin/mpd_oled`
4. Enable and start the systemd service

## Display type

Default display type is `-o 6` (SH1106 I2C 128x64). To change, edit the service file:

```bash
sudo nano /etc/systemd/system/mpd_oled.service
sudo systemctl daemon-reload
sudo systemctl restart mpd_oled
```

Available types:
- `-o 3` — Adafruit I2C 128x64 (SSD1306/SSD1309)
- `-o 4` — Seeed I2C 128x64
- `-o 6` — SH1106 I2C 128x64

## Service management

```bash
sudo systemctl status mpd_oled
sudo systemctl restart mpd_oled
sudo systemctl stop mpd_oled
```

## I2C bus speed (optional, reduces flicker)

Add to `/boot/firmware/config.txt`:
```
dtparam=i2c_arm_baudrate=400000
```
