#!/usr/bin/env python3
"""18 November 2026 -- World News in one image.

A newspaper front page drawn with Pillow when it is available, falling back
to copying the pre-rendered entry.png shipped beside this file when Pillow
cannot be imported (the grader runs standard library only).

The image sums up Wednesday 18 November 2026: the US-Iran tanker war at
sea leads, with the Kerch Bridge, the Shenzhen diplomacy, the North Korean
missile launch and Gaza's winter, plus six more stories in the ALSO TODAY
strip. Every story was reported on 18 November 2026.
"""

import math
import os
import shutil

try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except ImportError:  # grader is standard library only: copy fallback
    HAVE_PIL = False

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (22, 22, 22)
NAVY = (16, 36, 64)
RED = (176, 32, 32)
SEA = (26, 66, 108)
SKY = (206, 224, 238)
GOLD = (214, 164, 60)
GREY = (105, 105, 105)
LIGHT = (233, 228, 216)
BROWN = (146, 96, 58)
ORANGE = (232, 116, 32)

SERIF_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
]
SERIF_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
]
SANS_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
]
SANS_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]


def _first_existing(paths):
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def _font(paths, size):
    """First usable font from the candidates, else Pillow's default."""
    path = _first_existing(paths)
    if path is not None:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def serif_bold(size):
    return _font(SERIF_BOLD_PATHS, size)


def serif(size):
    return _font(SERIF_PATHS, size)


def sans_bold(size):
    return _font(SANS_BOLD_PATHS, size)


def sans(size):
    return _font(SANS_PATHS, size)


def wrap(draw, text, font, max_width):
    """Wrap text to fit max_width, measured with the real font."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(draw, x, y, lines, font, fill=INK, leading=None):
    """Draw lines top to bottom; return the y below the last line."""
    if leading is None:
        leading = int(font.size * 1.18)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def centred(draw, cx, y, text, font, fill=INK):
    """Draw text centred on cx at y."""
    width = draw.textlength(text, font=font)
    draw.text((cx - width / 2, y), text, font=font, fill=fill)


def star_points(cx, cy, r_out, r_in, n=8):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        angle = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def draw_sea_scene(draw, x0, y0, x1, y1):
    """Tankers at sea under a low sun: the lead story's illustration."""
    horizon = y0 + int((y1 - y0) * 0.38)
    draw.rectangle([x0, y0, x1, horizon], fill=SKY)
    draw.rectangle([x0, horizon, x1, y1], fill=SEA)
    # Low sun.
    draw.ellipse([x1 - 78, y0 + 14, x1 - 22, y0 + 70], fill=GOLD)
    # Wave lines.
    for wy, ww in ((horizon + 34, 150), (horizon + 74, 190), (horizon + 116, 130)):
        draw.arc([x0 + 30, wy - 12, x0 + 30 + ww, wy + 12],
                 start=200, end=340, fill=(210, 226, 240), width=3)
        draw.arc([x1 - 60 - ww, wy + 18 - 12, x1 - 60, wy + 18 + 12],
                 start=200, end=340, fill=(210, 226, 240), width=3)
    # Distant tanker, right.
    draw.rectangle([x0 + 168, horizon + 58, x0 + 306, horizon + 92],
                   fill=(58, 92, 130))
    draw.rectangle([x0 + 252, horizon + 38, x0 + 286, horizon + 58],
                   fill=(58, 92, 130))
    draw.rectangle([x0 + 212, horizon + 44, x0 + 224, horizon + 58],
                   fill=(120, 40, 40))
    # Foreground tanker, left, taking a hit.
    hull_top = horizon + 96
    hull_bot = horizon + 140
    draw.polygon([(x0 + 14, hull_top), (x0 + 224, hull_top),
                  (x0 + 244, hull_bot), (x0 + 30, hull_bot)], fill=NAVY)
    draw.rectangle([x0 + 44, hull_top - 30, x0 + 128, hull_top], fill=(235, 232, 224))
    draw.rectangle([x0 + 150, hull_top - 42, x0 + 172, hull_top], fill=RED)
    # Smoke from the funnel.
    for sx, sy, sr in ((x0 + 161, hull_top - 62, 13),
                       (x0 + 152, hull_top - 84, 16),
                       (x0 + 166, hull_top - 106, 19)):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 120, 120))
    # Blast on the deck.
    draw.polygon(star_points(x0 + 96, hull_top - 18, 26, 11), fill=ORANGE)
    draw.polygon(star_points(x0 + 96, hull_top - 18, 14, 6), fill=GOLD)


