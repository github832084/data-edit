---
name: personal-explainer
description: "Explainer in the user's own voice ('How will the Tesla fly?' style): real footage with credit, step-by-step diagrams, popping numbers, RAAZ chapter chips. Use when the user runs /personal-explainer with a voiceover MP3, the topic and source links."
---

# Personal explainer

An explainer in your own voice, like “How will the Tesla fly?”: real footage with credit, clean diagrams that build step by step, numbers that pop, and you as the narrator.

## Run it

`/personal-explainer` with: your voiceover MP3, the topic, any source links, and any real footage clips of the subject you have the right to use.

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

1. Fact-check the topic from the links and split the voiceover into 3–4 “raaz” (secrets), each with a chip like RAAZ #1 · ULTA CHIPAKNA.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/voice.mp3 lines.txt align.json
   ```
2. Use real footage of the subject where it exists (clips the user attaches), always with a small “Footage: source” credit, and darken it so the graphics read.
   ```bash
   bash .claude/skills/video-core/scripts/frames.sh in/clip.mp4 clips/a 30
   ```
   In the scene: draw the frame, then a 45 % black overlay; this is a graphic overlay, not a regrade.
3. Draw a clean diagram for each idea that builds piece by piece as you say it: arrows for airflow, a tank with a pressure number, labels on the parts. Each part draws on with `k.strokePath` at its word.
4. Pop big numbers on the word (7,145 PSI, x300!) and NA ✗ chips for what it is not (NA VFX ✗, NA RASSI ✗). Numbers count up over 0.4 s with `outExpo`.
5. Add 2–3 word captions with the active word highlighted, and a hook question at the start.
6. Render 9:16 and 16:9.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 9:16 | 1080×1920 | 30 | original audio, AAC 256k |
| 16:9 | 1920×1080 | 30 | original audio, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `frames.sh`.

## Notes

Footage the user attaches is the only non-drawn imagery. If no footage exists for a part, draw it instead; never pull stock footage.
