#!/usr/bin/env python3
"""Track a person on every frame for doodle edits (MediaPipe).

    python3 track_body.py FRAMES_DIR OUT_DIR [--smooth 3]

Writes:
  OUT/masks_person/000001.png  person mask (white = person)
  OUT/masks_hair/…, OUT/masks_clothes/…, OUT/masks_skin/…   (selfie multiclass segmenter)
  OUT/landmarks.json  per frame: {"face": [[x,y],...468] | null, "face_box": [x0,y0,x1,y1], "face_w": px,
                                   "roll": rad, "pose": {"l_wrist":[x,y,vis], "r_wrist", "l_elbow", "r_elbow", "l_knee", "r_knee", ...}}
Points are in pixels and smoothed over +-N frames so doodles don't jitter.
Needs the MediaPipe Tasks models; they are downloaded once into OUT/../.mp_models (storage.googleapis.com).
"""
import argparse, glob, json, os, urllib.request
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser(); ap.add_argument("frames"); ap.add_argument("out"); ap.add_argument("--smooth", type=int, default=3)
a = ap.parse_args()
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

MODELS = {
 "seg": "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite",
 "face": "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task",
 "pose": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task",
}
mdir = os.path.join(os.path.dirname(os.path.abspath(a.out)), ".mp_models"); os.makedirs(mdir, exist_ok=True)
path = {}
for k, u in MODELS.items():
    path[k] = os.path.join(mdir, os.path.basename(u))
    if not os.path.exists(path[k]): urllib.request.urlretrieve(u, path[k])

seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=mpt.BaseOptions(model_asset_path=path["seg"]), output_category_mask=True, running_mode=vision.RunningMode.VIDEO))
face = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path=path["face"]), num_faces=1, running_mode=vision.RunningMode.VIDEO))
pose = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path=path["pose"]), num_poses=1, running_mode=vision.RunningMode.VIDEO))
# multiclass categories: 0 background, 1 hair, 2 body-skin, 3 face-skin, 4 clothes, 5 others(accessories)
for d in ("person", "hair", "clothes", "skin"): os.makedirs(os.path.join(a.out, f"masks_{d}"), exist_ok=True)
POSE = {"nose": 0, "l_shoulder": 11, "r_shoulder": 12, "l_elbow": 13, "r_elbow": 14, "l_wrist": 15, "r_wrist": 16, "l_hip": 23, "r_hip": 24, "l_knee": 25, "r_knee": 26, "l_ankle": 27, "r_ankle": 28}
files = sorted(glob.glob(os.path.join(a.frames, "*.jpg")) + glob.glob(os.path.join(a.frames, "*.png")))
raw = []
for i, f in enumerate(files):
    im = np.array(Image.open(f).convert("RGB")); h, w = im.shape[:2]; ts = int(i * 1000 / 30)
    mi = mp.Image(image_format=mp.ImageFormat.SRGB, data=im)
    cat = seg.segment_for_video(mi, ts).category_mask.numpy_view()
    name = f"{i + 1:06d}.png"
    for d, cls in (("person", (1, 2, 3, 4, 5)), ("hair", (1,)), ("clothes", (4,)), ("skin", (2, 3))):
        Image.fromarray((np.isin(cat, cls) * 255).astype(np.uint8)).resize((w, h)).save(os.path.join(a.out, f"masks_{d}", name))
    fr = face.detect_for_video(mi, ts); pr = pose.detect_for_video(mi, ts)
    rec = {"face": None, "pose": None}
    if fr.face_landmarks:
        pts = np.array([[p.x * w, p.y * h] for p in fr.face_landmarks[0]]); rec["face"] = pts
    if pr.pose_landmarks:
        lm = pr.pose_landmarks[0]; rec["pose"] = {k: np.array([lm[j].x * w, lm[j].y * h, lm[j].visibility]) for k, j in POSE.items()}
    raw.append(rec)

def smooth(get, i):
    vals = [get(raw[j]) for j in range(max(0, i - a.smooth), min(len(raw), i + a.smooth + 1))]
    vals = [v for v in vals if v is not None]
    return np.mean(vals, 0) if vals else None
out = []
for i in range(len(raw)):
    fpts = smooth(lambda r: r["face"], i); rec = {"face": None, "face_box": None, "face_w": None, "roll": None, "pose": None}
    if fpts is not None and raw[i]["face"] is not None:
        x0, y0 = fpts.min(0); x1, y1 = fpts.max(0); le, re_ = fpts[33], fpts[263]
        rec.update(face=np.round(fpts, 1).tolist(), face_box=[round(x0), round(y0), round(x1), round(y1)], face_w=round(float(x1 - x0), 1),
                   roll=round(float(np.arctan2(re_[1] - le[1], re_[0] - le[0])), 4))
    if raw[i]["pose"] is not None:
        rec["pose"] = {k: np.round(smooth(lambda r, k=k: r["pose"][k] if r["pose"] else None, i), 2).tolist() for k in POSE}
    out.append(rec)
json.dump(out, open(os.path.join(a.out, "landmarks.json"), "w"))
print(f"tracked {len(out)} frames -> {a.out}")
