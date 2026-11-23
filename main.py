#!/usr/bin/env python3
"""THE ATLAS LEDGER -- one globe, one day, every story pinned.

Draws the front page for Monday 23 November 2026 as a single 1024x1024
PNG, written to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png on
the grader, or ./out/entry.png when run by hand without the variable).

Pure Python 3 standard library, no network. The globe artwork in
globe.ppm is an original illustration drawn for this daily series; the
program places it, pins the day's eight stories on it, and sets the
whole page in a 5x7 bitmap font drawn from scratch. The run is
deterministic: the same bytes come out every time.

Verification layer: every headline on the page is a real event of
20-23 November 2026, each with its outlet and date recorded in
SOURCES.md. The timeline strip dates each turning point in UTC.
"""
import hashlib
import math
import os
import struct
import zlib

W = H = 1024
PAPER = (242, 231, 206)
INK = (28, 52, 66)
FAINT = (176, 168, 146)
RED = (178, 52, 38)
WHITE = (250, 248, 240)
SEA = (35, 80, 100)
SEA_LINE = (96, 145, 155)

# ------------------------------------------------------------------ font
# 5x7 bitmaps, authored for this entry. Each glyph is 7 rows of 5 bits.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}


def text_width(text, s):
    return (len(text) * 6 - 1) * s if text else 0


def draw_text(buf, x, y, s, color, text, bold=False):
    """Draw text at scale s (glyph 5x7, 1s gap). Bold = double strike."""
    for dx in ((0, 1) if bold else (0,)):
        cx = x + dx
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == "1":
                        rect(buf, cx + col_i * s, y + row_i * s, s, s, color)
            cx += 6 * s
    return text_width(text, s)


def wrap(text, max_w, s):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if text_width(trial, s) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas
def px(buf, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(buf, x, y, w, h, c):
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + len(row)] = row


def hline(buf, x0, x1, y, c, thick=1):
    for t in range(thick):
        rect(buf, x0, y + t, x1 - x0, 1, c)


def disc(buf, cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(r * r - dy * dy, 0)))
        rect(buf, cx - dx, cy + dy, 2 * dx + 1, 1, c)


def ring(buf, cx, cy, r, c, thick=2):
    for rr in range(r - thick + 1, r + 1):
        for a in range(360):
            t = math.radians(a)
            px(buf, cx + int(round(rr * math.cos(t))),
               cy + int(round(rr * math.sin(t))), c)


# ------------------------------------------------------------------ ppm
def load_ppm(path):
    with open(path, "rb") as f:
        data = f.read()
    pos = 0

    def token():
        nonlocal pos
        while pos < len(data) and chr(data[pos]) in " \t\r\n":
            pos += 1
        if pos < len(data) and data[pos:pos + 1] == b"#":
            while pos < len(data) and data[pos:pos + 1] != b"\n":
                pos += 1
            return token()
        start = pos
        while pos < len(data) and chr(data[pos]) not in " \t\r\n":
            pos += 1
        return data[start:pos]

    magic = token()
    if magic != b"P6":
        raise ValueError("not a P6 ppm")
    w = int(token())
    h = int(token())
    maxval = int(token())
    if maxval != 255:
        raise ValueError("ppm maxval is not 255")
    pos += 1  # single whitespace after maxval
    need = w * h * 3
    return w, h, data[pos:pos + need]


def blit(buf, ppm_w, ppm_h, pixels, dx, dy):
    for y in range(ppm_h):
        src = y * ppm_w * 3
        dst = ((dy + y) * W + dx) * 3
        buf[dst:dst + ppm_w * 3] = pixels[src:src + ppm_w * 3]


