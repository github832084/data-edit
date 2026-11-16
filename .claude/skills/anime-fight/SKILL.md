---
name: anime-fight
description: "One-punch-style anime gag: a sleepy original hero ends an original giant monster with one punch, then punches something relatable (MONDAY 9 AM → HOLIDAY). Use when the user runs /anime-fight with a voiceover MP3 and the second-punch joke."
---

# Anime fight

An anime fight gag in the one-punch style: a sleepy, unbothered hero ends a giant monster with a single punch, then turns the same punch on something relatable, like Monday morning.

## Run it

`/anime-fight` with: your voiceover MP3 and the joke you want on the second punch.

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

1. Force-align the voiceover and mark the two punch words and the reveal word.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/voice.mp3 lines.txt align.json
   python3 .claude/skills/video-core/scripts/mouth.py in/voice.mp3 align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
2. Design an ORIGINAL hero (never copy an existing anime character): their own hairstyle, outfit and a bored, half-lidded stare. Make the monster original too: horns, extra eyes, a jagged grin.
3. Set an anime sunset sky over a ruined city. On the first punch, add radial speed lines, an impact flash (2 white frames + 2 inverted frames), screen shake and a big DHISHUM! burst.
4. The monster bursts into confetti (seeded particles with gravity), with a small “villain gaayab” label.
5. For the second joke, drop in the relatable thing (a MONDAY 9 AM calendar page) and punch it into the payoff (HOLIDAY ✨).
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
