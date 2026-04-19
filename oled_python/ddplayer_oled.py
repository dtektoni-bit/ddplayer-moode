#!/usr/bin/env python3
import time, socket, subprocess, re, os, threading
import screensaver
from datetime import datetime
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106, ssd1306, ssd1309
from PIL import ImageFont, Image, ImageDraw
import mpd
import RPi.GPIO as GPIO

# ---- НАСТРОЙКИ ----
DISPLAY_TYPE     = "ssd1306"
DISPLAY_ADDRESS  = 0x3C
DISPLAY_CONTRAST = 150
I2C_PORT         = 1
FONT_SMALL       = 9
FONT_LARGE       = 20
FONT_PATH        = "/usr/share/fonts/opentype/unifont/unifont.otf"
POLL_INTERVAL    = 1.5   # секунд между опросом файлов
DRAW_INTERVAL    = 0.1   # секунд между перерисовкой
# -------------------

GPIO.setmode(GPIO.BCM)
for pin in [4, 17, 22, 27]:
    GPIO.setup(pin, GPIO.IN)

FILTERS = {(0,0):"SHARP",(0,1):"SLOW",(1,0):"SDSHARP",(1,1):"SDSLOW"}
INPUTS  = {(0,0):"NETWORK",(1,0):"COAX",(1,1):"OPTICAL"}

def get_filter(): return "DF:" + FILTERS.get((GPIO.input(22), GPIO.input(27)), "?")
def get_input():  return INPUTS.get((GPIO.input(4), GPIO.input(17)), "?")
def is_network(): return get_input() == "NETWORK"

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except: return "No network"

def get_nettype():
    try:
        out = subprocess.run(['ip','route'], capture_output=True, text=True).stdout
        return "ETH" if "eth" in out else ("WiFi" if "wlan" in out else "---")
    except: return "---"

def spotify_is_playing():
    try:
        with open("/proc/asound/card0/pcm0p/sub0/hw_params") as f:
            return f.read().strip() != "closed"
    except: return False

# --- Состояние (обновляется в фоне) ---
state = {
    "spotify_active": False,
    "mpd_state":      "stop",
    "mpd_status":     {},
    "mpd_song":       {},
    "spot_name":      "",
    "spot_artist":    "",
    "spot_album":     "",
    "spot_duration":  0.0,
    "spot_position":  0.0,   # позиция в момент последнего события
    "spot_base_time": 0.0,   # time.time() когда была записана позиция
    "spot_playing":   False,
    "ip":             "",
    "nettype":        "",
    "lock":           threading.Lock(),
}

# --- MPD ---
client = mpd.MPDClient()
def mpd_connect():
    try: client.connect("localhost", 6600); return True
    except: return False

def mpd_data():
    try: return client.status(), client.currentsong()
    except:
        try: client.disconnect()
        except: pass
        if mpd_connect():
            try: return client.status(), client.currentsong()
            except: pass
        return {'state':'stop'}, {}

mpd_connect()

# --- Фоновый поллер ---
def poller():
    last_spot_meta_mtime = 0
    last_spot_state_mtime = 0
    while True:
        try:
            # IP (меняется редко)
            ip = get_ip()
            nt = get_nettype()

            # currentsong.txt
            cs = {}
            try:
                with open("/var/local/www/currentsong.txt") as f:
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            cs[k.strip()] = v.strip()
            except: pass
            spotify_active = cs.get("file","") == "Spotify Active"

            # MPD
            mpd_status, mpd_song = mpd_data()

            # spotmeta.txt
            spot_name = spot_artist = spot_album = ""
            spot_duration = 0.0
            try:
                mt = os.path.getmtime("/var/local/www/spotmeta.txt")
                if mt != last_spot_meta_mtime:
                    last_spot_meta_mtime = mt
                    with open("/var/local/www/spotmeta.txt") as f:
                        parts = f.read().strip().split("~~~")
                    if len(parts) >= 4:
                        spot_name     = parts[0]
                        spot_artist   = parts[1]
                        spot_album    = parts[2]
                        spot_duration = int(parts[3]) / 1000.0
                        # новый трек — сброс позиции
                        with state["lock"]:
                            state["spot_position"]  = 0.0
                            state["spot_base_time"] = mt
                else:
                    with state["lock"]:
                        spot_name     = state["spot_name"]
                        spot_artist   = state["spot_artist"]
                        spot_album    = state["spot_album"]
                        spot_duration = state["spot_duration"]
            except: pass

            # spotstate.txt
            try:
                mt = os.path.getmtime("/var/local/www/spotstate.txt")
                if mt != last_spot_state_mtime:
                    last_spot_state_mtime = mt
                    ss = {}
                    with open("/var/local/www/spotstate.txt") as f:
                        for line in f:
                            if "=" in line:
                                k, v = line.strip().split("=", 1)
                                ss[k.strip()] = v.strip()
                    with state["lock"]:
                        if "position_ms" in ss:
                            state["spot_position"]  = int(ss["position_ms"]) / 1000.0
                            state["spot_base_time"] = mt
                        if "state" in ss:
                            state["spot_playing"] = (ss["state"] == "playing")
            except: pass
            # ALSA точнее для определения play/pause
            if spotify_active:
                with state["lock"]:
                    state["spot_playing"] = spotify_is_playing()

            # Обновляем состояние
            with state["lock"]:
                state["spotify_active"] = spotify_active
                state["mpd_state"]      = mpd_status.get("state", "stop")
                state["mpd_status"]     = mpd_status
                state["mpd_song"]       = mpd_song
                state["spot_name"]      = spot_name
                state["spot_artist"]    = spot_artist
                state["spot_album"]     = spot_album
                state["spot_duration"]  = spot_duration
                state["ip"]             = ip
                state["nettype"]        = nt

        except Exception as e:
            pass

        time.sleep(POLL_INTERVAL)

