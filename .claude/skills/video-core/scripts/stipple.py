#!/usr/bin/env python3
"""Turn a photo into stipple dots for a particle portrait.

    python3 stipple.py PHOTO OUT.json [--n 25000] [--cutout] [--size 1080] [--seed 1]

Dots are sampled with probability from darkness + local contrast + edges, so faces read even with few
dots. --cutout removes the background first (rembg), so dots only land on the person.
OUT.json: {"w","h","pts":[[x,y,r,brightness],...]} normalised to 0..1. Same --seed and --n for two photos
gives a 1:1 dot pairing for morphing (dot i of photo A flies to dot i of photo B).
"""
import argparse, json
import numpy as np, cv2
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("photo"); ap.add_argument("out"); ap.add_argument("--n", type=int, default=25000)
ap.add_argument("--cutout", action="store_true"); ap.add_argument("--size", type=int, default=1080); ap.add_argument("--seed", type=int, default=1)
a = ap.parse_args()
im = Image.open(a.photo).convert("RGB")
alpha = None
if a.cutout:
    from rembg import remove
    alpha = np.array(remove(im, only_mask=True).convert("L")).astype(np.float32) / 255
s = a.size / max(im.size); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
if alpha is not None: alpha = cv2.resize(alpha, im.size)
g = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
clahe = cv2.createCLAHE(2.5, (8, 8)).apply((g * 255).astype(np.uint8)).astype(np.float32) / 255  # local contrast
edges = cv2.GaussianBlur(cv2.Canny((clahe * 255).astype(np.uint8), 60, 140).astype(np.float32) / 255, (0, 0), 1.2)
w = (1 - clahe) ** 1.6 * 0.7 + edges * 0.9 + 0.02
if alpha is not None: w *= alpha
p = (w / w.sum()).ravel()
rng = np.random.default_rng(a.seed)
idx = rng.choice(p.size, size=a.n, replace=True, p=p)
ys, xs = np.divmod(idx, g.shape[1]); jit = rng.random((a.n, 2))
b = clahe.ravel()[idx]
pts = np.stack([(xs + jit[:, 0]) / g.shape[1], (ys + jit[:, 1]) / g.shape[0], 0.6 + (1 - b) * 1.4, 1 - b * 0.6], 1)
order = np.lexsort((pts[:, 0], np.round(pts[:, 1] * 40)))  # stable spatial order -> nicer morph pairing
json.dump({"w": g.shape[1], "h": g.shape[0], "pts": np.round(pts[order], 4).tolist()}, open(a.out, "w"))
print(f"{a.n} dots -> {a.out}")
