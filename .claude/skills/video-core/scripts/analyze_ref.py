#!/usr/bin/env python3
"""Analyse a reference reel or a source clip: cuts, shot lengths, and 2 fps contact sheets.

    python3 analyze_ref.py REEL.mp4 OUTDIR [--threshold 0.3] [--fps 2] [--beats beats.json]

Writes OUTDIR/cuts.json {"cuts":[s], "shots":[[start,end,len]], "median_shot":s, "cuts_per_sec"},
OUTDIR/frames_2fps/*.jpg and OUTDIR/sheet_*.jpg (24 frames per sheet). Look at the sheets yourself and
write down fonts, colours, transitions, camera moves and the colour grade. With --beats, each cut is
matched to the nearest beat / half beat / quarter beat so you can copy the cutting grid.
Also used for frame-difference flicker rates (flicker-edit) and for scene changes in source clips.
"""
import argparse, json, os, re, subprocess, glob
ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("outdir"); ap.add_argument("--threshold", type=float, default=0.3)
ap.add_argument("--fps", type=float, default=2); ap.add_argument("--beats")
a = ap.parse_args(); os.makedirs(a.outdir, exist_ok=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video], capture_output=True, text=True).stdout)
log = subprocess.run(["ffmpeg", "-v", "info", "-i", a.video, "-vf", f"select='gt(scene,{a.threshold})',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]
edges = [0.0] + cuts + [dur]; shots = [[round(edges[i], 3), round(edges[i + 1], 3), round(edges[i + 1] - edges[i], 3)] for i in range(len(edges) - 1)]
res = {"duration": dur, "cuts": cuts, "shots": shots, "median_shot": sorted(s[2] for s in shots)[len(shots) // 2], "cuts_per_sec": round(len(cuts) / dur, 3)}
if a.beats:
    b = json.load(open(a.beats)); grid = {"beat": b["beats"], "half": b["half_beats"], "quarter": b["quarter_beats"]}
    res["cut_grid"] = [{"t": c, **{k: round(min(abs(c - x) for x in v), 3) for k, v in grid.items() if v}} for c in cuts]
json.dump(res, open(os.path.join(a.outdir, "cuts.json"), "w"), indent=1)
fd = os.path.join(a.outdir, "frames_2fps"); os.makedirs(fd, exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", f"fps={a.fps},scale=480:-2", "-q:v", "3", os.path.join(fd, "%05d.jpg")], check=True)
fr = sorted(glob.glob(os.path.join(fd, "*.jpg")))
here = os.path.dirname(os.path.abspath(__file__))
for i in range(0, len(fr), 24):
    batch = fr[i:i + 24]
    named = []
    for j, f in enumerate(batch):
        t = (i + j) / a.fps; nf = os.path.join(fd, f"t_{t:08.2f}.jpg"); os.replace(f, nf); named.append(nf)
    subprocess.run(["python3", os.path.join(here, "contact_sheet.py"), os.path.join(a.outdir, f"sheet_{i // 24 + 1:02d}.jpg"), *named], check=True)
print(f"{len(cuts)} cuts, median shot {res['median_shot']:.2f}s, {res['cuts_per_sec']} cuts/s -> {a.outdir}")
