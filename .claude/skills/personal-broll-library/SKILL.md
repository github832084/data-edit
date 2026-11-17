---
name: personal-broll-library
description: "Searchable index of the user's own B-roll folder: samples frames from every clip, writes a description (place, action, mood, time of day) per clip, and returns the 3 best matches with timestamps for a plain-English query. Use when the user runs /personal-broll-library with a folder, or asks to find a clip like 'me walking at night'."
---

# Personal B-roll library

Search my own B-roll folder in plain English (“me walking at night”) and return the best matching clips.

## Run it

`/personal-broll-library` with: a folder of your B-roll clips (and later, a plain-English search).

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

1. Go through every clip in the folder and sample frames.
   ```bash
   python3 .claude/skills/personal-broll-library/broll_index.py <folder>   # new/changed clips only; writes <folder>/.broll/<clip>/sheet.jpg + frames
   ```
2. Write a short description of each clip (place, action, mood, time of day, people, camera move) into the index file: look at each new clip's `sheet.jpg` yourself and fill its `description` and `tags` in `<folder>/broll_index.json` (the script leaves them empty for you). Add per-segment notes with timestamps when a clip has distinct parts.
3. When the user asks for a scene in plain English, read `broll_index.json` and return the 3 best matching clips with timestamps (file, start–end, why it matches), plus their sheets.
4. Keep the index updated when new clips are added: re-run `broll_index.py`; it skips clips whose size and modified time haven't changed and lists the new ones to describe.

### Approve and render

1. **3 snapshots → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w 1080 --h 1920 --data ... --stills a,b,c --stills-dir stills`, show them, wait for a yes.
2. **Render**: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>.mp4 --w 1080 --h 1920 --fps 30 --data ... --audio <original audio>`.
3. **Check**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>.mp4 --expect-audio <audio>` (add `--whatsapp out/<name>_whatsapp.mp4` if the user wants a WhatsApp copy).

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| Reel | 1080×1920 | 30 | original audio, AAC 256k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `contact_sheet.py`.
In this skill's folder: `broll_index.py`.

## Notes

This skill makes no video, so the render rules apply only when its results are used by another skill (like /personal-short-form-reels).
