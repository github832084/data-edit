---
name: glass-to-neon-lyrics
description: "Emotional 16:9 lyric video that keeps changing mood (Arz Kiya Hai style): a red frosted-glass lyrics card that cracks and shatters, full-screen clips with lyrics in the empty space, a key line cut out as giant letters with fire inside, and a pink neon ending with rain and water reflections. Use when the user runs /glass-to-neon-lyrics with a song, lyrics, cover art and 4–6 clips or photos."
---

# Glass to neon lyrics

An emotional 16:9 lyric video that keeps changing mood with the song, like the Arz Kiya Hai (Anuv Jain × Lost Stories) video: a red glass lyrics card over a wall of giant red words that cracks and shatters, then full-screen clips with the lyrics standing in the empty space, a key line cut out as giant letters with fire burning inside them, and a pink neon ending where lyrics fall in, splash and reflect in water while it rains.

## Run it

`/glass-to-neon-lyrics` with: a song MP3 (or a clip of it), its lyrics, the cover art, and 4–6 clips or photos with the mood you want for each part.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Read the lyrics for meaning and split the song into parts: card, clips, key line, neon ending. Tell the user which clip goes with which lines and use every clip only once.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Part 1, glass card: a dark red frosted-glass card (cover art, song title, artists) like the Apple Music lyrics screen, tilted slightly in 3D. Each word fills from dim to bright exactly when it is sung, the next line waits blurred below, and a soft shine sweeps across on every line change. Behind it, a slow scrolling wall of the lyric words in giant deep-red caps.
3. At the end of part 1, crack the card with thin light lines (seeded branching cracks from an impact point), then shatter it into glass shards that fly toward the camera (scale up + rotate + fade) with a red bloom into the next part.
4. Part 2, clips: each clip full-screen in its natural colours, with a slow push-in. Place the lyrics in the empty space of each shot (above the person or below the horizon, never over a face): a small tracked caps row, one big Inter 800 caps row and one word in red Great Vibes script that writes itself on, all word by word on the voice. On a still photo (like a starry field), make it alive: twinkling stars, a few shooting stars and light drifting.
   Prepare clips: watch each at 2 fps (`python3 .claude/skills/video-core/scripts/analyze_ref.py in/clipX.mp4 ref/clipX`), list usable moments, then cut frames with `bash .claude/skills/video-core/scripts/frames.sh in/clipX.mp4 clips/X 30 <start> <dur>`. Horizontal clips only for 16:9; never pillarbox.
   Find faces/bodies to avoid: `python3 .claude/skills/video-core/scripts/matte.py clips/X mattes/X` and use `bounds.json`.
5. Key line: cut the words out of black as giant Inter 900 letters so a fire (or any bright clip) burns only inside the letters, then let the letters grow until the clip fills the screen. Soft white flashes or red burns between shots.
6. Part 3, pink neon ending: all clips in a pink duotone (this skill's intended grade), darker at the bottom. Neon lyric words drop in one by one with a small bounce, flicker on like a sign, and land with a splash ripple and drops on a wet floor that mirrors them. Add light rain and a few drops on glass. On the last word, hold the frame and fade out.
7. Grain and a soft vignette on everything, a short fade in and out of the audio, 1920×1080 at 30 fps with the song.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 30 | the song, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `frames.sh`, `matte.py`, `analyze_ref.py`.
