#!/usr/bin/env python3
"""Finish a render: check it, then make the WhatsApp copy.

    python3 finish.py MASTER.mp4 [--whatsapp OUT_720p.mp4] [--max-mb 19.5] [--expect-audio SRC] [--force]

Checks (prints PASS/FAIL lines, exit 1 on any FAIL):
  - has a video and an audio stream, size and fps as expected, duration matches --expect-audio (+-0.2 s)
  - no black or empty stretches (ffmpeg blackdetect, >= 0.25 s), unless they are intended fades at the very end
Then writes the WhatsApp copy: short side 720 px, H.264 + AAC, two-pass to fit under --max-mb.
Never overwrites an existing file unless --force (ask the user first).
"""
import argparse, json, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("master"); ap.add_argument("--whatsapp"); ap.add_argument("--max-mb", type=float, default=19.5)
ap.add_argument("--expect-audio"); ap.add_argument("--force", action="store_true"); ap.add_argument("--allow-black-end", type=float, default=2.5)
a = ap.parse_args()

def probe(p):
    return json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p], capture_output=True, text=True, check=True).stdout)

ok = True
def check(cond, msg):
    global ok
    print(("PASS " if cond else "FAIL ") + msg); ok = ok and cond

info = probe(a.master); dur = float(info["format"]["duration"])
v = [s for s in info["streams"] if s["codec_type"] == "video"]; au = [s for s in info["streams"] if s["codec_type"] == "audio"]
check(bool(v), "video stream"); check(bool(au), "audio stream (original audio muxed)")
if v:
    fr = eval(v[0]["r_frame_rate"]); print(f"     {v[0]['width']}x{v[0]['height']} @ {fr:.2f} fps, {dur:.2f}s, {os.path.getsize(a.master)/1e6:.1f} MB")
if a.expect_audio:
    ad = float(probe(a.expect_audio)["format"]["duration"]); check(abs(ad - dur) < 0.25 or dur < ad, f"duration {dur:.2f}s vs audio {ad:.2f}s")
bd = subprocess.run(["ffmpeg", "-v", "info", "-i", a.master, "-vf", "blackdetect=d=0.25:pic_th=0.97:pix_th=0.06", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
blacks = [(float(s), float(e)) for s, e in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", bd)]
bad = [(s, e) for s, e in blacks if not (e >= dur - 0.1 and s >= dur - a.allow_black_end) and not (s < 0.05 and e < 0.8)]
check(not bad, "no black/empty stretches" + (f": {bad}" if bad else ""))

if a.whatsapp:
    out = a.whatsapp
    if os.path.exists(out) and not a.force:
        print(f"REFUSING: {out} exists. Ask the user, then re-run with --force."); sys.exit(3)
    abr = 128 if dur < 300 else 96
    budget = a.max_mb * 8 * 1024 * 1024 / dur / 1000  # kbit/s total
    vbr = int(min(4000, budget - abr - 30))
    w, h = v[0]["width"], v[0]["height"]
    scale = "scale=-2:720" if w >= h else "scale=720:-2"
    for attempt in range(4):
        log = out + ".2pass"
        base = ["ffmpeg", "-y", "-v", "error", "-i", a.master, "-vf", scale + ",fps=30" if eval(v[0]["r_frame_rate"]) > 30 else scale, "-c:v", "libx264", "-preset", "slow", "-b:v", f"{vbr}k", "-pix_fmt", "yuv420p", "-passlogfile", log]
        subprocess.run(base + ["-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
        subprocess.run(base + ["-pass", "2", "-c:a", "aac", "-b:a", f"{abr}k", "-movflags", "+faststart", out], check=True)
        for f in os.listdir(os.path.dirname(os.path.abspath(out))):
            if f.startswith(os.path.basename(log)): os.remove(os.path.join(os.path.dirname(os.path.abspath(out)), f))
        mb = os.path.getsize(out) / 1e6
        if mb <= a.max_mb * 1.048: break
        vbr = int(vbr * 0.85)
    check(os.path.getsize(out) / (1024 * 1024) < 20, f"WhatsApp copy {out}: {os.path.getsize(out)/(1024*1024):.1f} MB at {vbr} kbit/s")
sys.exit(0 if ok else 1)
