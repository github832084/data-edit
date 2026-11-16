---
name: 3d-explainer
description: "3D animated news explainer built in Blender with Python (Professor of Claude ISRO / Cyclone style): simple 3D shots in one scene, camera cuts on the user's words, numbers and labels popping in, captions, SFX, EEVEE headless render. Use when the user runs /3d-explainer with a voiceover MP3 and 2–3 article links."
---

# 3D explainer

A 3D animated news explainer built in Blender, like the Professor of Claude ISRO and Cyclone Arnab reels: Claude builds every 3D shot in code (rockets on launch pads, a 3D India map with pins, a storm spiralling over the sea, Earth from space), cuts the camera on your words and pops the numbers in as you say them.

## Run it

`/3d-explainer` with: your voiceover MP3 and the topic (2–3 article links).

## Every time it runs

- **Build every shot in Blender with Python (bpy)** and render it headless (`blender -b`) with EEVEE. No stock footage or image generators, so the look is the same every time.
- **Time every camera cut, number and caption with forced alignment** (`align.py`, torchaudio MMS_FA). Never guess timings.
- **For any map of India, use the official Natural Earth India point-of-view boundary** (`python3 .claude/skills/3d-explainer/ne_india.py india.json` reads `ne_10m_admin_0_countries_ind` from naturalearthdata.com; then `build_scene.py --india india.json`). Never draw the outline by hand.
- **Show one still of every shot** before the full render, and ask before overwriting files.
- **Render a 1080×1920 MP4 with the voice**, plus a 720p copy under 20 MB for WhatsApp.

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Check that Blender (free from blender.org) is installed and that `blender -b` runs from the terminal. Install it if it's missing.
   `bash .claude/skills/3d-explainer/check_blender.sh` (Mac: `brew install --cask blender`; Linux: the official tarball from download.blender.org, symlinked to /usr/local/bin/blender). It also checks EEVEE renders headless.
2. Transcribe the voiceover and force-align every word. Split it into 6–9 shots, one idea per shot, and tell the user the shot list before building.
   ```bash
   python3 .claude/skills/video-core/scripts/transcribe.py in/audio.mp3 . --lang hi --model large-v3
   ```
   STOP: show transcript.txt to the user and let them correct wrong words before aligning.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/audio.mp3 transcript.txt align.json
   ```
   Write `shots.json`: [{id, start_word_index, idea, models, camera_move, labels:[{text, word_index}]}].
3. Build each shot as clean, simple 3D models in its own area of one Blender scene: soft studio light, a slow camera push or orbit, and a bloom glow on lights, flames and glowing pins.
   `blender -b -P .claude/skills/3d-explainer/build_scene.py -- shots.json align.json scene.blend`. Each shot sits 100 m apart on X with its own camera; emissive materials + EEVEE bloom (Blender 4.2+: the Glare compositor node).
4. Cut to each shot's camera on the exact word that starts its idea. Keep any 3D text in English, because Blender can't draw Devanagari.
   `build_scene.py` binds cameras to timeline markers at `round(word.start × 30)`.
5. Pop big numbers and labels in as they're spoken (4 LAUNCH PADS, 2029, 125 KM/H), and add word-by-word captions with the key word in orange, outside the top 250 px and the bottom 420 px.
   English 3D numbers and labels are built in Blender (`build_scene.py` labels list). Captions (Hindi allowed) go on as a canvas overlay: render the Blender shots to `shots.mp4`, cut it into frames with `bash .claude/skills/video-core/scripts/frames.sh shots.mp4 clips/shots 30`, and draw those frames plus the captions in `overlay.html`.
6. Mix the voice with small sound effects: a whoosh on every cut, a low rumble under launches and wind under storms.
   Build `mix.wav` with ffmpeg (`adelay` + `amix`; SFX at −14 dB under the voice).

### Approve and render

1. **One still per shot → OK**: `blender -b scene.blend -P .claude/skills/3d-explainer/stills.py -- stills/` renders the middle frame of each shot; `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`.
2. **Render**: `blender -b scene.blend -a` (writes `shots.mp4`, 1080×1920, EEVEE), then the caption overlay scene: `node .claude/skills/video-core/scripts/render.cjs --page overlay.html --out out/explainer.mp4 --w 1080 --h 1920 --data align.json --audio mix.wav`.
3. **Check**: `python3 .claude/skills/video-core/scripts/finish.py out/explainer.mp4 --whatsapp out/explainer_whatsapp.mp4 --expect-audio mix.wav`.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 9:16 | 1080×1920 | 30 | voice + SFX mix, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `transcribe.py`, `align.py`, `frames.sh`, `render.cjs`, `contact_sheet.py`, `finish.py`.
In this skill's folder: `check_blender.sh`, `build_scene.py`, `stills.py`, `ne_india.py`.
