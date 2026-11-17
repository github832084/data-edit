#!/usr/bin/env python3
"""Cut silences and filler words from a talking-head clip, using word timings from align.py.

  1) plan:   python3 tighten.py align.json edl.json [--max-gap 0.25] [--fillers "um,uh,matlab"] [--pad 0.06]
  2) apply:  python3 tighten.py --apply edl.json align.json align_cut.json

edl.json = {"keep": [[src_start, src_end], ...], "duration": out_seconds}. Plan prints the ffmpeg command
that cuts the clip (video + audio) with the same EDL, so frames, audio and captions all stay in sync.
--apply maps every word time from source time to output time, dropping cut words.
Show the user the cut list (what was removed) before rendering.
"""
import argparse, json, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("c", nargs="?")
ap.add_argument("--apply", action="store_true"); ap.add_argument("--max-gap", type=float, default=0.25)
ap.add_argument("--fillers", default="um,uh,umm,uhh,hmm,matlab,basically,like,toh"); ap.add_argument("--pad", type=float, default=0.06)
ap.add_argument("--src", default="in/clip.mp4")
a = ap.parse_args()

def norm(w): return re.sub(r"[^\w]", "", w.lower())

if not a.apply:
    al = json.load(open(a.a)); fill = {norm(f) for f in a.fillers.split(",") if f}
    words = [w for l in al["lines"] for w in l["words"]]
    keep, cut = [], []
    for w in words:
        if norm(w["w"]) in fill:
            cut.append(w["w"]); continue
        s, e = max(0, w["start"] - a.pad), w["end"] + a.pad
        if keep and s - keep[-1][1] <= a.max_gap:
            keep[-1][1] = max(keep[-1][1], e)
        else:
            keep.append([s, e])
    keep = [[round(s, 3), round(e, 3)] for s, e in keep]
    dur = sum(e - s for s, e in keep)
    json.dump({"keep": keep, "duration": round(dur, 3), "removed_fillers": cut}, open(a.b, "w"), indent=1)
    sel = "+".join(f"between(t,{s},{e})" for s, e in keep)
    print(f"{len(keep)} segments kept, {al['duration'] - dur:.1f}s removed, fillers cut: {cut}")
    print("cut the clip with:")
    print(f"ffmpeg -i {a.src} -vf \"select='{sel}',setpts=N/FRAME_RATE/TB\" -af \"aselect='{sel}',asetpts=N/SR/TB\" -c:v libx264 -crf 14 -c:a aac -b:a 256k in/clip_tight.mp4")
else:
    edl = json.load(open(a.a)); al = json.load(open(a.b))
    def m(t):
        acc = 0.0
        for s, e in edl["keep"]:
            if t < s: return None
            if t <= e: return round(acc + (t - s), 3)
            acc += e - s
        return None
    lines = []
    for l in al["lines"]:
        ws = []
        for w in l["words"]:
            s, e = m(w["start"]), m(w["end"])
            if s is None or e is None: continue
            ws.append({**w, "start": s, "end": e})
        if ws: lines.append({**l, "words": ws, "start": ws[0]["start"], "end": ws[-1]["end"]})
    json.dump({**al, "lines": lines, "duration": edl["duration"]}, open(a.c, "w"), ensure_ascii=False, indent=1)
    print(f"mapped {sum(len(l['words']) for l in lines)} words -> {a.c}")
