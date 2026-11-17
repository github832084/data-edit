---
name: anime-reel
description: "Anime-style episode with original characters drawn in code and lip-synced to the user's voice lines (Zero Se Freelance style). Use when the user runs /anime-reel or asks for an anime episode from a script plus one voice MP3 per line."
---

# Anime reel

An anime-style episode with original characters drawn in code and lip-synced to your voice lines, like the Zero Se Freelance series.

## Run it

`/anime-reel` with: the script and the voice MP3 for each line (name them 01.mp3, 02.mp3 … in script order).

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

1. Read the script and split it into shots: who speaks, where it happens, and the camera move.
   Write `shots.json`: one entry per voice line with speaker, location, camera (push-in, pan, whip, static, two-shot), mood and any anime trick.
   Join the line MP3s into one track with a 0.25 s gap, keeping each line's offset: `ffmpeg -f concat` on the files, then write `lines.txt` as `SPEAKER|text`, one row per MP3.
2. Draw each character in anime style (big eyes, thick clean outlines, flat colours with one shade) and save a character sheet, so they look the same in every shot.
   Characters are drawn as code functions `drawX(c, pose, mood, mouth, blink)` in a `cast.js` next to the scene, so the same function draws them in every shot. Save a character sheet (`render.cjs --stills` of a sheet scene showing every pose and mood) as `cast_sheet.png` and reuse the same `cast.js` in later episodes.
3. Force-align every voice line, open and close each mouth with the loudness of that character's voice, and add blinks and small idle motion.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py voice.wav lines.txt align.json   # rows as SPEAKER|text
   python3 .claude/skills/video-core/scripts/mouth.py voice.wav align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
   Idle motion: breathing (`Math.sin(t*2)` on the torso), hair sway with `k.noise1`, blinks with `k.blink(t, seed)` (different seed per character).
4. Add anime tricks on key lines: speed lines, impact frames, screen shake and chibi reactions.
   Speed lines `k.speedLines`; impact frame = 2–3 frames of inverted black/white silhouette; shake `k.shake` for 0.3 s on the hit word; chibi = the same character function at 0.6× head-to-body ratio with simple face.
5. Add 2–3 word captions with the spoken word in the speaker's colour, and sound effects on the hits. No background music unless the user asks.
   `k.chunks(words, 3)` + `k.caption(..., {wordColor})` with each speaker's colour. Mix SFX (whoosh, hit) with ffmpeg `amix` at the hit times into `mix.wav` and render with `--audio mix.wav`.
6. Render 9:16 for reels and a 16:9 copy for YouTube.
   Lay the scene out from `k.W`/`k.H` so the same page renders both; keep captions in the 9:16 safe zone.

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

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
