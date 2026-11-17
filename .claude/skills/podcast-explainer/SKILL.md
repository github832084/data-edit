---
name: podcast-explainer
description: "45–90 s podcast clip turned into an animated explainer (Raj Shamani 'Two Winners' style): stick-figure metaphors per idea, bold kinetic captions, the host as a lip-synced cartoon in a LIVE corner window. Use when the user runs /podcast-explainer with a podcast MP3."
---

# Podcast explainer

A podcast clip turned into an animated explainer, like the Raj Shamani “Two Winners” video: simple stick-figure metaphors for every idea, bold kinetic captions, and the host drawn as a cartoon in a live corner window.

## Run it

`/podcast-explainer` with: a 45–90 second podcast clip (MP3), plus a screenshot of the host if you have one.

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

1. Transcribe the clip and force-align every word. Split it into 6–10 ideas and give each one a short chapter chip (01 NO BACKUP, 02 NO PLAN B…).
   ```bash
   python3 .claude/skills/video-core/scripts/transcribe.py in/audio.mp3 . --lang hi --model large-v3
   ```
   STOP: show transcript.txt to the user and let them correct wrong words before aligning.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/audio.mp3 transcript.txt align.json
   python3 .claude/skills/video-core/scripts/mouth.py in/audio.mp3 align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
2. For each idea, design one simple visual metaphor on a warm off-white background (#f6f1e7): a tightrope with no safety net, a crossed-out word, a line chart that turns around, two figures compared side by side. Stick figures are `k.strokePath` lines with round heads, drawn on stroke by stroke.
3. Draw the host as a flat cartoon (same face, beard and outfit every time), lip-synced to the voice, sitting in a small LIVE window in the top corner. Open and close on a big shot of him at his desk.
   Characters are drawn as code functions `drawX(c, pose, mood, mouth, blink)` in a `cast.js` next to the scene, so the same function draws them in every shot. Save a character sheet (`render.cjs --stills` of a sheet scene showing every pose and mood) as `cast_sheet.png` and reuse the same `cast.js` in later episodes.
4. Captions: 3–4 words, bold condensed caps, the spoken word in yellow and key words in a red pill.
   `bash fonts.sh anton` (or bebas-neue). Key words list per idea; `hiPill:'#e63946'` for those, `hi:'#ffd60a'` otherwise.
5. End on a big quote card with the main line and the podcast's credit.
6. Render 16:9, plus a 9:16 version with the visuals in the top half and the host below.

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

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `transcribe.py`.