# ------------------------------------------------------------------ png
def _chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload +
            struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def png_bytes(buf):
    raw = bytearray()
    prev = bytes(W * 3)
    for y in range(H):
        row = bytes(buf[y * W * 3:(y + 1) * W * 3])
        sub = bytes((row[i] - (row[i - 3] if i >= 3 else 0)) & 0xFF
                    for i in range(len(row)))
        up = bytes((row[i] - prev[i]) & 0xFF for i in range(len(row)))
        best, best_score = 0, None
        for ftype, filt in ((0, row), (1, sub), (2, up)):
            score = sum(b if b < 128 else 256 - b for b in filt)
            if best_score is None or score < best_score:
                best, best_score = ftype, score
        raw.append(best)
        raw.extend((row, sub, up)[best])
        prev = row
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + _chunk(b"IEND", b""))

# --------------------------------------------------------------- content
# The eight stories of Monday 23 November 2026, each pinned on the
# globe. (headline, one-line summary) -- pin number is the story's
# position. Every fact is sourced in SOURCES.md with outlet + date.
STORIES = [
    ("COP31 COLLAPSES",
     "COP31 ENDS WITH NO DEAL."),
    ("NATO MEETS ON POLAND",
     "3 MISSILES WERE RUSSIAN."),
    ("HORMUZ TANKERS HIT MINES",
     "2 MORE TANKERS CATCH FIRE."),
    ("RUSSIAN SHIP SUNK IN LIBYA",
     "MERKURY HIT AT BENGHAZI."),
    ("HOUTHIS HIT SAUDI REFINERY",
     "RABIGH HIT; SAUDIS SILENT."),
    ("MARKETS IN CORRECTION",
     "AI SELL-OFF SINKS STOCKS."),
    ("BEPICOLOMBO AT MERCURY",
     "8-YEAR TRIP ENDS IN ORBIT."),
    ("KILLER ROBOTS PACT",
     "128 STATES AGREE RULES."),
]
# Pin spots as fractions of the globe artwork: Antalya, Poland,
# Hormuz, Benghazi, Rabigh, New York, Darmstadt (ESA), Geneva.
PINS = [(0.785, 0.360), (0.690, 0.295), (0.895, 0.400), (0.735, 0.435),
        (0.845, 0.450), (0.375, 0.355), (0.600, 0.250), (0.640, 0.365)]

# Four more stories from the same day, in brief.
BRIEF = [
    "DYMER FLAT HIT: 2 DEAD, 11 MISSING.",
    "DEMOCRATS WIN CONTROL OF CONGRESS.",
    "MARQUEZ TAKES 8TH MOTOGP TITLE.",
    "ALCARAZ WINS FIRST ATP FINALS TITLE.",
]

# How the day arrived, in UTC.
TIMELINE = [
    "FRI 20 - MISSILES FALL IN POLAND",
    "SAT 21 - BEPICOLOMBO AT MERCURY",
    "SUN 22 - COP31 COLLAPSES",
    "MON 23 - NATO MEETS IN BRUSSELS",
]

GLOBE_X, GLOBE_Y, GLOBE_S = 24, 138, 600
RAIL_X, RAIL_W = 648, 352


def draw_pin(buf, cx, cy, n):
    disc(buf, cx, cy, 13, RED)
    ring(buf, cx, cy, 13, INK, thick=2)
    label = str(n)
    draw_text(buf, cx - text_width(label, 2) // 2, cy - 7, 2, WHITE,
              label, bold=True)


