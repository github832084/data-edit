#!/usr/bin/env python3
"""Make crayon carousel slides: crayon drawing on top ("One day"), real photo below ("Day one").

    python3 make_slides.py IN_DIR OUT_DIR [--only N] [--force] [--gap 8]

IN_DIR holds photo.jpg + photo_drawing.png pairs (any image extension). Photos are taken in name order.
Each slide is 1080×1350 (4:5). Both halves are cropped to fill (never stretched), centred on the face
(OpenCV) or the upper body, so nobody gets cut off. Labels are Caveat (from video-core/fonts, installed with
fonts.sh caveat), white with a soft shadow. Writes slide_01.png ... and contact_sheet.jpg.
"""
import argparse, glob, os, re, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--only", type=int)
ap.add_argument("--force", action="store_true"); ap.add_argument("--gap", type=int, default=8)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
W, H = 1080, 1350; half = (H - a.gap) // 2
EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic")
files = sorted(f for f in os.listdir(a.inp) if f.lower().endswith(EXT))
photos = [f for f in files if not re.search(r"_drawing\.", f, re.I)]
pairs, missing = [], []
for p in photos:
    stem = os.path.splitext(p)[0]; d = next((f for f in files if os.path.splitext(f)[0].lower() == stem.lower() + "_drawing"), None)
    (pairs.append((p, d)) if d else missing.append(p))
if missing: print("missing drawings for:", ", ".join(missing), "- ask the user for them"); sys.exit(2)

fdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video-core", "fonts", "caveat", "files")
fp = next(iter(sorted(glob.glob(os.path.join(fdir, "caveat-latin-700-normal.woff2")) + glob.glob(os.path.join(fdir, "*latin-7*.woff2")))), None)
def font(size):
    if fp:
        try: return ImageFont.truetype(fp, size)
        except Exception: pass
    print("Caveat not found: run bash .claude/skills/video-core/scripts/fonts.sh caveat"); sys.exit(2)

import sys as _s, os as _o; _s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "..", "video-core", "scripts")); import vision
def focus(im):
    bgr = cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR); s = 800 / max(bgr.shape[:2]); f = vision.faces(cv2.resize(bgr, None, fx=s, fy=s))
    if f:
        x, y, w, h, _ = f[0]; return ((x + w / 2) / s / im.width, (y + h * 1.2) / s / im.height, (h * 3) / s / im.height)
    return (0.5, 0.42, None)

def fill(im, w, h):
    fx, fy, need = focus(im)
    sc = max(w / im.width, h / im.height); iw, ih = int(im.width * sc + 0.5), int(im.height * sc + 0.5)
    im2 = im.convert("RGB").resize((iw, ih), Image.LANCZOS)
    x0 = int(np.clip(fx * iw - w / 2, 0, iw - w)); y0 = int(np.clip(fy * ih - h * 0.45, 0, ih - h))
    return im2.crop((x0, y0, x0 + w, y0 + h))

def label(canvas, text, x, y):
    f = font(92); sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    d.text((x + 3, y + 5), text, font=f, fill=(0, 0, 0, 150)); sh = sh.filter(ImageFilter.GaussianBlur(6))
    canvas.alpha_composite(sh); ImageDraw.Draw(canvas).text((x, y), text, font=f, fill=(255, 255, 255, 255))

made = []
for i, (p, d) in enumerate(pairs, 1):
    if a.only and i != a.only: continue
    out = os.path.join(a.out, f"slide_{i:02d}.png")
    if os.path.exists(out) and not a.force: print(f"REFUSING: {out} exists. Ask the user, then re-run with --force."); sys.exit(3)
    c = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    c.paste(fill(Image.open(os.path.join(a.inp, d)), W, half), (0, 0))
    c.paste(fill(Image.open(os.path.join(a.inp, p)), W, H - half - a.gap), (0, half + a.gap))
    label(c, "One day", 48, 30); label(c, "Day one", 48, half + a.gap + 30)
    c.convert("RGB").save(out); made.append(out); print(out)
if not a.only and made:
    sheet = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video-core", "scripts", "contact_sheet.py")
    os.system(f'python3 "{sheet}" "{os.path.join(a.out, "contact_sheet.jpg")}" ' + " ".join(f'"{m}"' for m in made))
