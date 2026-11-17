---
name: katha-video
description: "A 60–90 s pravachan clip turned into an animated story: the cast acts out the kahani, the speaker talks from a lip-synced corner badge, Hindi captions follow every word. Use when the user runs /katha-video or sends a pravachan MP3."
---

# Katha video

A pravachan clip turned into an animated story: the characters act out the kahani, the speaker talks from a lip-synced corner badge, and Hindi captions follow every word.

## Run it

`/katha-video` with: a 60–90 second pravachan MP3.

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

1. If music or noise sits behind the voice, separate the vocals with demucs.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/pravachan.mp3 .   # use vocals.wav for transcription and alignment, the original MP3 for the final audio
   ```
2. Transcribe in Devanagari with whisper (large-v3), then stop and show the user the text so they can correct wrong words.
   ```bash
   python3 .claude/skills/video-core/scripts/transcribe.py vocals.wav . --lang hi --model large-v3
   ```
   STOP and wait for the corrected `transcript.txt`.
3. Force-align the corrected text and make a mouth-open curve from the voice loudness.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py vocals.wav transcript.txt align.json
   python3 .claude/skills/video-core/scripts/mouth.py vocals.wav align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
4. Plan 20–26 shots in 6–8 chapters with Hindi titles and show the user the shot list before writing any code.
5. Draw the speaker with respect (never comic) on a golden seat with a starry backdrop, plus the story's cast, in a flat Indian cartoon style.
   Characters are drawn as code functions `drawX(c, pose, mood, mouth, blink)` in a `cast.js` next to the scene, so the same function draws them in every shot. Save a character sheet (`render.cjs --stills` of a sheet scene showing every pose and mood) as `cast_sheet.png` and reuse the same `cast.js` in later episodes.
   The speaker: calm proportions, gentle blinks, no exaggerated mouth or gags; golden seat with carved arms, deep blue starry backdrop with a soft halo.
6. Captions in 3–5 word Hindi chunks with the spoken word in a marigold pill, a chapter chip top-left, and a 9:16 version with the speaker below the story.
   `k.caption(c, chunk, t, {hiPill:'#f6a21a', font:'700 64px Tiro Devanagari Hindi'})`. 16:9: story full frame, speaker badge in a round frame bottom-right. 9:16: story in the top 60 %, speaker large below it, captions above the bottom safe zone.

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

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `stems.sh`, `transcribe.py`.
