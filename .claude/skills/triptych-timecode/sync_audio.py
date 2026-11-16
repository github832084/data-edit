#!/usr/bin/env python3
"""Sync clips by their audio (cross-correlation of loudness envelopes).

    python3 sync_audio.py A.mp4 B.mp4 C.mp4 OUT.json

OUT.json: {"offsets": {"A.mp4": 0.0, "B.mp4": 1.234, ...}, "common_duration": s}
offset = seconds to skip at the start of that clip so all clips line up with the latest-starting one.
Use them as the START of frames.sh for each clip.
"""
import json, subprocess, sys
import numpy as np

*clips, out = sys.argv[1:]
SR = 8000; HOP = 80  # 10 ms envelope

def env(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    y = np.frombuffer(raw, np.float32); n = len(y) // HOP
    e = np.sqrt((y[:n * HOP].reshape(n, HOP) ** 2).mean(1) + 1e-9); e = np.log(e); e -= e.mean(); return e / (e.std() + 1e-9), len(y) / SR

envs = [env(c) for c in clips]
ref = envs[0][0]; lags = [0.0]
for e, _ in envs[1:]:
    n = len(ref) + len(e); f = np.fft.irfft(np.fft.rfft(ref, n) * np.conj(np.fft.rfft(e, n)), n)
    lag = int(np.argmax(f)); lag = lag - n if lag > n // 2 else lag
    lags.append(lag * HOP / SR)   # clip i starts `lag` seconds after clip 0's start
offsets = {c: round(max(lags) - l, 3) for c, l in zip(clips, lags)}  # skip so all align to the latest start
common = min(d - offsets[c] for c, (_, d) in zip(clips, envs))
json.dump({"offsets": offsets, "common_duration": round(common, 3)}, open(out, "w"), indent=1)
print(json.dumps(offsets), f"common {common:.2f}s")
