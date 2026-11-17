#!/usr/bin/env python3
"""Transcribe with Whisper and write an editable text file, one line per row.

    python3 transcribe.py AUDIO OUTDIR [--lang hi] [--model large-v3] [--speakers]

Writes OUTDIR/transcript.txt (one segment per row; Devanagari for --lang hi) and OUTDIR/whisper.json
(segments + rough word times). Then STOP and show transcript.txt to the user so they can fix wrong words.
After that, run align.py on the corrected transcript.txt: Whisper's word times are only rough, and the
skills never use them for final timing.

--speakers: prefix each row with "S1|". Whisper has no speaker labels, so edit the labels with the user
(or decide them from the video: who holds the mic, whose mouth moves).
"""
import argparse, json, os, re

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("outdir")
ap.add_argument("--lang", default=None); ap.add_argument("--model", default=os.environ.get("WHISPER_MODEL", "large-v3"))
ap.add_argument("--speakers", action="store_true")
a = ap.parse_args()
os.makedirs(a.outdir, exist_ok=True)

import whisper
m = whisper.load_model(a.model)
prompt = "यह हिंदी में है।" if a.lang == "hi" else None  # nudges Whisper to Devanagari instead of Urdu/roman script
r = m.transcribe(a.audio, language=a.lang, word_timestamps=True, initial_prompt=prompt, condition_on_previous_text=False)
json.dump(r, open(os.path.join(a.outdir, "whisper.json"), "w"), ensure_ascii=False, indent=1)
with open(os.path.join(a.outdir, "transcript.txt"), "w", encoding="utf-8") as f:
    f.write("# One line per row. Fix any wrong words, then run align.py on this file.\n")
    for s in r["segments"]:
        t = re.sub(r"\s+", " ", s["text"]).strip()
        if t:
            f.write(("S1|" if a.speakers else "") + t + "\n")
print(f"{len(r['segments'])} segments, language={r.get('language')} -> {a.outdir}/transcript.txt")
