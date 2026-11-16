---
name: iphone-style-by-aansh
description: "Talking-head reel with frosted iOS-style widgets and notifications (weather, calendar, notes) floating over the footage, sliding down from the top as things are mentioned, in a light clean Apple look. Use when the user runs /iphone-style-by-aansh with a 9:16 clip."
---

# iPhone style by Aansh

Frosted iOS widgets and notifications floating over my footage.

## Run it

`/iphone-style-by-aansh` with: a 9:16 talking-head clip.

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
2. Turn the points into iOS-style widgets (weather, calendar, notes, notifications).
3. Use frosted glass, rounded corners and an SF-like font look (`fonts.sh inter`; SF Pro is not freely licensed).
4. Slide notifications down from the top (below the 250 px safe line) as things are mentioned.
5. Keep everything in Apple's light, clean style.

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
