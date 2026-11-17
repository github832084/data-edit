---
name: flicker-edit
description: "Viral flicker edit (How to do this with Claude Ep 6): two tripod shots, one with the model and one empty, swapped every quarter beat so she appears and vanishes, with a face-anchored zoom on each return, a warm sunset grade and soft flashes. Use when the user runs /flicker-edit with a model shot, the same empty shot and a song."
---

# Flicker edit

The viral flicker edit from How to do this with Claude (Ep 6): two shots from the same tripod spot, one with the model and one of the empty beach, cut against each other about 8 times a second on the beat, so the model appears and vanishes into the sea, with a small zoom to her face every time she comes back.

## Run it

`/flicker-edit` with: a shot (or photo) of the model, the same frame without her, and the song MP3 (plus a reference reel if you have one).

## Every time it runs

- **Do the cutting, zooms and grade in code**: `flicker.py` (Python + numpy piped into ffmpeg). No CapCut, no manual splits.
- **Keep both shots framed exactly the same**, so the only thing that changes on a cut is the model (same crop box for both).
- **Show a contact sheet** of stills before the full render, and ask before overwriting files.
- **Render 1080×1920 with the song as the audio**, plus a 720p copy under 20 MB for WhatsApp.

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Take the two shots from the same spot and the song. If a reference reel is attached, measure how often it cuts (frame differences); the viral one swaps about every 0.1–0.13 s.
   ```bash
   python3 .claude/skills/video-core/scripts/analyze_ref.py in/reference.mp4 ref --threshold 0.15   # cuts_per_sec
   ```
2. Find the beat in the song. Swap between the model shot and the empty shot every quarter beat, so it flickers about 8 times a second in sync with the music.
   ```bash
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json   # quarter_beats
   ```
3. Open on one beat of the model, and end on the last beat with only the empty beach, so she's gone.
4. Crop both shots to 9:16 with the horizon at the same height, and grade them to one warm sunset look (a little contrast, a warm tint, a soft vignette, fine grain) so the cut is seamless. `flicker.py` finds the horizon and the face automatically; check them in the preview stills.
5. Every time the model appears, zoom in about 3 % towards her face with an ease-out over that quarter beat, on top of a slow 8 % push-in over the whole edit. Anchor every zoom on her face so it stays in place.
6. Add a very short soft white flash on the strongest beats (`hits`), use the song as the audio and export the MP4.

### Approve and render

1. **Stills → OK**: `python3 .claude/skills/flicker-edit/flicker.py in/model.jpg in/empty.jpg in/song.mp3 beats.json out/flicker.mp4 --stills stills/` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`.
2. **Render**: same command without `--stills` (refuses to overwrite without `--force`).
3. **Check**: `python3 .claude/skills/video-core/scripts/finish.py out/flicker.mp4 --whatsapp out/flicker_whatsapp.mp4 --expect-audio in/song.mp3`.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 9:16 | 1080×1920 | 30 | the song, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `beats.py`, `analyze_ref.py`, `vision.py`, `contact_sheet.py`, `finish.py`.
In this skill's folder: `flicker.py`.
