#!/usr/bin/env python3
"""Line a Gemini sketch up with the original photo and keep the sketch only where the people changed.

    python3 diff_mask.py PHOTO SKETCH OUT_DIR [--thresh 38] [--wm 0.07]

Writes OUT/photo.png, OUT/sketch.png (aligned to the photo, background replaced by the real photo),
OUT/people_mask.png (white = where Gemini redrew the people) and OUT/preview.jpg.
- Alignment: ECC affine on grayscale (Gemini often shifts/scales a few pixels).
- Mask: colour difference, cleaned (open/close), largest blobs kept, then feathered.
- Watermark: Gemini's sparkle in the bottom-right corner is replaced with the photo there.
"""
import argparse, os
import cv2, numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("photo"); ap.add_argument("sketch"); ap.add_argument("out")
ap.add_argument("--thresh", type=float, default=38); ap.add_argument("--wm", type=float, default=0.07)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
P = cv2.imread(a.photo); S = cv2.imread(a.sketch); h, w = P.shape[:2]
S = cv2.resize(S, (w, h), interpolation=cv2.INTER_AREA)
gp, gs = [cv2.GaussianBlur(cv2.cvtColor(x, cv2.COLOR_BGR2GRAY), (0, 0), 3).astype(np.float32) / 255 for x in (P, S)]
M = np.eye(2, 3, dtype=np.float32)
try:
    _, M = cv2.findTransformECC(gp, gs, M, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
    S = cv2.warpAffine(S, M, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
except cv2.error:
    print("warn: ECC alignment failed, using unaligned sketch")
d = cv2.absdiff(cv2.GaussianBlur(P, (0, 0), 2), cv2.GaussianBlur(S, (0, 0), 2)).astype(np.float32).max(2)
m = (d > a.thresh).astype(np.uint8) * 255
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] > 0.004 * w * h: keep[lab == i] = 255
s = int(min(h, w) * a.wm); keep[h - s * 5 // 4:, w - s * 5 // 4:] = 0   # never use the watermark corner
keep = cv2.dilate(keep, np.ones((9, 9), np.uint8)); soft = cv2.GaussianBlur(keep, (0, 0), 4).astype(np.float32)[..., None] / 255
out = (S * soft + P * (1 - soft)).astype(np.uint8)
cv2.imwrite(os.path.join(a.out, "photo.png"), P); cv2.imwrite(os.path.join(a.out, "sketch.png"), out); cv2.imwrite(os.path.join(a.out, "people_mask.png"), keep)
cv2.imwrite(os.path.join(a.out, "preview.jpg"), np.hstack([cv2.resize(x, (w // 3, h // 3)) for x in (P, out, cv2.cvtColor(keep, cv2.COLOR_GRAY2BGR))]))
print(f"mask covers {keep.mean() / 2.55:.1f}% of the frame -> {a.out} (check preview.jpg)")
