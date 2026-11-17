#!/usr/bin/env python3
"""Paint out a small watermark (Gemini / Flow sparkle, a logo) from an image or every frame of a folder.

    python3 paint_out.py IN(image|frames_dir) OUT(image|dir) [--box x,y,w,h | --corner br] [--size 0.07] [--from REF_IMAGE]

--corner br|bl|tr|tl picks a square of --size (fraction of the short side) in that corner (Gemini puts its
sparkle bottom-right). --box sets it exactly in pixels. With --from, the area is copied from REF_IMAGE
(e.g. the real photo under a Gemini sketch); otherwise it is inpainted (OpenCV Telea).
Colours are never changed outside the box.
"""
import argparse, glob, os
import cv2, numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--box"); ap.add_argument("--corner", default="br")
ap.add_argument("--size", type=float, default=0.07); ap.add_argument("--from", dest="ref")
a = ap.parse_args()

def box_for(h, w):
    if a.box: return [int(v) for v in a.box.split(",")]
    s = int(min(h, w) * a.size); m = int(s * 0.25)
    x = w - s - m if "r" in a.corner else m; y = h - s - m if "b" in a.corner else m
    return x, y, s + m, s + m

def fix(img):
    h, w = img.shape[:2]; x, y, bw, bh = box_for(h, w)
    if a.ref:
        ref = cv2.resize(cv2.imread(a.ref), (w, h)); img[y:y + bh, x:x + bw] = ref[y:y + bh, x:x + bw]; return img
    mask = np.zeros((h, w), np.uint8); mask[y:y + bh, x:x + bw] = 255
    return cv2.inpaint(img, mask, 9, cv2.INPAINT_TELEA)

if os.path.isdir(a.inp):
    os.makedirs(a.out, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(a.inp, "*.*"))):
        cv2.imwrite(os.path.join(a.out, os.path.basename(f)), fix(cv2.imread(f)), [cv2.IMWRITE_JPEG_QUALITY, 95])
else:
    cv2.imwrite(a.out, fix(cv2.imread(a.inp)))
print("painted out ->", a.out)
