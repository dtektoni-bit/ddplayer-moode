# DDPlayer DAC — Moode Audio

Driver and install script for the custom DDPlayer DAC board on Moode Audio.

## Hardware

- Raspberry Pi 4
- Custom DDPlayer board (AK4490 / PCM1794, AK4113 clock)
- Pi runs as I2S Slave

## Requirements

- Moode Audio (PiOS Trixie/Bookworm based image)
- Internet connection on Pi
- SSH access

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/dtektoni-bit/ddplayer-moode.git
cd ddplayer-moode
```

### 2. Run the install script

```bash
chmod +x install.sh
sudo ./install.sh
```

The script will automatically:
- Install build dependencies
- Install kernel headers for the running kernel
- Compile and install the kernel module (`.ko`)
- Compile and install the device tree overlay (`.dtbo`)

Takes about 2–5 minutes.

### 3. Configure in Moode UI

Open `http://moode.local` in a browser:

**Step 1** — Configure → Audio → Audio Output
- "or DT overlay" field → enter `ddplayer-dac`
- Click Save → reboot Pi

**Step 2** — after reboot: Configure → Audio → Audio Output → MPD
- Audio Output Device → select `snd_rpi_ddplayer_dac`
- Click Save

## Kernel updates

When updating the Moode image, re-run `install.sh` — the kernel module is tied to the kernel version.

## Verification

```bash
# Sound card is visible
aplay -l

# Module is loaded
lsmod | grep ddplayer

# Playback parameters
cat /proc/asound/card0/pcm0p/sub0/hw_params
```

## GPIO

| GPIO (BCM) | Function |
|---|---|
| 6 | Clock select (LOW = 44.1k, HIGH = 48k) |
| 5 | OCKS1 on AK4113 |
| 13 | OCKS0 on AK4113 |
| 16 | Mute (active high) |
| 26 | Reset (active high) |
