#!/usr/bin/env python3
"""Fit photo, sketch and mask to 1080×1920 with the SAME crop, extending the sky at the top if needed.

    python3 fit_916.py IN_DIR OUT_DIR [--focus-x 0.5]

IN_DIR = diff_mask.py output (photo.png, sketch.png, people_mask.png). Scales so the width fills 1080 (crops
the sides around the people, or --focus-x), and if the image is then shorter than 1920, extends the top by
stretching the top rows' colours upward with a smooth vertical gradient plus soft noise (never mirrored).
"""
import argparse, os
import cv2, numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--focus-x", type=float)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
names = ["photo.png", "sketch.png", "people_mask.png"]; ims = [cv2.imread(os.path.join(a.inp, n), cv2.IMREAD_UNCHANGED) for n in names]
h, w = ims[0].shape[:2]; mask = ims[2] if ims[2].ndim == 2 else ims[2][..., 0]
ys, xs = np.where(mask > 128); fx = a.focus_x if a.focus_x is not None else (xs.mean() / w if len(xs) else 0.5)
# fill the width; if that leaves the photo under 60% of the frame height, scale up more and crop the sides
s = 1080 / w if h * 1080 / w >= 1920 * 0.6 else 1920 * 0.6 / h
nw, nh = int(round(w * s)), int(round(h * s))
x0 = int(np.clip(fx * nw - 540, 0, max(0, nw - 1080)))
outs = []
for n, im in zip(names, ims):
    r = cv2.resize(im, (nw, nh), interpolation=cv2.INTER_LANCZOS4 if n != "people_mask.png" else cv2.INTER_LINEAR)[:, x0:x0 + 1080]
    if nh >= 1920:
        y0 = nh - 1920; outs.append(r[y0:y0 + 1920])  # keep the bottom (people), crop sky
        continue
    ext = 1920 - nh
    if n == "people_mask.png":
        top = np.zeros((ext,) + r.shape[1:], r.dtype)
    else:
        band = cv2.GaussianBlur(r[:12].astype(np.float32).mean(0, keepdims=True), (0, 0), 25)  # row colour of the top edge, smoothed
        t = np.linspace(1, 0, ext)[:, None, None] ** 1.5
        sky = band * (1 + 0.03 * t)  # same colour as the top edge, slightly deeper toward the top
        rng = np.random.default_rng(3); sky = sky + rng.normal(0, 1.2, (ext, r.shape[1], r.shape[2]))
        top = np.clip(sky, 0, 255).astype(r.dtype)
        # feather the seam over 40 rows
        k = min(40, nh); blend = np.linspace(0, 1, k)[:, None, None]
        r = r.copy(); r[:k] = (top[-1:].astype(np.float32) * (1 - blend) + r[:k].astype(np.float32) * blend).astype(r.dtype)
    outs.append(np.vstack([top, r]))
for n, o in zip(names, outs): cv2.imwrite(os.path.join(a.out, n), o)
print(f"fitted to 1080x1920 (scale {s:.3f}, crop x {x0}, sky extended {max(0, 1920 - nh)} px) -> {a.out}")
