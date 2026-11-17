---
name: sketch-to-motion
description: "Rough paper sketches turned into a polished app-promo animation (Kulhad chai reel style): each sketch stays on a 'Drawing' paper card while the finished motion graphic plays beside it in a card labelled with the Claude logo + 'Opus 5.5', cut on the beat. Use when the user runs /sketch-to-motion with 8–10 sketch photos, product photos and clips."
---

# Sketch to motion

Your rough paper sketches turned into a polished app-promo animation: the sketch stays on the left, the finished motion graphic plays next to it, like the Kulhad chai reel.

## Run it

`/sketch-to-motion` with: 8–10 photos of your sketches, plus your product photos and video clips, the song MP3, and the Claude logo PNG.

## Every time it runs

- **Draw everything in code**: one `scene.html` canvas page per job, rendered frame by frame in headless Chrome by `render.cjs` and encoded with ffmpeg. No stock footage and no image generators, so the look is the same every time. Files the user attaches (photos, clips, logos) are the only outside pictures allowed.
- **Never guess timings.** Every word, cut and effect is keyed to `align.json` from `align.py` (torchaudio MMS_FA forced alignment) or to `beats.json` from `beats.py`.
- **Show a contact sheet first**: render 8–12 stills across the video (`render.cjs --stills`), tile them with `contact_sheet.py`, show the user, and wait for an OK before the full render.
- **Ask before overwriting files.** `render.cjs` and `finish.py` refuse to overwrite without `--force`; only pass it after the user says yes.
- **Deliver** the master MP4 with the original audio, plus a 720p copy under 20 MB for WhatsApp (`finish.py --whatsapp`).
- The user's product photos, clips and logos are the real assets; anything else is drawn in code. Never generate images.

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Read each sketch: the boxes, arrows and notes like “tap!”, “zoom in + type”, “flip up”, “burst!”. Each sketch is one scene. Write `scenes.json` (sketch file, layout boxes, actions in order) and show it to the user.
2. Layout: a static paper card labelled “Drawing” with the sketch photo, and a bigger card labelled with the Claude logo + “Opus 5.5” where the finished scene plays. Clip each card's content to its rounded rect so nothing spills outside the card.
3. Build each scene from real assets: real app icons, product cutouts with transparent backgrounds, video clips (rain, steam, pouring), and mood photos.
   Cutouts: `python3 .claude/skills/video-core/scripts/matte.py` on a single-image folder, or rembg directly. Clips: `bash .claude/skills/video-core/scripts/frames.sh`.
4. Do exactly what the notes say: tap with a finger and zoom, type into a search bar, flip a result screen up, scroll a photo grid, burst a word into particles.
5. Cut on the beat of the song (about every 0.55 s), and end on a logo card.
   ```bash
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json
   ```
6. Render 9:16 for reels and a 16:9 version.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 9:16 | 1080×1920 | 30 | the song, AAC 256k |
| 16:9 | 1920×1080 | 30 | the song, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `beats.py`, `frames.sh`, `matte.py`, `render.cjs`, `contact_sheet.py`, `finish.py`.

## Notes

If any spoken words or lyrics should trigger actions, align them with `align.py` too; otherwise all timing comes from `beats.json`.
