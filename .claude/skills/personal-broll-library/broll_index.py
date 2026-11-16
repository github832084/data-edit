#!/usr/bin/env python3
"""Index a B-roll folder so clips can be found in plain English.

    python3 broll_index.py FOLDER [--every 1.5] [--force]

For every video in FOLDER (recursive) that is new or changed (size + mtime), samples a frame every
--every seconds into FOLDER/.broll/<clip>/ and tiles a labelled sheet.jpg. Writes/updates
FOLDER/broll_index.json:
  {"clips": {"<relative path>": {"duration", "size", "mtime", "sheet", "fps", "w", "h",
                                 "description": "", "tags": [], "segments": []}}}
"description"/"tags"/"segments" are left empty for new clips: Claude looks at each new sheet.jpg and fills
them (place, action, mood, time of day, people, camera move; segments = [{"start","end","what"}]).
Prints the clips that still need a description. Removed files are dropped from the index.
"""
import argparse, json, os, subprocess, sys

VID = (".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi")
ap = argparse.ArgumentParser(); ap.add_argument("folder"); ap.add_argument("--every", type=float, default=1.5); ap.add_argument("--force", action="store_true")
a = ap.parse_args()
root = os.path.abspath(a.folder); idx_path = os.path.join(root, "broll_index.json")
idx = json.load(open(idx_path)) if os.path.exists(idx_path) else {"clips": {}}
sheet_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video-core", "scripts", "contact_sheet.py")
seen = set()
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if not d.startswith(".")]
    for f in sorted(fn):
        if not f.lower().endswith(VID): continue
        p = os.path.join(dp, f); rel = os.path.relpath(p, root); seen.add(rel); st = os.stat(p)
        old = idx["clips"].get(rel)
        if old and not a.force and old["size"] == st.st_size and abs(old["mtime"] - st.st_mtime) < 1: continue
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate:format=duration", "-of", "json", p], capture_output=True, text=True).stdout)
        dur = float(pr["format"]["duration"]); s = pr["streams"][0]
        out = os.path.join(root, ".broll", rel.replace(os.sep, "__")); os.makedirs(out, exist_ok=True)
        frames = []
        t = min(0.3, dur / 2)
        while t < dur:
            fp = os.path.join(out, f"t_{t:08.2f}.jpg")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", p, "-frames:v", "1", "-vf", "scale=480:-2", fp])
            if os.path.exists(fp): frames.append(fp)
            t += a.every
        sheet = os.path.join(out, "sheet.jpg")
        subprocess.run([sys.executable, sheet_py, sheet, *frames[:36]], check=True, capture_output=True)
        keep = {k: old[k] for k in ("description", "tags", "segments")} if old else {"description": "", "tags": [], "segments": []}
        idx["clips"][rel] = {"duration": round(dur, 2), "size": st.st_size, "mtime": st.st_mtime, "w": s["width"], "h": s["height"],
                             "fps": round(eval(s["r_frame_rate"]), 2), "sheet": os.path.relpath(sheet, root), **keep}
        if old: idx["clips"][rel]["description"] = ""  # changed file: describe again
for rel in list(idx["clips"]):
    if rel not in seen: del idx["clips"][rel]
json.dump(idx, open(idx_path, "w"), indent=1, ensure_ascii=False)
todo = [r for r, c in idx["clips"].items() if not c["description"]]
print(f"{len(idx['clips'])} clips indexed in {idx_path}; {len(todo)} need a description:")
for r in todo: print("  ", r, "->", idx["clips"][r]["sheet"])
