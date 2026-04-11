# DDPlayer DAC — Moode Audio

Драйвер и скрипт установки для кастомной платы DDPlayer DAC на Moode Audio.

## Железо

- Raspberry Pi 4
- Кастомная плата DDPlayer (AK4490 / PCM1794, тактирование AK4113)
- Pi работает как I2S Slave

## Требования

- Moode Audio (образ на базе PiOS Trixie/Bookworm)
- Подключение к интернету на Pi
- SSH доступ

## Установка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/dtektoni-bit/ddplayer-moode.git
cd ddplayer-moode
```

### 2. Запустить скрипт установки

```bash
chmod +x install.sh
sudo ./install.sh
```

Скрипт автоматически:
- Установит зависимости для сборки
- Установит kernel headers для текущего ядра
- Скомпилирует и установит kernel module (`.ko`)
- Скомпилирует и установит device tree overlay (`.dtbo`)

Занимает ~2-5 минут.

### 3. Настроить в Moode UI

Открыть `http://moode.local` в браузере:

**Шаг 1** — Configure → Audio → Audio Output
- Поле "or DT overlay" → ввести `ddplayer-dac`
- Нажать Save → перезагрузить Pi

**Шаг 2** — после перезагрузки: Configure → Audio → Audio Output → MPD
- Audio Output Device → выбрать `snd_rpi_ddplayer_dac`
- Нажать Save

## Обновление ядра

При обновлении образа Moode нужно повторно запустить `install.sh` — kernel module привязан к версии ядра.

## Проверка

```bash
# Звуковая карта появилась
aplay -l

# Модуль загружен
lsmod | grep ddplayer

# Параметры воспроизведения
cat /proc/asound/card0/pcm0p/sub0/hw_params
```

## GPIO

| GPIO (BCM) | Функция |
|---|---|
| 6 | Выбор генератора (LOW=44.1k, HIGH=48k) |
| 5 | OCKS1 на AK4113 |
| 13 | OCKS0 на AK4113 |
| 16 | Mute (active high) |
| 26 | Reset (active high) |
