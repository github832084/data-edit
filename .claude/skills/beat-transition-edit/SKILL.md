---
name: beat-transition-edit
description: "Trending beat edit (How to do this with Claude Ep 1): the user's dance/twirl video in smooth half-speed slow motion on one continuous clock, cutting to their photos on every music hit with a zoom-blur dissolve and a warm film grade copied from a reference reel. Use when the user runs /beat-transition-edit with a model video, 3+ photos, a song and a reference reel."
---

# Beat transition edit

The trending beat edit from the How to do this with Claude series (Ep 1): your dance or twirl video in smooth slow motion, cutting to your photos on every music hit with a quick zoom-blur dissolve and a warm film grade, copied from any reference reel.

## Run it

`/beat-transition-edit` with: your model video, 3+ photos, the song MP3 and the reference reel.

## Every time it runs

- **Word-level timings for everything**: transcribe with `transcribe.py`, then time every word with `align.py` (MMS_FA) on the corrected text. Every graphic lands on the word it belongs to.
- **Safe zone**: keep all text out of the top 250 px and the bottom 420 px of the 1080×1920 frame (Instagram buttons and caption). Use `k.SAFE` / `k.inSafe()` in the scene.
- **Never re-grade or filter the face** unless this skill's steps say so: footage goes through `frames.sh`, which keeps the original colours, and is drawn untouched.
- **Render 1080×1920 at 30 fps with the original audio.**
- **Show 3 snapshots** (`render.cjs --stills` at three key moments) before the final render, and **ask before overwriting files** (`--force` only after a yes).
- This skill **does** grade the footage (step 5) to match the reference — that is the skill saying so. It never changes the face beyond the overall grade.
- Audio here is the song (there is no speech), so “word timings” means the song's beat and hit times from `beats.py`.

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Analyze the reference reel at 2 frames per second: find every transition, how long each shot stays, the beat it cuts on, and the colour grading.
   ```bash
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json
   python3 .claude/skills/video-core/scripts/analyze_ref.py in/reference.mp4 ref --beats beats.json   # cut grid; look at ref/sheet_*.jpg for the grade
   ```
2. Find the beat and every music hit in the song (`beats.json`). Cut on the same grid as the reference, usually every hit.
3. Play the video in smooth slow motion (half speed; interpolate if it's 30 fps) on one continuous clock, so the motion carries on every time it comes back.
   ```bash
   bash .claude/skills/video-core/scripts/frames.sh in/model.mp4 clips/model 30
   python3 .claude/skills/video-core/scripts/retime.py clips/model clips/model_slow --map "0:0,<2×dur>:<dur>" --in-fps 30 --out-fps 30
   ```
   In the scene, the video's time = elapsed time while video shots are on screen (accumulate only during video shots), so it continues where it left off.
4. Alternate it with the photos on each hit. Each photo keeps its own slow zoom (its own clock, accumulated while it is on screen), which continues on every return.
5. Use a short zoom-blur dissolve on each cut (6 frames: draw the outgoing frame 6× at scales 1.00–1.08 with falling alpha, cross to the incoming) and the same colour grade as the reference (warm film look: lift the blacks, soften the whites, warm the tint, add a vignette and fine grain — as canvas passes over the whole frame).
6. Use the song as the audio, 9:16 at 1080×1920. Show a contact sheet first, then render.

### Approve and render

1. **3 snapshots → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w 1080 --h 1920 --data ... --stills a,b,c --stills-dir stills`, show them, wait for a yes.
2. **Render**: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>.mp4 --w 1080 --h 1920 --fps 30 --data ... --audio <original audio>`.
3. **Check**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>.mp4 --expect-audio <audio>` (add `--whatsapp out/<name>_whatsapp.mp4` if the user wants a WhatsApp copy).

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 9:16 | 1080×1920 | 30 | the song, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `beats.py`, `analyze_ref.py`, `frames.sh`, `retime.py`, `render.cjs`, `contact_sheet.py`, `finish.py`.
