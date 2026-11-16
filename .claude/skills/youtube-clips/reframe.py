#!/usr/bin/env python3
"""Reframe a 16:9 segment to 9:16 by following the speaker's face.

    python3 reframe.py SOURCE START END OUT_FRAMES_DIR [--fps 30] [--smooth 0.8] [--zoom 1.0]

Detects faces every 3rd frame (MediaPipe face detector via video-core/scripts/vision.py), keeps the largest/most central face
track, smooths the crop centre with a critically damped follow (--smooth seconds), and writes 1080×1920
JPEG frames (Kit.clip-compatible numbering) plus OUT/crop.json. No colour changes. Audio: cut separately with
ffmpeg -ss START -to END. If no face is found the crop stays centred.
"""
import argparse, json, os, subprocess
import cv2, numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("start", type=float); ap.add_argument("end", type=float); ap.add_argument("out")
ap.add_argument("--fps", type=int, default=30); ap.add_argument("--smooth", type=float, default=0.8); ap.add_argument("--zoom", type=float, default=1.0)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cap = cv2.VideoCapture(a.src); cap.set(cv2.CAP_PROP_POS_MSEC, a.start * 1000)
W, H = int(cap.get(3)), int(cap.get(4)); src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
cw = int(H * 9 / 16 / a.zoom); ch = int(H / a.zoom)
import sys as _s, os as _o; _s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "..", "video-core", "scripts")); import vision
frames, cx_raw = [], []
n = int((a.end - a.start) * a.fps); last = W / 2
for i in range(n):
    cap.set(cv2.CAP_PROP_POS_MSEC, (a.start + i / a.fps) * 1000)
    ok, fr = cap.read()
    if not ok: break
    if i % 3 == 0:
        faces = vision.faces(cv2.resize(fr, (W // 2, H // 2)))
        if faces:
            x, y, w, h, _ = max(faces, key=lambda f: f[2] * f[3] - abs(f[0] * 2 + f[2] - W / 2) * 0.5)
            last = (x + w / 2) * 2
    cx_raw.append(last); frames.append(i)
# smooth: critically damped follow
k = 1 - np.exp(-1 / (a.fps * max(a.smooth, 0.05))); v = cx_raw[0] if cx_raw else W / 2; cx = []
for x in cx_raw: v += (x - v) * k; cx.append(v)
crops = []
for i, c in enumerate(cx):
    cap.set(cv2.CAP_PROP_POS_MSEC, (a.start + i / a.fps) * 1000); ok, fr = cap.read()
    if not ok: break
    x0 = int(np.clip(c - cw / 2, 0, W - cw)); y0 = (H - ch) // 2
    crop = cv2.resize(fr[y0:y0 + ch, x0:x0 + cw], (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(os.path.join(a.out, f"{i + 1:06d}.jpg"), crop, [cv2.IMWRITE_JPEG_QUALITY, 94]); crops.append([x0, y0, cw, ch])
json.dump({"src": a.src, "start": a.start, "end": a.end, "fps": a.fps, "crops": crops}, open(os.path.join(a.out, "crop.json"), "w"))
print(f"{len(crops)} frames -> {a.out}")