t = threading.Thread(target=poller, daemon=True)
t.start()

# --- Дисплей ---
serial = i2c(port=I2C_PORT, address=DISPLAY_ADDRESS)
DISPLAYS = {"sh1106": sh1106, "ssd1306": ssd1306, "ssd1309": ssd1309}
device = DISPLAYS.get(DISPLAY_TYPE, ssd1309)(serial, width=128, height=64)
device.contrast(DISPLAY_CONTRAST)

fS = ImageFont.truetype(FONT_PATH, FONT_SMALL)
fL = ImageFont.truetype(FONT_PATH, FONT_LARGE)

def tw(d, text, font):
    b = d.textbbox((0,0), text, font=font); return b[2]-b[0]

def cx(d, text, font):
    return (128 - tw(d, text, font)) // 2

def new_frame():
    img = Image.new("1", (128, 64), 0)
    return img, ImageDraw.Draw(img)

def draw_stop():
    img, d = new_frame()
    now = datetime.now()
    inp = get_input(); filt = get_filter()
    with state["lock"]:
        ip = state["ip"]; net = state["nettype"]
    f12st = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 12)
    f14st = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 14)
    d.text((0, 0), ip, font=f14st, fill=1)
    if net == "ETH":
        ex = 108
        ey = 0
        d.point((ex+3, ey), fill=1)
        for x in range(ex+2, ex+11): d.point((x, ey+1), fill=1)
        for x in range(ex+1, ex+11): d.point((x, ey+2), fill=1)
        for x in range(ex+1, ex+11): d.point((x, ey+4), fill=1)
        for x in range(ex+2, ex+11): d.point((x, ey+5), fill=1)
        d.point((ex+8, ey+6), fill=1)
    else:
        wx = 108
        wy = 0
        for i in range(4):
            ht = 2*i + 1
            xo = 3*i + 1
            for y in range(wy+7-(ht), wy+7):
                d.point((wx+xo, y), fill=1)
                d.point((wx+xo+1, y), fill=1)
    ts = now.strftime("%H:%M:%S")
    d.text((cx(d,ts,fL), 13), ts, font=fL, fill=1)
    ds = now.strftime("%d.%m.%Y")
    d.text((cx(d,ds,f14st), 35), ds, font=f14st, fill=1)
    inp_str = inp
    d.text((0, 50), filt, font=f14st, fill=1)
    d.text((128 - tw(d,inp_str,f14st), 50), inp_str, font=f14st, fill=1)
    device.display(img.convert(device.mode))

scroll_x = 0
scroll_pause = 0
last_activity = time.time()
SCREENSAVER_TIMEOUT = 180  # 10 minutes
PAUSE_TICKS = int(4.0 / DRAW_INTERVAL)  # 4 секунды паузы перед скроллингом

def draw_play(scroll_x):
    img, d = new_frame()
    with state["lock"]:
        status   = state["mpd_status"]
        song     = state["mpd_song"]
    filt = get_filter()
    st = status.get("state","stop")
    audio = status.get("audio","")
    if audio:
        p = audio.split(":")
        sr   = str(int(p[0])//1000) if p[0].isdigit() else p[0]
        bits = p[1] if len(p)>1 else "?"
        sr_str = f"{sr}/{bits}"
    else: sr_str = "--"
    f12 = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 12)
    d.text((0, 0), sr_str, font=f12, fill=1)
    d.text((128 - tw(d,filt,f12), 0), filt, font=f12, fill=1)
    st_str = "PLAY" if st=="play" else "PAUSE"
    fmt = song.get("file","").split(".")[-1].upper()[:4] if "file" in song else ""
    fSt = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 14)
    d.text((0, 15), f"{st_str} {fmt}", font=fSt, fill=1)
    elapsed  = float(status.get("elapsed", 0))
    duration = float(status.get("duration", 0))
    remaining = max(0, duration - elapsed)
    t_str = f"{int(remaining)//60}:{int(remaining)%60:02d}"
    d.text((128 - tw(d,t_str,fL), 11), t_str, font=fL, fill=1)
    artist = song.get("artist","")
    fAp = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 14)
    d.text((0, 32), artist[:18], font=fAp, fill=1)
    title = song.get("title", song.get("file","").split("/")[-1])
    album = song.get("album","")
    ta = f"{title}  /  {album}" if album else title
    fU2 = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 14)
    d.text((-scroll_x, 45), ta, font=fU2, fill=1)
    if duration > 0:
        bw = int(128 * elapsed / duration)
        d.rectangle([(0,61),(127,63)], outline=1)
        if bw > 1: d.rectangle([(1,62),(bw,62)], fill=1)
    device.display(img.convert(device.mode))
    return title

