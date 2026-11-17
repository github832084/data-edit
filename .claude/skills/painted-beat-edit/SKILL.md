---
name: painted-beat-edit
description: "Viral footage edit remade with no footage (Shiv aarti reel, How to do this with Claude Ep 2): acrylic-mural images painted in code, cut on every half-beat with slow zoom, one big moment on the drop. Use when the user runs /painted-beat-edit with a song MP3 and a reference reel."
---

# Painted beat edit

A viral footage edit remade with no footage at all, like the Shiv aarti reel from How to do this with Claude (Ep 2): Claude paints the images in code in an acrylic mural style and cuts between them on every half-beat with a slow zoom.

## Run it

`/painted-beat-edit` with: the song MP3 and the reference reel.

## Every time it runs

- **Draw everything in code**: one `scene.html` canvas page per job, rendered frame by frame in headless Chrome by `render.cjs` and encoded with ffmpeg. No stock footage and no image generators, so the look is the same every time. Files the user attaches (photos, clips, logos) are the only outside pictures allowed.
- **Never guess timings.** Every word, cut and effect is keyed to `align.json` from `align.py` (torchaudio MMS_FA forced alignment) or to `beats.json` from `beats.py`.
- **Show a contact sheet first**: render 8–12 stills across the video (`render.cjs --stills`), tile them with `contact_sheet.py`, show the user, and wait for an OK before the full render.
- **Ask before overwriting files.** `render.cjs` and `finish.py` refuse to overwrite without `--force`; only pass it after the user says yes.
- **Deliver** the master MP4 with the original audio, plus a 720p copy under 20 MB for WhatsApp (`finish.py --whatsapp`).

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Analyze the reference at 2 frames per second: note every cut, how long each shot holds and which beat it lands on.
   ```bash
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json
   python3 .claude/skills/video-core/scripts/analyze_ref.py in/reference.mp4 ref --beats beats.json
   ```
2. Rebuild the same edit, but instead of footage, paint the images in code in an acrylic mural style with visible brush strokes (thousands of seeded short strokes per image, rendered once in `setup` to offscreen canvases). For the Shiv aarti: a blue Lord Shiva face with the crescent moon and tilak, drawn respectfully, and a priest doing aarti with fire.
3. Cut between them on every half-beat (`half_beats`), with a slow continuous zoom and a little fire and glow that moves.
4. Save one big moment for the drop: open Shiva's eyes exactly on it.
5. No text. 9:16, 1080×1920, with the song as the audio.

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

Shared (in `.claude/skills/video-core/scripts/`): `beats.py`, `analyze_ref.py`, `render.cjs`, `contact_sheet.py`, `finish.py`.

## Notes

No words are sung-timed here, so alignment is not needed unless the song has lyrics you want to hit; cuts come from `beats.json`, never guessed.
