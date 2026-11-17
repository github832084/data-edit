#!/usr/bin/env python3
"""Person mattes for every frame, so words and UI can sit BEHIND a person.

    python3 matte.py FRAMES_DIR OUT_DIR [--model mediapipe|u2net_human_seg|isnet-anime|birefnet-portrait] [--smooth 2]

FRAMES_DIR is a frames.sh sequence. OUT_DIR gets 000001.png ... as 8-bit alpha masks (white = person),
same size as the frames. Draw order in the scene: background frame -> your graphics -> frame clipped by mask.
- mediapipe (default, fast, real people), u2net_human_seg / birefnet-portrait (rembg, cleaner hair),
  isnet-anime (anime / cartoon clips).
- --smooth N averages masks over +-N frames to stop edge flicker.
Also writes OUT_DIR/bounds.json: per frame [x0,y0,x1,y1] of the person, to place text off faces and bodies.
"""
import argparse, glob, json, os
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("frames"); ap.add_argument("out"); ap.add_argument("--model", default="mediapipe"); ap.add_argument("--smooth", type=int, default=1)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
files = sorted(glob.glob(os.path.join(a.frames, "*.jpg")) + glob.glob(os.path.join(a.frames, "*.png")))
masks = []
if a.model == "mediapipe":
    import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import vision
    for f in files:
        masks.append(vision.person_mask(np.array(Image.open(f).convert("RGB"))))
else:
    from rembg import new_session, remove
    sess = new_session(a.model)
    for f in files:
        m = remove(Image.open(f).convert("RGB"), session=sess, only_mask=True)
        masks.append(np.array(m.convert("L")))
bounds = []
for i in range(len(masks)):
    lo, hi = max(0, i - a.smooth), min(len(masks), i + a.smooth + 1)
    m = np.mean(np.stack(masks[lo:hi]).astype(np.float32), 0).astype(np.uint8)
    Image.fromarray(m).save(os.path.join(a.out, f"{i + 1:06d}.png"))
    ys, xs = np.where(m > 128); bounds.append([int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None)
json.dump(bounds, open(os.path.join(a.out, "bounds.json"), "w"))
print(f"{len(masks)} mattes -> {a.out}")