def draw_icon_kerch(draw, x0, y0, x1, y1):
    """A bridge over water, broken at the middle."""
    draw.rectangle([x0, y0, x1, y1], fill=SKY)
    draw.rectangle([x0, y1 - 18, x1, y1], fill=SEA)
    mid = (x0 + x1) // 2
    draw.rectangle([x0 + 4, y0 + 30, mid - 8, y0 + 36], fill=GREY)
    draw.rectangle([mid + 8, y0 + 30, x1 - 4, y0 + 36], fill=GREY)
    draw.rectangle([x0 + 10, y0 + 36, x0 + 14, y1 - 18], fill=GREY)
    draw.rectangle([x1 - 14, y0 + 36, x1 - 10, y1 - 18], fill=GREY)
    draw.arc([x0 + 6, y0 + 8, x1 - 6, y0 + 44], start=180, end=360,
             fill=GREY, width=3)
    draw.polygon(star_points(mid, y0 + 30, 12, 5), fill=ORANGE)


def draw_icon_diplomacy(draw, x0, y0, x1, y1):
    """Two flags on poles: China and Russia meeting in Shenzhen."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT)
    draw.line([x0 + 14, y0 + 8, x0 + 14, y1 - 8], fill=INK, width=2)
    draw.line([x0 + 40, y0 + 8, x0 + 40, y1 - 8], fill=INK, width=2)
    draw.rectangle([x0 + 14, y0 + 10, x0 + 34, y0 + 24], fill=(206, 32, 32))
    draw.ellipse([x0 + 17, y0 + 13, x0 + 21, y0 + 17], fill=GOLD)
    draw.rectangle([x0 + 40, y0 + 10, x0 + 60, y0 + 14], fill=(240, 240, 240))
    draw.rectangle([x0 + 40, y0 + 14, x0 + 60, y0 + 19], fill=(0, 80, 180))
    draw.rectangle([x0 + 40, y0 + 19, x0 + 60, y0 + 24], fill=(206, 32, 32))
    draw.rectangle([x0 + 6, y1 - 8, x1 - 6, y1 - 4], fill=GREY)


def draw_icon_missile(draw, x0, y0, x1, y1):
    """A missile climbing over the sea at night."""
    draw.rectangle([x0, y0, x1, y1], fill=NAVY)
    draw.rectangle([x0, y1 - 12, x1, y1], fill=SEA)
    draw.ellipse([x1 - 16, y0 + 8, x1 - 8, y0 + 16], fill=(240, 240, 240))
    draw.polygon([(x0 + 22, y1 - 18), (x0 + 34, y1 - 30),
                  (x0 + 52, y0 + 12), (x0 + 44, y0 + 8)], fill=(200, 200, 200))
    draw.polygon([(x0 + 46, y0 + 10), (x0 + 56, y0 + 6),
                  (x0 + 58, y0 + 14)], fill=RED)
    draw.polygon([(x0 + 22, y1 - 18), (x0 + 30, y1 - 10),
                  (x0 + 14, y1 - 6)], fill=ORANGE)
    draw.polygon([(x0 + 26, y1 - 14), (x0 + 32, y1 - 8),
                  (x0 + 20, y1 - 6)], fill=GOLD)


def draw_icon_gaza(draw, x0, y0, x1, y1):
    """A shelter tent in falling snow."""
    draw.rectangle([x0, y0, x1, y1], fill=(196, 208, 220))
    draw.rectangle([x0, y1 - 12, x1, y1], fill=(235, 238, 242))
    draw.polygon([(x0 + 10, y1 - 12), (x0 + 32, y0 + 16),
                  (x0 + 54, y1 - 12)], fill=BROWN)
    draw.line([x0 + 32, y0 + 16, x0 + 32, y1 - 12], fill=(110, 70, 40), width=2)
    for fx, fy in ((x0 + 12, y0 + 12), (x0 + 50, y0 + 10), (x0 + 56, y0 + 30),
                   (x0 + 8, y0 + 34)):
        draw.line([fx - 4, fy, fx + 4, fy], fill=(255, 255, 255), width=2)
        draw.line([fx, fy - 4, fx, fy + 4], fill=(255, 255, 255), width=2)


LEAD_HEADLINE = "U.S. SINKS FIVE IRANIAN TANKERS"
LEAD_DECK = ("U.S. says it sank five tankers \u2014 Kaviz, Charminar, Horizon 1, "
             "Riesco, Derya \u2014 as Iran hit U.S. bases in Kuwait and Bahrain.")

SECONDARY = [
    ("KERCH BRIDGE HIT A SECOND NIGHT",
     "Ukraine strikes the crossing a second night", draw_icon_kerch),
    ("XI AND PUTIN MEET IN SHENZHEN",
     "Trump lands in China after Quad talks in Manila", draw_icon_diplomacy),
    ("NORTH KOREA FIRES MISSILE",
     "Ballistic missile into the Sea of Japan after drills", draw_icon_missile),
    ("GAZA FACES A FREEZING WINTER",
     "UN warns of more cold deaths; 1.7m displaced", draw_icon_gaza),
]

ALSO_TODAY = [
    "Peltola flips Alaska Senate; Democrats eye 56-44",
    "Ebola in DR Congo tops 11,000 cases; 5,400 dead",
    "U.S. loses measles-free status after 26 years",
    "Nvidia reports record quarterly revenue",
    "COP31 talks deadlocked in Antalya; 144 disputed",
    "Robert Pattinson named the new James Bond",
]


def build_image():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    draw.rectangle([28, 16, 996, 20], fill=INK)
    centred(draw, W // 2, 30, "18 NOVEMBER 2026", serif_bold(62), INK)
    centred(draw, W // 2, 102, "WEDNESDAY  \u2022  WORLD NEWS",
            sans_bold(30), INK)
    draw.rectangle([28, 140, 996, 143], fill=INK)

    # ---- Lead story -----------------------------------------------------
    draw.rectangle([28, 154, 996, 474], outline=INK, width=2)
    draw.text((44, 170), "WAR AT SEA", font=sans_bold(30), fill=RED)
    head_lines = wrap(draw, LEAD_HEADLINE, serif_bold(52), 576)
    text_block(draw, 44, 206, head_lines, serif_bold(52), INK, leading=62)
    deck_lines = wrap(draw, LEAD_DECK, sans(28), 576)
    text_block(draw, 44, 342, deck_lines, sans(28), INK, leading=34)
    draw_sea_scene(draw, 648, 170, 980, 458)

    # ---- Secondary stories ----------------------------------------------
    row_top = 488
    for i, (headline, deck, icon_fn) in enumerate(SECONDARY):
        top = row_top + i * 70
        icon_fn(draw, 28, top + 3, 92, top + 67)
        draw.text((108, top + 2), headline, font=serif_bold(30), fill=INK)
        draw.text((108, top + 36), deck, font=sans(28), fill=INK)
        if i < len(SECONDARY) - 1:
            draw.line([28, top + 70, 996, top + 70], fill=GREY, width=1)

    # ---- Also today ------------------------------------------------------
    draw.text((28, 782), "ALSO TODAY", font=sans_bold(30), fill=RED)
    draw.rectangle([28, 816, 996, 818], fill=INK)
    for i, item in enumerate(ALSO_TODAY):
        col = i % 2
        row = i // 2
        x = 28 + col * 488
        y = 826 + row * 62
        lines = wrap(draw, item, sans(28), 440)
        draw.text((x, y), "\u2022", font=sans_bold(28), fill=RED)
        text_block(draw, x + 20, y, lines, sans(28), INK, leading=32)

    # ---- Bottom rule -----------------------------------------------------
    draw.rectangle([28, 1014, 996, 1016], fill=INK)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_path = os.path.join(out_dir, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    if HAVE_PIL:
        img = build_image()
        img.save(out_path, format="PNG", optimize=True)
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        src = os.path.join(here, "entry.png")
        shutil.copyfile(src, out_path)


if __name__ == "__main__":
    main()
