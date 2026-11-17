#!/usr/bin/env python3
"""Retime a frame sequence with a piecewise time map, with optical-flow in-betweens for slow parts.

    python3 retime.py IN_FRAMES OUT_FRAMES --map "0:0,2.0:3.1,4.5:5.0" [--in-fps 24] [--out-fps 30] [--skip-start 0] [--skip-end 0]

--map pairs are OUTPUT_TIME:SOURCE_TIME (seconds). Between pairs, source time is linear, so an event at a
source time lands exactly on the output time you choose (a word, a bar). Fractional source frames are
synthesised with DIS optical flow (warp both neighbours, blend), not plain cross-fades, so slow motion is smooth.
--skip-start/--skip-end drop bad frames at the head/tail of a generated clip (reference sheet, jump cut).
Use --map "0:0,D:D*0.5" style maps for half-speed slow motion (beat-transition-edit).
"""
import argparse, glob, os
import cv2, numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--map", required=True)
ap.add_argument("--in-fps", type=float, default=24); ap.add_argument("--out-fps", type=float, default=30)
ap.add_argument("--skip-start", type=int, default=0); ap.add_argument("--skip-end", type=int, default=0)
a = ap.parse_args()
files = sorted(glob.glob(os.path.join(a.inp, "*.jpg")) + glob.glob(os.path.join(a.inp, "*.png")))
files = files[a.skip_start:len(files) - a.skip_end if a.skip_end else None]
pairs = sorted(tuple(map(float, p.split(":"))) for p in a.map.split(","))
outT, srcT = np.array([p[0] for p in pairs]), np.array([p[1] for p in pairs])
os.makedirs(a.out, exist_ok=True)
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
cache = {}
def load(i):
    i = int(np.clip(i, 0, len(files) - 1))
    if i not in cache:
        if len(cache) > 8: cache.pop(next(iter(cache)))
        cache[i] = cv2.imread(files[i])
    return cache[i]
def warp(img, flow, s):
    h, w = flow.shape[:2]; gx, gy = np.meshgrid(np.arange(w), np.arange(h))
    return cv2.remap(img, (gx + flow[..., 0] * s).astype(np.float32), (gy + flow[..., 1] * s).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
n = int(round(outT[-1] * a.out_fps))
for k in range(n):
    st = float(np.interp(k / a.out_fps, outT, srcT)) * a.in_fps
    i0 = int(np.floor(st)); f = st - i0
    A = load(i0)
    if f < 0.04 or i0 + 1 >= len(files): frame = A
    else:
        B = load(i0 + 1); ga, gb = cv2.cvtColor(A, cv2.COLOR_BGR2GRAY), cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)
        fab, fba = dis.calc(ga, gb, None), dis.calc(gb, ga, None)
        frame = cv2.addWeighted(warp(A, fba, f), 1 - f, warp(B, fab, 1 - f), f, 0)
    cv2.imwrite(os.path.join(a.out, f"{k + 1:06d}.jpg"), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
print(f"{n} frames -> {a.out}")
