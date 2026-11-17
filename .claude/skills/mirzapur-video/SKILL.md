---
name: mirzapur-video
description: "Web-series dialogue turned into a comic meme (Kaalin Bhaiya 'chai piyoge?' style): a bold comic caricature of the don, halftone backgrounds swapping on every beat, a POV caption pill. Use when the user runs /mirzapur-video with the dialogue MP3 and a POV line."
---

# Mirzapur video

A web-series dialogue turned into a comic meme, like the Kaalin Bhaiya “chai piyoge?” reel: a bold comic portrait of the don, halftone backgrounds that change on every beat, and a POV caption.

## Run it

`/mirzapur-video` with: the dialogue audio (MP3) and a POV line for the caption.

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

1. Force-align the dialogue and mark the beats: the pause, the stare, the punchline.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/dialogue.mp3 lines.txt align.json
   python3 .claude/skills/video-core/scripts/mouth.py in/dialogue.mp3 align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
   The pause = the longest gap between words; the punchline = the last line.
2. Draw the don as your own bold comic caricature: thick outlines, flat colours, halftone shading, and props like shades, a tilak or a chai glass.
   Characters are drawn as code functions `drawX(c, pose, mood, mouth, blink)` in a `cast.js` next to the scene, so the same function draws them in every shot. Save a character sheet (`render.cjs --stills` of a sheet scene showing every pose and mood) as `cast_sheet.png` and reuse the same `cast.js` in later episodes.
3. Swap the background on every beat (green bokeh, cream halftone, purple night) and add radiating speed lines and a HAAN! burst on the punchline.
4. Keep the POV caption in a blue pill (#1d4ed8, white text) at the bottom the whole time (above the safe zone in 9:16).
5. Use small moves only: a slow push-in, an eyebrow raise, shades sliding down, steam rising from the chai.
6. Render 16:9 and 9:16.

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
