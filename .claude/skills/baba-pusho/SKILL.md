---
name: baba-pusho
description: "Puneet Superstar 'Baba Pusho' clip as a cartoon class: Pusho preaching from his desk under a big Om, his fixed students reacting, explainer cutaways for named places, Hindi captions. Use when the user runs /baba-pusho with a Puneet Superstar audio clip."
---

# Baba Pusho

A Puneet Superstar “Baba Pusho” clip as a cartoon class: Pusho preaches from his desk under a big Om, his fixed class of students reacts, and every Hindi line gets a caption plus a scene of its own.

## Run it

`/baba-pusho` with: a Puneet Superstar audio clip (MP3).

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

1. Transcribe the Hindi in Devanagari with whisper (large-v3), let the user fix any wrong words, then force-align the corrected text.
   ```bash
   python3 .claude/skills/video-core/scripts/transcribe.py in/audio.mp3 . --lang hi --model large-v3
   ```
   STOP: show transcript.txt to the user and let them correct wrong words before aligning.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/audio.mp3 transcript.txt align.json
   python3 .claude/skills/video-core/scripts/mouth.py in/audio.mp3 align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
2. Keep the same cast in every clip: Baba Pusho (long white beard, dark cap, saffron shawl) at a desk, and his students (a footballer in a #7 jersey, a man in a kurta, an old bearded baba, a Greek marble bust).
   Reuse `cast.js` from /pusho-reel if it exists (copy it into this folder too). Characters are drawn as code functions `drawX(c, pose, mood, mouth, blink)` in a `cast.js` next to the scene, so the same function draws them in every shot. Save a character sheet (`render.cjs --stills` of a sheet scene showing every pose and mood) as `cast_sheet.png` and reuse the same `cast.js` in later episodes.
3. Set the classroom in a warm beige hall with a big golden Om, an hourglass and plants. Pusho's mouth moves with the voice and the students react (shock, laugh, take notes).
4. When a line names a place or a thing, cut to a quick explainer scene for it (a temple, a mosque and a gurudwara lighting up in turn).
5. Add a small “पुशो वाणी” badge top-left, stickers on key words (COPY, RED FLAG) and Hindi captions with the spoken word in yellow on a dark band.
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

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `transcribe.py`.
