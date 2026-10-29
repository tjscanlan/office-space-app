# Flair Meter v2 - MonaOS 4.0 app, no `badgeware` import.
# C (SELECT, "Enter") is the only flair button: each press shades in the next
# dot and the banner flashes NOT ENOUGH FLAIR. When the 15th dot is shaded the
# banner switches to IS THIS ENOUGH FLAIR. Hold UP+DOWN for 1.5s to reset.
# HOME exits (handled by the OS).
import json
import os

badge.mode(HIRES | VSYNC)          # 320x240
screen.antialias = image.X2

BTN_ENTER = BUTTON_SELECT          # C

STATE_DIR = "/state"
STATE_PATH = "/state/flair_meter.json"
TARGET = 15
RESET_HOLD_MS = 1500

COLS, ROWS = 5, 3                  # 15 dots
X0, Y0, DX, DY, R = 50, 66, 55, 40, 16

BG = color.rgb(20, 24, 40)
TEXT = color.rgb(235, 235, 235)
DIM = color.rgb(60, 66, 90)
WARN = color.rgb(255, 120, 90)
OK = color.rgb(120, 230, 140)
PINS = (
    color.rgb(255, 80, 80),
    color.rgb(255, 200, 60),
    color.rgb(90, 200, 255),
    color.rgb(170, 120, 255),
    color.rgb(120, 230, 140),
)

BIG = font.ziplock
SMALL = font.nope

count = 0
hold_ms = 0
lights_on = False


def load():
    global count
    try:
        with open(STATE_PATH) as f:
            count = max(0, min(TARGET, int(json.load(f).get("count", 0))))
    except Exception:
        count = 0


def save():
    try:
        try:
            os.mkdir(STATE_DIR)
        except OSError:
            pass
        with open(STATE_PATH, "w") as f:
            json.dump({"count": count}, f)
    except Exception:
        pass


def set_lights(on):
    global lights_on
    if on != lights_on:
        lights_on = on
        badge.caselights(1 if on else 0)


def handle_input():
    global count, hold_ms
    changed = False
    if badge.pressed(BTN_ENTER) and count < TARGET:
        count += 1
        changed = True

    if badge.held(BUTTON_UP) and badge.held(BUTTON_DOWN):
        hold_ms += badge.ticks_delta
        if hold_ms >= RESET_HOLD_MS:
            count, hold_ms = 0, 0
            changed = True
    else:
        hold_ms = 0

    if changed:
        save()


def draw_banner():
    done = count >= TARGET
    msg = "IS THIS ENOUGH FLAIR" if done else "NOT ENOUGH FLAIR"
    accent = OK if done else WARN
    on = (badge.ticks // 250) % 2 == 0
    set_lights(on)

    screen.pen = accent if on else BG
    screen.rectangle(0, 180, screen.width, 48)

    screen.font = BIG
    w, _ = screen.measure_text(msg)
    x = screen.width - ((badge.ticks // 5) % (screen.width + w))
    screen.pen = BG if on else accent
    screen.text(msg, x, 192)


def draw():
    screen.pen = BG
    screen.clear()

    screen.font = BIG
    screen.pen = OK if count >= TARGET else TEXT
    screen.text("FLAIR %d/%d" % (count, TARGET), 8, 8)

    for i in range(TARGET):
        x = X0 + (i % COLS) * DX
        y = Y0 + (i // COLS) * DY
        if i < count:
            screen.pen = PINS[i % len(PINS)]
            screen.shape(shape.circle(x, y, R))
        else:
            screen.pen = DIM
            screen.shape(shape.circle(x, y, R).stroke(2))

    if count > 0:
        draw_banner()
    else:
        set_lights(False)
        screen.font = SMALL
        screen.pen = TEXT
        screen.text("Press C", 8, 214)


def update():
    handle_input()
    draw()


load()
run(update)
