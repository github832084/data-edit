---
name: maut-ke-bare-mai-sochte-ho
description: "Podcast moment retold as a comic page (Ranveer × Honey Singh 'manzil kya hai? … Death.' style): the host's question in a bubble, a long silent beat, DEATH. slamming in on black with a skull, the guest gulping in an inset. Use when the user runs /maut-ke-bare-mai-sochte-ho with the podcast clip audio and who says what."
---

# Maut ke bare mai sochte ho

A podcast moment retold as a comic page: the host's big question in a speech bubble, a long silent beat, then DEATH. slams in on black with a skull and the guest gulps in an inset panel.

## Run it

`/maut-ke-bare-mai-sochte-ho` with: the podcast clip audio (MP3) and who says what.

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

1. Transcribe the clip, mark who speaks each line, and find the punchline word and the silent beat before it.
   ```bash
   python3 .claude/skills/video-core/scripts/transcribe.py in/audio.mp3 . --lang hi --model large-v3 --speakers
   ```
   STOP: show transcript.txt to the user and let them correct wrong words before aligning.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/audio.mp3 transcript.txt align.json   # rows as SPEAKER|text
   python3 .claude/skills/video-core/scripts/mouth.py in/audio.mp3 align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
   The silent beat is the gap before the punchline word in align.json.
2. Draw both people as clean comic portraits of your own: thick outlines, flat colours, halftone dot shading. Never trace real photos.
3. Give every line its own panel on a bright background (yellow, sky blue) with speed lines, and put the words in a white speech bubble with the key word in red. HA! bursts pop on laughs.
4. On the silent beat, cut to a dark panel with a “…” bubble and hold it. On the punchline, slam DEATH. in on black with a skull, a red burst and a camera shake.
5. Drop the listener's reaction in as a small inset panel with a GULP! sticker, then end on a tiny “THE END…?” tag.
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