def draw_page():
    buf = bytearray(bytes(PAPER) * (W * H))

    # Masthead.
    title = "THE ATLAS LEDGER"
    draw_text(buf, (W - text_width(title, 6)) // 2, 30, 6, INK, title,
              bold=True)
    hline(buf, 24, 1000, 86, INK, thick=2)
    hline(buf, 24, 1000, 92, INK, thick=2)
    dateline = "MONDAY, 23 NOVEMBER 2026 - THE WORLD IN ONE PAGE"
    draw_text(buf, (W - text_width(dateline, 2)) // 2, 104, 2, INK, dateline)

    # Globe: the original illustration, or a drawn disc if it is missing.
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        pw, ph, pixels = load_ppm(os.path.join(here, "globe.ppm"))
        blit(buf, pw, ph, pixels, GLOBE_X, GLOBE_Y)
    except (OSError, ValueError):
        cx, cy, r = GLOBE_X + GLOBE_S // 2, GLOBE_Y + GLOBE_S // 2, 276
        disc(buf, cx, cy, r, SEA)
        for frac in (0.25, 0.5, 0.75):
            yy = GLOBE_Y + int(GLOBE_S * frac)
            half = int(math.sqrt(max(r * r - (yy - cy) ** 2, 0)))
            hline(buf, cx - half, cx + half, yy, SEA_LINE, thick=2)
        for frac in (0.25, 0.75):
            xx = GLOBE_X + int(GLOBE_S * frac)
            rect(buf, xx, cy - r, 2, 2 * r, SEA_LINE)

    # Numbered pins, one per story.
    for i, (fx, fy) in enumerate(PINS, start=1):
        draw_pin(buf, GLOBE_X + int(fx * GLOBE_S),
                 GLOBE_Y + int(fy * GLOBE_S), i)

    # Story rail, right of the globe: eight stories, 75 px each.
    slot = (738 - 138) // len(STORIES)
    for i, (headline, summary) in enumerate(STORIES, start=1):
        top = 138 + (i - 1) * slot + 6
        draw_pin(buf, RAIL_X + 14, top + 22, i)
        tx = RAIL_X + 38
        tw = RAIL_X + RAIL_W - tx
        y = top
        for line in wrap(headline, tw, 3):
            draw_text(buf, tx, y, 3, INK, line, bold=True)
            y += 22
        y = top + 46
        for line in wrap(summary, tw, 2):
            draw_text(buf, tx, y, 2, INK, line)
            y += 13
        if i < len(STORIES):
            hline(buf, RAIL_X, RAIL_X + RAIL_W, 138 + i * slot - 4, FAINT)

    # Footline under the globe.
    line = "ONE GLOBE. ONE DAY."
    draw_text(buf, GLOBE_X + (GLOBE_S - text_width(line, 3)) // 2, 756, 3,
              INK, line, bold=True)
    line = "ALL EIGHT STORIES: 23 NOVEMBER 2026."
    draw_text(buf, GLOBE_X + (GLOBE_S - text_width(line, 2)) // 2, 790, 2,
              INK, line)

    # Bottom band: in brief (left) and the UTC timeline (right).
    rect(buf, 24, 824, 560, 2, INK)
    rect(buf, 24, 948, 560, 2, INK)
    rect(buf, 24, 824, 2, 126, INK)
    rect(buf, 582, 824, 2, 126, INK)
    rect(buf, 600, 824, 400, 2, INK)
    rect(buf, 600, 948, 400, 2, INK)
    rect(buf, 600, 824, 2, 126, INK)
    rect(buf, 998, 824, 2, 126, INK)
    draw_text(buf, 36, 836, 2, INK, "IN BRIEF - MORE FROM 23 NOVEMBER",
              bold=True)
    for j, item in enumerate(BRIEF):
        draw_text(buf, 36, 860 + j * 22, 2, INK, item)
    draw_text(buf, 612, 836, 2, INK, "TIMELINE - UTC", bold=True)
    for j, item in enumerate(TIMELINE):
        draw_text(buf, 612, 860 + j * 22, 2, INK, item)

    # Credit line.
    hline(buf, 24, 1000, 968, INK, thick=2)
    credit = "THE ATLAS LEDGER - MONDAY 23 NOVEMBER 2026 - SOURCES IN SOURCES.MD"
    draw_text(buf, (W - text_width(credit, 2)) // 2, 978, 2, INK, credit)
    return buf


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or (
        "/output" if os.path.isdir("/output") else "out")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw_page())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s %d bytes sha256=%s"
          % (path, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
