#!/usr/bin/env python3
"""Beats, bars, kicks, hits and loudness for a song (librosa).

    python3 beats.py SONG OUT.json [--fps 30] [--bpm-hint 92] [--hits-only-from VOICE]

OUT.json: {"tempo","beats":[s],"downbeats":[s],"bars":[[s,e]],"half_beats","quarter_beats",
           "kicks":[s],"hits":[s],"onsets":[s],"rms":[per video frame 0..1],"low":[per frame 0..1]}
- kicks: onsets of the 20-150 Hz band (kick drum). hits: the strongest onsets (music hits / bells / barks).
- Beat trackers can be off by a few BPM or by half/double: check the tempo by ear (play a click track with
  click.sh) and pass --bpm-hint when it is wrong.
"""
import argparse, json
import numpy as np, librosa

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("out"); ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--bpm-hint", type=float); ap.add_argument("--hit-percentile", type=float, default=92)
a = ap.parse_args()

y, sr = librosa.load(a.audio, sr=22050, mono=True)
hop = 512
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
kw = {"start_bpm": a.bpm_hint, "tightness": 400} if a.bpm_hint else {}
tempo, bf = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=hop, **kw)
tempo = float(np.atleast_1d(tempo)[0])
beats = librosa.frames_to_time(bf, sr=sr, hop_length=hop).tolist()

# downbeat guess: the beat phase (0-3) with the most low-end energy
S = np.abs(librosa.stft(y, hop_length=hop)); freqs = librosa.fft_frequencies(sr=sr)
low = S[(freqs >= 20) & (freqs <= 150)].sum(0)
phase = int(np.argmax([low[bf[p::4]].sum() if len(bf[p::4]) else 0 for p in range(4)])) if len(bf) >= 8 else 0
downbeats = beats[phase::4]
bars = [[downbeats[i], downbeats[i + 1]] for i in range(len(downbeats) - 1)]
half = sorted(beats + [(beats[i] + beats[i + 1]) / 2 for i in range(len(beats) - 1)])
quarter = sorted(half + [(half[i] + half[i + 1]) / 2 for i in range(len(half) - 1)])

low_env = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[(freqs >= 20) & (freqs <= 150)]), sr=sr, hop_length=hop)
kicks = librosa.frames_to_time(librosa.onset.onset_detect(onset_envelope=low_env, sr=sr, hop_length=hop, backtrack=False, delta=0.25), sr=sr, hop_length=hop).tolist()
on = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, hop_length=hop)
onsets = librosa.frames_to_time(on, sr=sr, hop_length=hop).tolist()
thr = np.percentile(oenv[on], a.hit_percentile) if len(on) else 0
hits = [t for t, f in zip(onsets, on) if oenv[f] >= thr]

dur = len(y) / sr; n = int(np.ceil(dur * a.fps))
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
ft = np.arange(n) / a.fps
norm = lambda v: (v / (np.percentile(v, 99) + 1e-9)).clip(0, 1)
out = {"duration": dur, "tempo": round(tempo, 2), "beats": beats, "downbeats": downbeats, "bars": bars, "half_beats": half, "quarter_beats": quarter,
       "kicks": kicks, "hits": hits, "onsets": onsets, "fps": a.fps,
       "rms": np.round(norm(np.interp(ft, times, rms)), 3).tolist(), "low": np.round(norm(np.interp(ft, librosa.frames_to_time(np.arange(len(low)), sr=sr, hop_length=hop), low)), 3).tolist()}
json.dump(out, open(a.out, "w"))
print(f"tempo {tempo:.1f} bpm, {len(beats)} beats, {len(kicks)} kicks, {len(hits)} hits -> {a.out}")
