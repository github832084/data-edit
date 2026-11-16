#!/usr/bin/env python3
"""Cut the three Gemini 2x2 sheets into 12 frames A-L at 1920x1080.

    python3 cut_sheets.py IN_DIR OUT_DIR      (IN_DIR has sheet-1.png, sheet-2.png, sheet-3.png)

Finds the thin black grid lines (darkest row/column near the middle), crops each panel inside them
(trims 4 px of line), and resizes to 1920x1080 (crop-to-fill, never stretched). Letters follow the prompts:
  sheet-1: TL=C TR=F BL=H BR=I     sheet-2: TL=B TR=E BL=G BR=J     sheet-3: TL=A TR=D BL=K BR=L
Then paints out the Gemini sparkle (bottom-right of the whole sheet = panel BR) with video-core paint_out.py.
"""
import os, subprocess, sys
import cv2, numpy as np

inp, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
MAP = {1: "CFHI", 2: "BEGJ", 3: "ADKL"}
here = os.path.dirname(os.path.abspath(__file__)); paint = os.path.join(here, "..", "video-core", "scripts", "paint_out.py")
def split_line(prof, n):
    lo, hi = int(n * 0.4), int(n * 0.6); return lo + int(np.argmin(prof[lo:hi]))
def fill(im, W=1920, H=1080):
    s = max(W / im.shape[1], H / im.shape[0]); r = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4)
    y0, x0 = (r.shape[0] - H) // 2, (r.shape[1] - W) // 2; return r[y0:y0 + H, x0:x0 + W]
for k, letters in MAP.items():
    p = os.path.join(inp, f"sheet-{k}.png")
    if not os.path.exists(p): print(f"missing {p}: ask the user for it"); sys.exit(2)
    im = cv2.imread(p); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    cx, cy = split_line(g.mean(0), g.shape[1]), split_line(g.mean(1), g.shape[0]); t = 4
    panels = [im[:cy - t, :cx - t], im[:cy - t, cx + t:], im[cy + t:, :cx - t], im[cy + t:, cx + t:]]
    for L, pan in zip(letters, panels):
        f = os.path.join(out, f"{L}.png"); cv2.imwrite(f, fill(pan)); print(f)
    br = os.path.join(out, f"{letters[3]}.png"); subprocess.run([sys.executable, paint, br, br, "--corner", "br", "--size", "0.09"], check=True)
