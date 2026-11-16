#!/usr/bin/env python3
"""Flicker edit: swap the model shot and the empty shot every quarter beat, in Python + numpy -> ffmpeg.

    python3 flicker.py MODEL EMPTY SONG BEATS.json OUT.mp4 [--stills DIR] [--force]
           [--swap quarter|half|beat] [--start 0] [--face x,y] [--horizon y]

MODEL/EMPTY: photos or videos from the same tripod spot (videos: frame at the same output time, looped).
Same 9:16 crop box for both. Warm sunset grade (contrast, warm tint, vignette, grain) applied identically.
Each model appearance: +3 % zoom toward the face with ease-out over that swap slot, on top of a slow 8 %
push-in over the whole edit, both anchored on the face. Soft white flash on the strongest beats (hits).
Opens on one beat of the model, ends on the last beat with only the empty shot.
--face / --horizon override the automatic face detection (OpenCV) and horizon (strongest horizontal edge row).
"""
import argparse, json, os, subprocess, sys
import cv2, numpy as np

ap = argparse.ArgumentParser()
for x in ("model", "empty", "song", "beats", "out"): ap.add_argument(x)
ap.add_argument("--stills"); ap.add_argument("--force", action="store_true"); ap.add_argument("--swap", default="quarter")
ap.add_argument("--start", type=float, default=0.0); ap.add_argument("--face"); ap.add_argument("--horizon", type=float)
ap.add_argument("--fps", type=int, default=30)
a = ap.parse_args()
W, H, FPS = 1080, 1920, a.fps
B = json.load(open(a.beats)); grid = {"quarter": B["quarter_beats"], "half": B["half_beats"], "beat": B["beats"]}[a.swap]
grid = [t for t in grid if t >= a.start]; beats = [t for t in B["beats"] if t >= a.start]
hits = set(round(t, 2) for t in B.get("hits", []))
end = beats[-1] if beats else B["duration"]

def reader(p):
    if p.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        im = cv2.imread(p); return lambda t: im, im.shape
    cap = cv2.VideoCapture(p); n = int(cap.get(7)); fps = cap.get(5) or 30; ok, f0 = cap.read()
    def get(t):
        cap.set(1, int(t * fps) % max(n, 1)); ok, f = cap.read(); return f if ok else f0
    return get, f0.shape
gm, shp = reader(a.model); ge, _ = reader(a.empty)
h0, w0 = shp[:2]
first = gm(0)
if a.face: fx, fy = map(float, a.face.split(","))
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video-core", "scripts")); import vision
    f = vision.faces(first)
    if f: x, y, w, h, _ = f[0]; fx, fy = x + w / 2, y + h / 2
    else:  # no face: use where the two shots differ most (the model)
        d = cv2.absdiff(first, ge(0)).max(2); ys, xs = np.where(d > 40); fx, fy = (xs.mean(), ys.mean()) if len(xs) else (w0 / 2, h0 / 2)
if a.horizon is None:
    g = cv2.cvtColor(ge(0), cv2.COLOR_BGR2GRAY).astype(np.float32); edge = np.abs(np.diff(cv2.GaussianBlur(g, (0, 0), 3), axis=0)).mean(1)
    hz = float(np.argmax(edge[int(h0 * 0.2):int(h0 * 0.8)]) + int(h0 * 0.2))
else: hz = a.horizon
# 9:16 crop box centred on the face horizontally; horizon kept at the same height for both shots (same box)
ch = h0; cw = int(ch * 9 / 16)
if cw > w0: cw = w0; ch = int(cw * 16 / 9)
cx0 = int(np.clip(fx - cw / 2, 0, w0 - cw)); cy0 = int(np.clip(hz - ch * 0.42, 0, h0 - ch))
ffx, ffy = (fx - cx0) / cw * W, (fy - cy0) / ch * H  # face position in output pixels
yy, xx = np.mgrid[0:H, 0:W]; vig = (1 - 0.45 * (((xx - W / 2) / (W / 1.3)) ** 2 + ((yy - H / 2) / (H / 1.3)) ** 2)).clip(0.45, 1)[..., None].astype(np.float32)
rng = np.random.default_rng(7); grains = [rng.normal(0, 3.5, (H, W, 1)).astype(np.float32) for _ in range(4)]
def grade(img, k):
    f = img.astype(np.float32)
    f = (f - 128) * 1.08 + 128                     # a little contrast
    f[..., 2] *= 1.07; f[..., 1] *= 1.01; f[..., 0] *= 0.90   # warm tint (BGR)
    f = f * vig + grains[k % 4]
    return np.clip(f, 0, 255).astype(np.uint8)
def frame(t, k):
    slot = max(0, np.searchsorted(grid, t, side="right") - 1)
    model_on = (slot % 2 == 0) and t < end - 1e-3 and (t < grid[-1] if grid else True)
    if t >= (beats[-2] if len(beats) > 1 else end): model_on = False   # last beat: empty only
    src = (gm if model_on else ge)(t)
    crop = cv2.resize(src[cy0:cy0 + ch, cx0:cx0 + cw], (W, H), interpolation=cv2.INTER_AREA)
    z = 1 + 0.08 * (t - a.start) / max(end - a.start, 1e-3)
    if model_on and slot < len(grid):
        s0 = grid[slot]; s1 = grid[slot + 1] if slot + 1 < len(grid) else s0 + 0.12
        p = min(1, (t - s0) / (s1 - s0)); z *= 1 + 0.03 * (1 - (1 - p) ** 3)
    M = np.float32([[z, 0, ffx * (1 - z)], [0, z, ffy * (1 - z)]])
    out = grade(cv2.warpAffine(crop, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), k)
    fl = max([np.exp(-(t - b) / 0.05) for b in hits if 0 <= t - b < 0.15] + [0])
    if fl > 0.02: out = cv2.addWeighted(out, 1 - 0.35 * fl, np.full_like(out, 255), 0.35 * fl, 0)
    return out
if a.stills:
    os.makedirs(a.stills, exist_ok=True)
    for t in np.linspace(a.start + 0.05, end - 0.05, 8):
        cv2.imwrite(os.path.join(a.stills, f"still_{t:07.2f}.png"), frame(t, 0))
    print("stills ->", a.stills); sys.exit()
if os.path.exists(a.out) and not a.force: print(f"REFUSING: {a.out} exists. Ask the user, then re-run with --force."); sys.exit(3)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
n = int((end - a.start) * FPS)
ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-ss", str(a.start), "-t", str(end - a.start), "-i", a.song, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "256k", "-af", "afade=t=out:st=%.2f:d=0.4" % max(0, end - a.start - 0.4), "-shortest", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
for k in range(n): ff.stdin.write(frame(a.start + k / FPS, k).tobytes())
ff.stdin.close(); ff.wait(); print(f"wrote {a.out} ({n} frames)")
