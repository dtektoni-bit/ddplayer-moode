# DDPlayer OLED Display (Python)

OLED display driver for DDPlayer DAC on moOde audio player.

## Hardware
- Raspberry Pi 4
- SSD1309 / SH1106 / SSD1306 128x64 I2C OLED display
- DDPlayer DAC board

## Features
- STOP screen: time, date, IP, digital filter, input source
- PLAY screen: samplerate, format, artist, title/album scroll, progress bar
- Spotify screen: artist, title, album, progress bar
- Auto-switch to STOP when input is OPTICAL/COAX

## Install
```bash
cat > ~/ddplayer-moode/oled_python/README.md << 'EOF'
# DDPlayer OLED Display (Python)

OLED display driver for DDPlayer DAC on moOde audio player.

## Hardware
- Raspberry Pi 4
- SSD1309 / SH1106 / SSD1306 128x64 I2C OLED display
- DDPlayer DAC board

## Features
- STOP screen: time, date, IP, digital filter, input source
- PLAY screen: samplerate, format, artist, title/album scroll, progress bar
- Spotify screen: artist, title, album, progress bar
- Auto-switch to STOP when input is OPTICAL/COAX

## Install
```bash
wget https://raw.githubusercontent.com/dtektoni-bit/ddplayer-moode/main/oled_python/install.sh
sudo bash install.sh
```

## GPIO
| GPIO | Function |
|------|----------|
| 4, 17 | Input select (OPTICAL/COAX/NETWORK) |
| 22, 27 | Digital filter select |
