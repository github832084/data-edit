#!/usr/bin/env python3
"""Mouth-open curves for lip sync: one 0..1 value per video frame per speaker, from voice loudness,
gated to that speaker's aligned words so only the person talking moves their mouth.

    python3 mouth.py VOICE ALIGN.json OUT.json [--fps 30] [--attack 0.04] [--release 0.09]

OUT.json: {"fps":30, "all":[...], "<speaker>":[...], ...}   use Kit.mouth(k.data.mouth[speaker], t)
"""
import argparse, json, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("voice"); ap.add_argument("align"); ap.add_argument("out")
ap.add_argument("--fps", type=int, default=30); ap.add_argument("--attack", type=float, default=0.04); ap.add_argument("--release", type=float, default=0.09)
a = ap.parse_args()
sr = 16000
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.voice, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
y = np.frombuffer(raw, dtype=np.float32)
al = json.load(open(a.align))
n = int(np.ceil(len(y) / sr * a.fps)); hop = sr // a.fps
rms = np.array([np.sqrt(np.mean(y[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
db = 20 * np.log10(rms); lo, hi = np.percentile(db, 30), np.percentile(db, 98)
lvl = ((db - lo) / (hi - lo + 1e-9)).clip(0, 1)

def follow(x):  # attack/release envelope so mouths snap open and ease shut
    out = np.zeros_like(x); v = 0.0
    ka, kr = 1 - np.exp(-1 / (a.fps * a.attack)), 1 - np.exp(-1 / (a.fps * a.release))
    for i, s in enumerate(x):
        v += (s - v) * (ka if s > v else kr); out[i] = v
    return out

res = {"fps": a.fps, "all": np.round(follow(lvl), 3).tolist()}
speakers = sorted({l.get("speaker", "") for l in al["lines"]})
for spk in speakers:
    gate = np.zeros(n)
    for l in al["lines"]:
        if l.get("speaker", "") != spk: continue
        for w in l["words"]:
            gate[int(w["start"] * a.fps):int(np.ceil(w["end"] * a.fps)) + 1] = 1
    res[spk or "main"] = np.round(follow(lvl * gate[:n]), 3).tolist()
json.dump(res, open(a.out, "w"))
print(f"mouth curves for {', '.join(s or 'main' for s in speakers)} ({n} frames) -> {a.out}")
