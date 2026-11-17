"""Shared vision helpers (MediaPipe Tasks): face boxes and person masks.

    import sys; sys.path.insert(0, ".claude/skills/video-core/scripts"); import vision
    vision.faces(bgr_image)  -> [(x, y, w, h, score), ...] largest first
    vision.person_mask(rgb_image) -> uint8 HxW mask (255 = person)

Models download once to ~/.cache/video-core/ from storage.googleapis.com. Works with OpenCV 5 (which no
longer ships Haar cascades) and MediaPipe >= 0.10 Tasks API (the old mp.solutions API is gone).
"""
import atexit, os, urllib.request
import numpy as np
os.environ.setdefault("GLOG_minloglevel", "2"); os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

def _close_all():  # close detectors before interpreter shutdown (MediaPipe's own __del__ fails late)
    for d in (_det, _seg):
        for v in list(d.values()):
            try: v.close()
            except Exception: pass
        d.clear()
atexit.register(_close_all)

CACHE = os.path.expanduser("~/.cache/video-core")
URLS = {
    "face": "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite",
    "face_full": "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_full_range/float16/latest/blaze_face_full_range.tflite",
    "selfie": "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite",
    "multiclass": "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite",
}

def model(name):
    os.makedirs(CACHE, exist_ok=True); p = os.path.join(CACHE, os.path.basename(URLS[name]))
    if not os.path.exists(p):
        tmp = p + ".part"; urllib.request.urlretrieve(URLS[name], tmp); os.replace(tmp, p)
    return p

_det = {}
def faces(bgr, min_score=0.5):
    import cv2, mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision as mv
    if "face" not in _det:
        _det["face"] = mv.FaceDetector.create_from_options(mv.FaceDetectorOptions(base_options=mpt.BaseOptions(model_asset_path=model("face_full")), min_detection_confidence=min_score))
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB) if bgr.ndim == 3 else cv2.cvtColor(bgr, cv2.COLOR_GRAY2RGB)
    r = _det["face"].detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    out = [(d.bounding_box.origin_x, d.bounding_box.origin_y, d.bounding_box.width, d.bounding_box.height, d.categories[0].score) for d in r.detections]
    return sorted(out, key=lambda f: -f[2] * f[3])

_seg = {}
def person_mask(rgb):
    import mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision as mv
    if "seg" not in _seg:
        _seg["seg"] = mv.ImageSegmenter.create_from_options(mv.ImageSegmenterOptions(base_options=mpt.BaseOptions(model_asset_path=model("selfie")), output_confidence_masks=True))
    r = _seg["seg"].segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    m = r.confidence_masks[-1].numpy_view()  # selfie_segmenter: single "person" confidence mask
    m = m[..., 0] if m.ndim == 3 else m
    return (np.clip(m, 0, 1) * 255).astype(np.uint8)
