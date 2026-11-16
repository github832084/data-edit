---
name: madira-peekar-soo-gaye
description: "Famous movie dialogue as a comic-book scene (Drishyam 3 'madira peekar so gaye' style): one character's line fills a bubble word by word, the other explodes in close-up with speed lines and a colour flash. Use when the user runs /madira-peekar-soo-gaye with the dialogue MP3 and each line's words."
---

# Madira peekar soo gaye

A famous movie dialogue turned into a comic-book scene: one character delivers the line in a speech bubble word by word, then the other explodes in close-up with speed lines and a colour flash.

## Run it

`/madira-peekar-soo-gaye` with: the dialogue audio (MP3) and the words of each line (as SPEAKER|text rows).

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

1. Split the dialogue by speaker and force-align every word so the bubbles fill in exactly as they're said.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/dialogue.mp3 lines.txt align.json   # rows as SPEAKER|text
   python3 .claude/skills/video-core/scripts/mouth.py in/dialogue.mp3 align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
2. Draw the scene in a flat comic style: the setting (a wooden hall with pillars and a doorway), and each character as your own bold cartoon with thick outlines and halftone shading.
3. Speaker one: a mid shot with a small gesture (a raised hand), and a white speech bubble that writes the line in word by word.
4. Speaker two: cut to a tight close-up on a green halftone background with radiating speed lines. The bubble grows on every repeated word (CHEE, CHEE CHEE…) and the speed lines pulse.
5. On the last word, flash the background to purple and add a small burst sticker.
6. Render 16:9 and a 9:16 copy.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 30 | original audio, AAC 256k |
| 9:16 | 1080×1920 | 30 | original audio, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
