---
name: paper-cutout
description: "Paper-cutout music video like 'Jaadoo': hand-cut paper characters and floating islands in 15 fps stop-motion, lyric words on little paper tags popping on their sung time. Use when the user runs /paper-cutout with a song MP3 and lyrics."
---

# Paper cutout music video

A paper-cutout music video like Jaadoo: hand-cut paper characters, floating islands and lyric tags that pop on their words, moving in 15 fps stop-motion.

## Run it

`/paper-cutout` with: a song MP3 and its lyrics, one sung line per row.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Build every character and set from cut paper: flat colours, slightly rough edges (seeded jitter on outlines, fixed per piece), a drop shadow under each piece and a fibre texture.
3. Animate in 15 fps stop-motion steps so it feels handmade: quantise motion time with `tq = Math.floor(t*15)/15` (render still runs at 30 fps). Characters walk, wave and float between scenes like islands in the sky.
4. Put each lyric word on its own little paper tag that pops in on its sung time and bounces on the beat.
5. Add grain and a soft vignette. Show streaming badges (Spotify, Apple Music; drawn as simple text pills unless the user attaches the logos) in a corner early on.
6. Render 16:9 and 9:16.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 30 | the song, AAC 256k |
| 9:16 | 1080×1920 | 30 | the song, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
