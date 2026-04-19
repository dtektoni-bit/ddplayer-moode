# DDPlayer OLED Display

Python-based OLED display driver for DDPlayer DAC running on moOde audio player.
Replaces the original C++ mpd_oled which is incompatible with 64-bit aarch64 kernel (Debian Trixie).

## Hardware

- Raspberry Pi 4
- 128x64 I2C OLED display (SSD1309 / SH1106 / SSD1306)
- DDPlayer DAC board

## Features

- **STOP screen** — time, date, IP address, digital filter, input source
- **PLAY screen** — samplerate, format, artist, title/album scrolling, progress bar, remaining time
- **RADIO screen** — station name, current track, bitrate
- **Spotify screen** — artist, title, album, progress bar, play/pause state, remaining time
- Auto-switch to STOP screen when input is OPTICAL or COAX
- Screensaver — snake game after 3 minutes of inactivity
- Interactive display setup: type, contrast, font size

## Install

```bash
git clone https://github.com/dtektoni-bit/ddplayer-moode.git
sudo bash ~/ddplayer-moode/oled_python/install.sh
```

## Reconfigure display

```bash
python3 /home/moode/setup_oled.py
```

## Uninstall

```bash
sudo bash ~/ddplayer-moode/oled_python/uninstall.sh
```

## GPIO

| GPIO (BCM) | Pi Pin | Function |
|------------|--------|----------|
| 4 | 7 | Input select bit 0 |
| 17 | 11 | Input select bit 1 |
| 22 | 15 | Digital filter bit 0 |
| 27 | 13 | Digital filter bit 1 |

## Dependencies

- luma.oled
- python-mpd2
- RPi.GPIO
- Pillow
- Monocraft font (downloaded during install)
- Unifont (apt package, installed automatically)

## Files

| File | Purpose |
|------|---------|
| ddplayer_oled.py | Main display script |
| screensaver.py | Snake screensaver |
| setup_oled.py | Interactive configuration |
| install.sh | Installation script |
| uninstall.sh | Uninstallation script |
| adafruit_font.py | Adafruit 5x7 bitmap font |
| ddplayer-oled.service | systemd service |
| make_font.py | Generates adafruit_font.py from glcdfont.c (run once) |
