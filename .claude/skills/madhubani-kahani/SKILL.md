---
name: madhubani-kahani
description: "Panchatantra-style Hindi story told as a living Madhubani painting (double black outlines, patterned fills, fish-scale water, red-yellow folk border). Use when the user runs /madhubani-kahani or wants a Hindi story voiceover turned into an animated folk painting."
---

# Madhubani kahani

A Panchatantra-style story told as a living Madhubani painting: double black outlines, patterned fills, fish-scale water and a red-yellow folk border.

## Run it

`/madhubani-kahani` with: a Hindi story voiceover MP3.

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

1. Transcribe the story in Devanagari and force-align every word to the voice.
   ```bash
   python3 .claude/skills/video-core/scripts/transcribe.py in/audio.mp3 . --lang hi --model large-v3
   ```
   STOP: show transcript.txt to the user and let them correct wrong words before aligning.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/audio.mp3 transcript.txt align.json
   ```
2. Plan one painted scene per line: the place, the characters, and the one action that matters. Write it as `scenes.json` and show it to the user.
3. Paint everything in Madhubani style: bold black double outlines, flat red, yellow, indigo and green, every shape filled with line patterns, inside a thick decorated border.
   Palette: red #c8102e, yellow #f2b705, indigo #26408b, green #2e7d32, black #111 on cream #f3e6c8. Every shape: fill, then clip to it and draw a line pattern (hatching, dots, fish scales, chevrons), then two black outlines 6 px apart. Border: 70 px band of repeating lotus/triangle motifs. Water = rows of fish-scale arcs. Patterns are seeded with `k.rng` so they never change between frames.
4. Animate small things on the spoken word: the monkey jumps, the crocodile's jaw snaps, the water ripples.
   Key each action to the aligned word (`ws.find(w => w.w.includes('कूद'))` etc.); ease with `k.ease.outBack`. Water scales shift phase slowly so it ripples.
5. Put dialogue in speech bubbles that pop in on the first spoken word of each line.
   `k.bubble` with a Devanagari font (`bash fonts.sh tiro-devanagari-hindi`), popping with `outBack` at `line.words[0].start`.
6. Render 1920×1080.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 30 | original audio, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `transcribe.py`.
