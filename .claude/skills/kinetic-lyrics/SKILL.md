---
name: kinetic-lyrics
description: "Big kinetic typography for an English song (Justin Bieber 'Let Me Love You' style): chunky words punching in on the beat on black, oversized key words, paint splats, petals and confetti. Use when the user runs /kinetic-lyrics with a song MP3 and lyrics."
---

# Kinetic lyrics

Big kinetic typography for an English song, like Justin Bieber's “Let Me Love You”: every word punches in on the beat in chunky letters on black, with paint splats and confetti.

## Run it

`/kinetic-lyrics` with: a song MP3 and its lyrics, one sung line per row.

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
2. Black background. Each line builds word by word in heavy rounded display caps (`fonts.sh fredoka` 700 or `baloo-2` 800); the key word of each line is 2–3× bigger (BELIEVE, BEAUTIFUL, DREAM).
3. Every word lands exactly on its sung time with a pop (`outBack`), a squash (scaleY 0.8→1 over 0.1 s) and a small shake on strong beats.
4. Add accents that fit the words: falling petals, rain drips on “smoke and mirrors”, a pink paint splat behind “miracle”, sparkles on the chorus.
5. Open with the artist names as a title card, and clear each line with a quick wipe before the next one.
6. Render 16:9 and a 9:16 version.

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
