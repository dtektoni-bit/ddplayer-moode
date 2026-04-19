import random
import time
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 128, 64
CELL = 4
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL
SPEED = 0.15

def spotify_is_playing():
    try:
        with open("/proc/asound/card0/pcm0p/sub0/hw_params") as f:
            return f.read().strip() != "closed"
    except:
        return False

def run(device, state):
    snake = [(COLS//2, ROWS//2)]
    direction = (1, 0)
    food = _new_food(snake)

    while True:
        with state["lock"]:
            spotify = state["spotify_active"]
            mpd_st  = state["mpd_state"]
        if (spotify and spotify_is_playing()) or mpd_st == "play":
            return

        direction = _autopilot(snake, direction, food)
        head = ((snake[0][0] + direction[0]) % COLS,
                (snake[0][1] + direction[1]) % ROWS)

        if head in snake:
            snake = [(COLS//2, ROWS//2)]
            direction = (1, 0)
            food = _new_food(snake)
            time.sleep(0.5)
            continue

        snake.insert(0, head)

        if head == food:
            food = _new_food(snake)
        else:
            snake.pop()

        img = Image.new("1", (WIDTH, HEIGHT), 0)
        d = ImageDraw.Draw(img)

        fx, fy = food
        d.rectangle([fx*CELL+1, fy*CELL+1, fx*CELL+CELL-2, fy*CELL+CELL-2], fill=1)

        for i, (x, y) in enumerate(snake):
            if i == 0:
                d.rectangle([x*CELL, y*CELL, x*CELL+CELL-1, y*CELL+CELL-1], fill=1)
            else:
                d.rectangle([x*CELL+1, y*CELL+1, x*CELL+CELL-2, y*CELL+CELL-2], fill=1)

        device.display(img.convert(device.mode))
        time.sleep(SPEED)

def _new_food(snake):
    while True:
        f = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if f not in snake:
            return f

def _autopilot(snake, direction, food):
    head = snake[0]
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    opposite = (-direction[0], -direction[1])

    def dist(d):
        nx = (head[0]+d[0]) % COLS
        ny = (head[1]+d[1]) % ROWS
        if (nx,ny) in snake:
            return 9999
        return abs(nx - food[0]) + abs(ny - food[1])

    candidates = [d for d in dirs if d != opposite]
    candidates.sort(key=dist)
    return candidates[0]