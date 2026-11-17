---
name: personal-short-form-reels
description: "Fast personal reel from a 9:16 talking-head clip: silences and fillers cut, a matching cutaway from the user's own B-roll folder every 2–3 s, 2–3 word highlighted captions, punch-in zooms on key words. Use when the user runs /personal-short-form-reels with a clip (and their B-roll folder)."
---

# Personal short-form reels

A fast personal reel with my own B-roll and word-by-word captions.

## Run it

`/personal-short-form-reels` with: a 9:16 talking-head clip, and the path to your B-roll folder.

## Every time it runs

- **Word-level timings for everything**: transcribe with `transcribe.py`, then time every word with `align.py` (MMS_FA) on the corrected text. Every graphic lands on the word it belongs to.
- **Safe zone**: keep all text out of the top 250 px and the bottom 420 px of the 1080×1920 frame (Instagram buttons and caption). Use `k.SAFE` / `k.inSafe()` in the scene.
- **Never re-grade or filter the face** unless this skill's steps say so: footage goes through `frames.sh`, which keeps the original colours, and is drawn untouched.
- **Render 1080×1920 at 30 fps with the original audio.**
- **Show 3 snapshots** (`render.cjs --stills` at three key moments) before the final render, and **ask before overwriting files** (`--force` only after a yes).

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Prep the clip: frames, transcript and word timings.
   ```bash
   bash .claude/skills/video-core/scripts/frames.sh in/clip.mp4 clips/me 30          # stops if the clip is HDR: convert it first (see /talking-head-edit)
   ffmpeg -i in/clip.mp4 -vn -ac 1 -ar 16000 audio.wav
   python3 .claude/skills/video-core/scripts/transcribe.py audio.wav . --lang hi --model large-v3   # Hinglish/Hindi; use --lang en for English
   ```
   Show `transcript.txt` to the user if any word looks wrong, then:
   ```bash
   python3 .claude/skills/video-core/scripts/align.py audio.wav transcript.txt align.json
   ```
2. Cut silences and filler words so the pacing stays tight.
   ```bash
   python3 .claude/skills/personal-short-form-reels/tighten.py align.json edl.json --max-gap 0.25 --fillers "um,uh,matlab,basically,like,toh"
   ```
   Then re-time: python3 .claude/skills/personal-short-form-reels/tighten.py --apply edl.json align.json align_cut.json, and cut the frames/audio with the same EDL (it prints the ffmpeg commands).
3. Every 2–3 seconds, cut away to a matching clip from the B-roll folder (search by what is being said).
   Index the folder first with /personal-broll-library (`python3 .claude/skills/personal-broll-library/broll_index.py <folder>`), then for each 2–3 s span pick the best clip for its words from `broll_index.json`. Cutaways cover the picture only; the voice continues.
4. Add 2–3 word captions with the current word highlighted.
5. Add a punch-in zoom (1.0→1.15 over 0.12 s, hold, ease back) on key words. Anchor the zoom on the face (`mattes/me/bounds.json` top area or OpenCV face detect).

### Approve and render

1. **3 snapshots → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w 1080 --h 1920 --data ... --stills a,b,c --stills-dir stills`, show them, wait for a yes.
2. **Render**: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>.mp4 --w 1080 --h 1920 --fps 30 --data ... --audio <original audio>`.
3. **Check**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>.mp4 --expect-audio <audio>` (add `--whatsapp out/<name>_whatsapp.mp4` if the user wants a WhatsApp copy).

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| Reel | 1080×1920 | 30 | original audio, AAC 256k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `transcribe.py`, `align.py`, `frames.sh`, `matte.py`, `vision.py`, `render.cjs`, `contact_sheet.py`, `finish.py`.
In this skill's folder: `tighten.py`.
