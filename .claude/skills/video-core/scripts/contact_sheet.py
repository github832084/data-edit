#!/usr/bin/env python3
"""Contact sheet: tile stills into one labelled image to show the user before the full render.

    python3 contact_sheet.py OUT.jpg IMG1 IMG2 ...            (stills from render.cjs --stills)
    python3 contact_sheet.py OUT.jpg --video clip.mp4 --n 12  (sample a video evenly)
    python3 contact_sheet.py OUT.jpg --video clip.mp4 --every 0.5   (one frame every 0.5 s, e.g. 2 fps reference analysis)
Labels show the timestamp taken from the still's file name (still_0012.50.png) or from the sample time.
"""
import argparse, os, re, subprocess, tempfile, math
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("images", nargs="*")
ap.add_argument("--video"); ap.add_argument("--n", type=int, default=12); ap.add_argument("--every", type=float)
ap.add_argument("--cols", type=int); ap.add_argument("--width", type=int, default=2400)
a = ap.parse_args()

items = []
if a.video:
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video], capture_output=True, text=True).stdout)
    times = [i * a.every for i in range(int(dur / a.every) + 1)] if a.every else [dur * (i + 0.5) / a.n for i in range(a.n)]
    tmp = tempfile.mkdtemp()
    for i, t in enumerate(times):
        f = os.path.join(tmp, f"{i:04d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1", "-vf", "scale=640:-2", f], check=True)
        if os.path.exists(f): items.append((f, f"{t:.2f}s"))
else:
    for f in a.images:
        m = re.search(r"(\d+\.\d+)", os.path.basename(f)); items.append((f, f"{float(m.group(1)):.2f}s" if m else os.path.basename(f)))
if not items: raise SystemExit("no images")

ims = [Image.open(f).convert("RGB") for f, _ in items]
ar = ims[0].width / ims[0].height
cols = a.cols or (6 if ar < 1 else 4) if len(ims) > 4 else len(ims)
rows = math.ceil(len(ims) / cols); gap = 12; lab = 40
tw = (a.width - gap * (cols + 1)) // cols; th = int(tw / ar)
sheet = Image.new("RGB", (a.width, rows * (th + lab + gap) + gap), (24, 24, 24))
d = ImageDraw.Draw(sheet)
try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
except Exception: font = ImageFont.load_default()
for i, (im, (_, label)) in enumerate(zip(ims, items)):
    r, c = divmod(i, cols); x = gap + c * (tw + gap); y = gap + r * (th + lab + gap)
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + lab))
    d.text((x + 4, y + 6), f"#{i + 1}  {label}", fill=(240, 240, 240), font=font)
sheet.save(a.out, quality=90)
print("contact sheet ->", a.out)
