---
name: scribble-edit
description: "The user's own 9:16 clip covered in live boiling marker doodles (How to do this with Claude Ep 5, 'Where Are Ü Now' style): MediaPipe-tracked doodle wall behind them, face doodles that follow the head, neon body outline, clothes/hair patterns, hand props, a new look on every hit. Use when the user runs /scribble-edit with a 9:16 clip of them moving and a song MP3."
---

# Scribble edit

Your own clip covered in live marker doodles, like the Justin Bieber “Where Are Ü Now” video from How to do this with Claude (Ep 5): the wall behind you fills with hand-drawn stars, rockets, cats and lightning, crowns and shades stick to your face as you move, a neon line traces your body, and the whole look changes on every beat.

## Run it

`/scribble-edit` with: a 9:16 clip of you moving (a plain wall behind you works best) and the song MP3.

## Every time it runs

- **Draw every doodle in code** (a canvas page rendered frame by frame in headless Chrome by `render.cjs`, encoded with ffmpeg). No image generators, so the marker look is the same every time.
- **Never cover the face**: face doodles sit on top of it (crown, shades, horns), never instead of it.
- **Show a contact sheet** of stills before the full render, and ask before overwriting files.
- **Render 1080×1920 at 30 fps with the song as the audio**, plus a 720p copy under 20 MB for WhatsApp. **Check the render for black or empty frames** (`finish.py` does this) before giving it to the user.

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Track the person on every frame with MediaPipe: a person mask split into body, hair and clothes (selfie multiclass), face landmarks and pose landmarks (wrists, elbows, knees). Smooth the points over a few frames so the doodles don't jitter.
   ```bash
   bash .claude/skills/video-core/scripts/frames.sh in/clip.mp4 clips/me 30
   python3 .claude/skills/scribble-edit/track_body.py clips/me track --smooth 3   # track/masks_{person,hair,clothes}/, track/landmarks.json
   ```
2. Find the beat and every music hit in the song. Give the video a new doodle look on every hit and never hold one look longer than 7 frames, so it changes at least 4 times a second.
   ```bash
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json
   ```
   Look index = number of hits so far, plus one extra change every 7 frames inside long gaps.
3. Wall: for every look, fill the background with 15–25 marker doodles on a loose grid so there is no empty space (stars, hearts, rockets, cats, cactus, lightning, planets, mushrooms, music notes, bombs, eyes, speech bubbles with short words like BOOM or NAH). Draw them on a layer cut out by the person mask (`destination-out` with the mask) so they sit behind the person.
4. Face: draw 1–3 doodles in face space, scaled by the face width and turning with the head (roll from the eye line): crown, horns, halo, round shades, glowing eyes, skull, flower crown, beard, mask, rainbow mouth.
5. Body: most looks get a glowing neon outline around the person in one bright colour (dilate the mask, subtract it, glow), a pattern drawn on the shirt clipped to the clothes mask (ribcage, stripes, grid) and a colourful scribble clipped to the hair. Some looks swap the whole background for a full crayon backdrop (rainbow waves, stripes, op-art, galaxy, a white burst) with the person pasted back on top.
6. Props: when the hands or knees do something (air guitar = wrists close and moving; a throw = fast wrist; a kick = fast knee), draw a matching prop that follows them, like a guitar between the wrists or a ball in a parabola, with a word like ELECTRIC next to it.
7. Make it feel hand-drawn: thick wobbly marker lines in bright colours, every line redrawn slightly differently every 1–2 frames so it boils (`k.wobble` seeded by `k.boil(t, 15)`). Put the user's handle small in a corner (ask for it).

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

Shared (in `.claude/skills/video-core/scripts/`): `frames.sh`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`.
In this skill's folder: `track_body.py`.
