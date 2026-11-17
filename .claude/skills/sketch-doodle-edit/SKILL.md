---
name: sketch-doodle-edit
description: "One photo turned into the trending sketch doodle edit (How to do this with Claude Ep 4): the people flicker between the real photo and a Gemini pencil sketch on the beat, white wind lines swoosh across the sky, a scribble outline traces them, a handwritten line writes itself in. Use when the user runs /sketch-doodle-edit with a photo, its Gemini pencil-sketch version and a song."
---

# Sketch doodle edit

One photo turned into the trending sketch doodle edit from How to do this with Claude (Ep 4): the people flicker between the real photo and a pencil sketch on the beat, white wind lines swoosh across the sky, a scribble outline draws around them and a handwritten line writes itself in.

## Run it

`/sketch-doodle-edit` with: one photo (people against an open sky works best), its pencil-sketch version from Gemini, and the song MP3.

## Every time it runs

- **Draw the doodles, outlines and handwriting in code** (a canvas page rendered frame by frame in headless Chrome by `render.cjs`, encoded with ffmpeg). The only generated image is the pencil sketch the user gives you.
- **Keep text out of the top 250 px and the bottom 420 px** (Instagram buttons and caption).
- **Show a contact sheet** of stills before the full render, and ask before overwriting files.
- **Render a 1080×1920 MP4 with the song as the audio**, plus a 720p copy under 20 MB for WhatsApp.

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. First give the user a Gemini prompt that turns only the people in the photo into a clean pencil sketch and keeps the background exactly the same. They make the sketch in Gemini and give it back.
   Use the prompt in `.claude/skills/sketch-doodle-edit/gemini_prompt.md`, word for word. Stop until the sketch arrives.
2. Line the sketch up with the photo and use the sketch only where Gemini changed the people (a difference mask), so the sky and background stay the real photo. Paint over Gemini's sparkle watermark with the photo.
   ```bash
   python3 .claude/skills/sketch-doodle-edit/diff_mask.py in/photo.jpg in/sketch.png prep/   # aligned sketch, people mask, watermark copied from the photo
   ```
3. Fit the photo to 9:16: scale it up, crop the sides, and extend the sky smoothly at the top if it's too short. Never mirror the sky, it looks repeated.
   ```bash
   python3 .claude/skills/sketch-doodle-edit/fit_916.py prep/ prep916/   # same crop for photo, sketch and mask
   ```
4. Find the beat in the song. On the opening beats, flicker the people between the photo and the sketch, one switch per beat.
   ```bash
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json
   ```
5. Then draw white doodle wind lines swooshing across the sky, a white scribble outline that traces around the people (contour of the people mask, offset outward, drawn on with a pen tip), and a handwritten line (like “Your time on Earth is limited! Live it!”; `fonts.sh caveat`) that writes itself in word by word.
6. Make it feel hand-drawn: wobbly white marker lines that are redrawn slightly differently every 2 frames so they boil (`k.boil(t, 15)` seeds).

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 9:16 | 1080×1920 | 30 | the song, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
In this skill's folder: `gemini_prompt.md`, `diff_mask.py`, `fit_916.py`.
