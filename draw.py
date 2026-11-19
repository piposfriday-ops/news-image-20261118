#!/usr/bin/env python3
"""Draw the news-image-20261118 entry: a one-day newspaper front page for
Wednesday 18 November 2026, drawn entirely with Pillow (original artwork:
flat pictograms, no photographs, no copied art).

Stories (all reported on 18 Nov 2026, sources: AFP / AP / Reuters /
PAHO / NASA JPL, cross-checked across several briefings):
  1. Xi meets Putin in Shenzhen at APEC; first three-way summit with Trump
     set for Thursday.
  2. U.S. strikes a missile site on Qeshm Island; Iran answers with drones
     at Kuwait and Bahrain.
  3. Ukraine hits the Kerch (Crimea) bridge; part of the span collapses.
  4. Mary Peltola wins Alaska's Senate race; Democrats take the Senate 56-44.
  5. U.S. loses measles-elimination status after 26 years (5,412 cases).
  6. Ebola in DR Congo passes 11,000 cases.
  Ticker: Voyager 1 reaches one light-day from Earth; Nvidia revenue
  $115.8bn, up 103%; Quad leaders meet in Manila.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
NAVY2 = (28, 46, 84)
RED = (180, 35, 24)
GOLD = (201, 162, 39)
GOLD_L = (232, 184, 75)
RULE = (216, 210, 196)
GRAY = (90, 86, 76)
BLUE = (46, 92, 150)
SKY = (120, 170, 210)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(d, xy, s, fnt, fill=INK, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def kicker(d, x, y, s, color=RED):
    text(d, (x, y), s, font(SANS_B, 20), fill=color)


def star(d, cx, cy, r_out, r_in, n=5, fill=GOLD_L, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def flag_china(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    star(d, x + w * 0.28, y + h * 0.30, w * 0.16, w * 0.065, fill=(255, 222, 0))
    for sx, sy in [(0.55, 0.18), (0.68, 0.30), (0.68, 0.48), (0.55, 0.60)]:
        star(d, x + w * sx, y + h * sy, w * 0.055, w * 0.022, fill=(255, 222, 0))


def flag_russia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))
    d.rectangle([x, y, x + w, y + h], outline=(120, 120, 120), width=1)


def flag_usa(d, x, y, w, h):
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    cw, ch = w * 0.42, h * 4 / 7
    d.rectangle([x, y, x + cw, y + ch], fill=(60, 59, 110))
    for r in range(3):
        for c in range(4):
            d.ellipse([x + 6 + c * (cw - 12) / 3.5, y + 6 + r * (ch - 12) / 2.5,
                       x + 11 + c * (cw - 12) / 3.5, y + 11 + r * (ch - 12) / 2.5],
                      fill=(255, 255, 255))


def starburst(d, cx, cy, r, fill=(242, 194, 0), outline=(214, 120, 0)):
    pts = []
    n = 12
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(i * 180 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline)


def bridge(d, x, y, w, h):
    # deck
    d.line([x, y + h * 0.45, x + w, y + h * 0.45], fill=INK, width=5)
    # left arch (standing)
    d.arc([x, y, x + w * 0.38, y + h * 0.9], 180, 360, fill=INK, width=4)
    # right arch (standing)
    d.arc([x + w * 0.62, y, x + w, y + h * 0.9], 180, 360, fill=INK, width=4)
    # broken middle span: fallen segment tilted into the water
    d.line([x + w * 0.40, y + h * 0.45, x + w * 0.52, y + h * 0.85],
           fill=RED, width=6)
    d.line([x + w * 0.52, y + h * 0.85, x + w * 0.60, y + h * 0.45],
           fill=RED, width=6)
    # water
    for i, yy in enumerate([y + h * 0.88, y + h * 0.97]):
        for xx in range(0, w, 26):
            d.arc([x + xx, yy - 4, x + xx + 26, yy + 4], 180, 360,
                  fill=BLUE, width=2)


def dome(d, cx, y, w, h):
    # capitol dome
    d.pieslice([cx - w * 0.32, y, cx + w * 0.32, y + h * 0.75], 180, 360,
               fill=NAVY2)
    d.rectangle([cx - w * 0.42, y + h * 0.62, cx + w * 0.42, y + h * 0.72],
                fill=NAVY2)
    for i in range(5):
        xx = cx - w * 0.36 + i * w * 0.18
        d.rectangle([xx, y + h * 0.72, xx + w * 0.07, y + h], fill=NAVY2)
    d.line([cx, y - 8, cx, y], fill=NAVY2, width=3)


def virus(d, cx, cy, r, color=RED):
    for i in range(8):
        a = math.radians(i * 45)
        x1, y1 = cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a)
        x2, y2 = cx + r * 1.35 * math.cos(a), cy + r * 1.35 * math.sin(a)
        d.line([x1, y1, x2, y2], fill=color, width=4)
        d.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=color)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    for dx, dy, rr in [(-r * 0.35, -r * 0.2, 4), (r * 0.3, r * 0.25, 5),
                       (0, -r * 0.45, 3)]:
        d.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr],
                  fill=(255, 255, 255))


def cross(d, cx, cy, s, color=RED):
    d.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], radius=10,
                        outline=color, width=4)
    d.rectangle([cx - s * 0.22, cy - s * 0.6, cx + s * 0.22, cy + s * 0.6],
                fill=color)
    d.rectangle([cx - s * 0.6, cy - s * 0.22, cx + s * 0.6, cy + s * 0.22],
                fill=color)


def drone(d, cx, cy, s):
    d.rounded_rectangle([cx - s * 0.55, cy - s * 0.22, cx + s * 0.55,
                         cy + s * 0.22], radius=s * 0.2, fill=(70, 70, 70))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax, ay = cx + sx * s * 0.75, cy + sy * s * 0.35
            d.line([cx + sx * s * 0.4, cy, ax, ay], fill=(70, 70, 70), width=3)
            d.ellipse([ax - s * 0.22, ay - 3, ax + s * 0.22, ay + 3],
                      fill=(120, 120, 120))


def fit_font(d, lines, path, start, max_w):
    size = start
    while size > 20:
        f = font(path, size)
        if max(d.textlength(l, font=f) for l in lines) <= max_w:
            return f
        size -= 2
    return font(path, size)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- masthead ----------
    d.rectangle([0, 0, W, 140], fill=NAVY)
    text(d, (W // 2, 18), "THE WORLD IN ONE DAY", font(SERIF_B, 62),
         fill=(255, 255, 255), anchor="ma")
    text(d, (W // 2, 96), "WEDNESDAY  ·  18 NOVEMBER 2026", font(SANS_B, 28),
         fill=GOLD_L, anchor="ma")
    d.line([0, 140, W, 140], fill=GOLD, width=4)

    # ---------- lead story: Xi meets Putin ----------
    kicker(d, 40, 166, "APEC  ·  SHENZHEN")
    lead_lines = ["XI MEETS PUTIN", "IN SHENZHEN"]
    lead_fnt = fit_font(d, lead_lines, SERIF_B, 64, 570)
    text(d, (40, 194), lead_lines[0], lead_fnt, fill=INK)
    text(d, (40, 262), lead_lines[1], lead_fnt, fill=INK)
    sub = ("China and Russia open APEC talks a day before "
           "the first three-way summit with Trump.")
    yy = 344
    for ln in wrap(d, sub, font(SANS, 25), 560):
        text(d, (40, yy), ln, font(SANS, 25), fill=(60, 60, 60))
        yy += 32
    # flags pictogram, right side
    fx, fy, fw, fh = 640, 176, 104, 156
    flag_china(d, fx, fy, fw, fh)
    flag_russia(d, fx + 122, fy, fw, fh)
    flag_usa(d, fx + 244, fy, fw, fh)
    for i, lab in enumerate(["CHINA", "RUSSIA", "USA"]):
        text(d, (fx + i * 122 + fw // 2, fy + fh + 12), lab,
             font(SANS_B, 19), fill=INK, anchor="ma")
    text(d, (812, 392), "TRUMP JOINS THURSDAY", font(SANS_B, 20),
         fill=RED, anchor="ma")
    d.line([40, 452, 984, 452], fill=RULE, width=2)

    # ---------- row 2: Gulf + Crimea bridge ----------
    # left: Gulf
    kicker(d, 40, 472, "THE GULF")
    head = wrap(d, "U.S. HITS QESHM ISLAND", font(SERIF_B, 36), 460)
    yy = 500
    for ln in head:
        text(d, (40, yy), ln, font(SERIF_B, 36), fill=INK)
        yy += 42
    sub2 = "Iran answers with drones at Kuwait and Bahrain."
    yy += 4
    for ln in wrap(d, sub2, font(SANS, 22), 460):
        text(d, (40, yy), ln, font(SANS, 22), fill=(60, 60, 60))
        yy += 28
    starburst(d, 120, 660, 26)
    drone(d, 330, 660, 42)
    d.line([512, 470, 512, 690], fill=RULE, width=2)
    # right: Crimea bridge
    kicker(d, 540, 472, "UKRAINE")
    head = wrap(d, "CRIMEA BRIDGE HIT", font(SERIF_B, 36), 444)
    yy = 500
    for ln in head:
        text(d, (540, yy), ln, font(SERIF_B, 36), fill=INK)
        yy += 42
    sub2 = "Part of the Kerch span falls into the strait."
    yy += 4
    for ln in wrap(d, sub2, font(SANS, 22), 444):
        text(d, (540, yy), ln, font(SANS, 22), fill=(60, 60, 60))
        yy += 28
    bridge(d, 600, 622, 320, 62)
    d.line([40, 692, 984, 692], fill=RULE, width=2)

    # ---------- row 3: three stories ----------
    panels = [
        (40, "U.S. POLITICS", "PELTOLA WINS ALASKA",
         "Democrats take Senate 56–44.", "dome"),
        (357, "HEALTH", "U.S. LOSES MEASLES-FREE STATUS",
         "5,412 cases in 2026 · 10 deaths.", "virus"),
        (674, "HEALTH", "EBOLA IN CONGO PASSES 11,000",
         "2nd-largest outbreak on record.", "cross"),
    ]
    for x, kick, head3, sub3, pic in panels:
        kicker(d, x, 706, kick)
        if pic == "dome":
            dome(d, x + 154, 732, 150, 56)
        elif pic == "virus":
            virus(d, x + 154, 762, 26)
        else:
            cross(d, x + 154, 762, 26)
        yy = 796
        for ln in wrap(d, head3, font(SERIF_B, 23), 300):
            text(d, (x, yy), ln, font(SERIF_B, 23), fill=INK)
            yy += 27
        text(d, (x, 882), sub3, font(SANS, 18), fill=(60, 60, 60))
    d.line([40, 908, 984, 908], fill=RULE, width=2)

    # ---------- bottom ticker ----------
    d.rectangle([0, 908, W, H], fill=NAVY)
    text(d, (W // 2, 922),
         "ALSO:  VOYAGER 1 REACHES ONE LIGHT-DAY FROM EARTH",
         font(SANS_B, 21), fill=(255, 255, 255), anchor="ma")
    text(d, (W // 2, 952),
         "NVIDIA REVENUE $115.8BN, UP 103%  ·  QUAD MEETS IN MANILA",
         font(SANS_B, 21), fill=(255, 255, 255), anchor="ma")
    text(d, (W // 2, 990),
         "Sources: AFP · AP · Reuters · PAHO · NASA JPL  —  18 November 2026",
         font(SANS, 15), fill=(170, 175, 195), anchor="ma")

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
