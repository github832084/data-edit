#!/usr/bin/env python3
"""Camera track of the background (people masked out), so words can be locked to the world.

    python3 track_bg.py FRAMES_DIR MATTES_DIR OUT.json [--point x,y]

For each frame, estimates the similarity transform (tx, ty, scale, rot) that maps frame 1's background to
that frame, from ORB features outside the person matte (RANSAC), chained frame to frame.
OUT.json: {"frames":[{"a","b","tx","ty"}...]} where a world point (x,y) in frame 1 lands at
  x' = a*x - b*y + tx,  y' = b*x + a*y + ty
With --point x,y it also writes "point":[[x',y'],...] for that frame-1 point (use it to lock a TV or a face
across a join).
"""
import argparse, glob, json, os
import cv2, numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("frames"); ap.add_argument("mattes"); ap.add_argument("out"); ap.add_argument("--point")
a = ap.parse_args()
fs = sorted(glob.glob(os.path.join(a.frames, "*.jpg")) + glob.glob(os.path.join(a.frames, "*.png")))
ms = sorted(glob.glob(os.path.join(a.mattes, "*.png")))
orb = cv2.ORB_create(3000); bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
def feats(i):
    g = cv2.cvtColor(cv2.imread(fs[i]), cv2.COLOR_BGR2GRAY)
    mask = 255 - cv2.dilate(cv2.imread(ms[i], 0), np.ones((25, 25), np.uint8)) if i < len(ms) else None
    return orb.detectAndCompute(g, mask)
acc = np.eye(3); out = [{"a": 1.0, "b": 0.0, "tx": 0.0, "ty": 0.0}]
kp0, d0 = feats(0)
for i in range(1, len(fs)):
    kp1, d1 = feats(i); T = np.eye(3)
    if d0 is not None and d1 is not None:
        m = sorted(bf.match(d0, d1), key=lambda x: x.distance)[:600]
        if len(m) >= 8:
            p0 = np.float32([kp0[x.queryIdx].pt for x in m]); p1 = np.float32([kp1[x.trainIdx].pt for x in m])
            M, _ = cv2.estimateAffinePartial2D(p0, p1, method=cv2.RANSAC, ransacReprojThreshold=2.0)
            if M is not None: T = np.vstack([M, [0, 0, 1]])
    acc = T @ acc; out.append({"a": float(acc[0, 0]), "b": float(acc[1, 0]), "tx": float(acc[0, 2]), "ty": float(acc[1, 2])})
    kp0, d0 = kp1, d1
res = {"frames": out}
if a.point:
    x, y = map(float, a.point.split(",")); res["point"] = [[f["a"] * x - f["b"] * y + f["tx"], f["b"] * x + f["a"] * y + f["ty"]] for f in out]
json.dump(res, open(a.out, "w")); print(f"tracked {len(out)} frames -> {a.out}")