def draw_spotify(scroll_x):
    img, d = new_frame()
    with state["lock"]:
        name     = state["spot_name"]
        artist   = state["spot_artist"]
        album    = state["spot_album"]
        duration = state["spot_duration"]
        position = state["spot_position"]
        base_t   = state["spot_base_time"]
        playing  = state["spot_playing"]
    filt = get_filter()
    # Elapsed
    if playing:
        elapsed = min(position + (time.time() - base_t), duration)
    else:
        elapsed = position
    remaining = max(0, duration - elapsed)
    # Строка 1
    f12s = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 12)
    d.text((0, 0), "Spotify", font=f12s, fill=1)
    d.text((128 - tw(d,filt,f12s), 0), filt, font=f12s, fill=1)
    # Строка 2
    st_str = "PLAY" if playing else "PAUSE"
    fSt2 = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 14)
    d.text((0, 15), st_str, font=fSt2, fill=1)
    t_str = f"{int(remaining)//60}:{int(remaining)%60:02d}"
    d.text((128 - tw(d,t_str,fL), 11), t_str, font=fL, fill=1)
    # Строка 3: artist
    fA = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 14)
    d.text((0, 32), artist[:18], font=fA, fill=1)
    # Строка 4: title/album скроллинг
    ta = (f"{name} / {album}" if album else name) + "     "
    fU2 = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 14)
    d.text((-scroll_x, 45), ta, font=fU2, fill=1)
    # Прогресс
    if duration > 0:
        bw = int(128 * elapsed / duration)
        d.rectangle([(0,61),(127,63)], outline=1)
        if bw > 1: d.rectangle([(1,62),(bw,62)], fill=1)
    device.display(img.convert(device.mode))
    return name


def draw_radio(scroll_x):
    img, d = new_frame()
    with state["lock"]:
        status = state["mpd_status"]
        song   = state["mpd_song"]
    filt = get_filter()
    st = status.get("state","stop")
    audio = status.get("audio","")
    if audio:
        p = audio.split(":")
        sr = str(int(p[0])//1000) if p[0].isdigit() else p[0]
        bits = p[1] if len(p)>1 else "?"
        sr_str = f"{sr}/{bits}"
    else: sr_str = "--"
    bitrate = status.get("bitrate","")
    st_str = "PLAY" if st=="play" else "PAUSE"
    filt = get_filter()
    f12 = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 12)
    d.text((0, 0), sr_str, font=f12, fill=1)
    d.text((128 - tw(d,filt,f12), 0), filt, font=f12, fill=1)
    br_str = f"{st_str} RADIO {bitrate}kbps" if bitrate else f"{st_str} RADIO"
    fRad = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 14)
    d.text((0, 15), br_str, font=fRad, fill=1)
    station = song.get("name","")
    fM = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 16)
    d.text((1, 29), station[:18], font=fM, fill=1)
    d.text((0, 29), station[:18], font=fM, fill=1)
    title = song.get("title","")
    fT = ImageFont.truetype("/usr/share/fonts/opentype/unifont/unifont.otf", 15)
    d.text((-scroll_x, 48), title, font=fT, fill=1)
    device.display(img.convert(device.mode))
    return title

# --- Главный цикл ---
try:
    while True:
        # Screensaver check
        if time.time() - last_activity > SCREENSAVER_TIMEOUT:
            screensaver.run(device, state)
            last_activity = time.time()
            continue

        inp = get_input()
        network = (inp == "NETWORK")

        with state["lock"]:
            spotify = state["spotify_active"]
            mpd_st  = state["mpd_state"]
        if mpd_st not in ("stop", "pause") or spotify_is_playing():
            last_activity = time.time()

        if not network:
            # Вход не сетевой — всегда STOP
            draw_stop()
            scroll_x = 0; scroll_pause = 0
        elif spotify:
            title = draw_spotify(scroll_x)
            if scroll_pause < PAUSE_TICKS:
                scroll_pause += 1
            else:
                scroll_x += 2
                if scroll_x > max(0, len(title)*6 - 80):
                    scroll_x = 0; scroll_pause = 0
        elif mpd_st in ("play","pause"):
            with state["lock"]:
                song = state["mpd_song"]
            _file = song.get("file", "")
            is_radio = ("name" in song or _file.startswith("http")) and float(state["mpd_status"].get("duration", 0)) == 0
            if is_radio:
                title = draw_radio(scroll_x)
            else:
                title = draw_play(scroll_x)
            if scroll_pause < PAUSE_TICKS:
                scroll_pause += 1
            else:
                scroll_x += 2
                if scroll_x > max(0, len(title)*6 - 80):
                    scroll_x = 0; scroll_pause = 0
        else:
            draw_stop()
            scroll_x = 0; scroll_pause = 0

        time.sleep(DRAW_INTERVAL)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
    device.cleanup()
