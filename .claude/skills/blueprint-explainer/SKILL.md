---
name: blueprint-explainer
description: "Long 3–10 minute YouTube explainer drawn as an engineering blueprint (Piramal Finance loan style): blue grid sheets, white technical line drawings, live calculations as numbers are spoken. Use when the user runs /blueprint-explainer with a long voiceover MP3 and the facts or numbers."
---

# Blueprint explainer

A long YouTube explainer drawn like an engineering blueprint, like the Piramal Finance loan video: a blue grid sheet, white line drawings, and numbers that calculate live as you talk.

## Run it

`/blueprint-explainer` with: a long voiceover MP3 (3–10 minutes) and the facts or numbers it covers.

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

1. Transcribe and force-align the voiceover, then split it into sheets, one topic per sheet (Loan amount, Interest, Tenure, CIBIL, Documents…), each with a sheet number in the title block.
   ```bash
   python3 .claude/skills/video-core/scripts/transcribe.py in/audio.mp3 . --lang hi --model large-v3
   ```
   STOP: show transcript.txt to the user and let them correct wrong words before aligning.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/audio.mp3 transcript.txt align.json --windows whisper_lines.json   # long files: align per Whisper segment window
   ```
   (make whisper_lines.json from whisper.json segments: [[start,end],...], one per transcript row)
2. Style: deep blue blueprint paper (#0b3d91 with a fine #ffffff14 grid every 24 px and a bolder one every 120 px), thin white lines, monospace labels (`fonts.sh ibm-plex-mono`), yellow (#ffd60a) for the key numbers. Title block bottom-right with sheet number, title and date.
3. Draw every idea as a technical diagram that builds stroke by stroke: a policy file with labelled boxes, a ruler for the loan range, a gauge for the CIBIL score, a flow of steps for the process. Dimension lines and leader labels like a real drawing.
4. When numbers are spoken, show the calculation live: an EMI table filling in row by row, a total counting up, a bar that grows. Compute the numbers in code (EMI = P·r·(1+r)^n / ((1+r)^n − 1)) from the user's facts; never invent figures.
5. Captions: 3–5 words at the bottom, the key word in yellow. Keep a small sheet label in the corner the whole time.
6. Render 16:9 for YouTube, plus 9:16 cut-downs of the best minute.
   Pick the best minute with the user; render it with `--from/--to` on a 9:16 layout of the same sheets.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 30 | original audio, AAC 256k |
| 9:16 cut-down | 1080×1920 | 30 | original audio, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

Long renders: use `--workers 4` (or more); render in `--from/--to` chunks of 2 minutes if memory is tight, then join with ffmpeg concat.

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `transcribe.py`.
