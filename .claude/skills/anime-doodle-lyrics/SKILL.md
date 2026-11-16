---
name: anime-doodle-lyrics
description: "Moody 16:9 lyric video like Eden's Echo's 'Parvah Nahi': the user's anime clips graded deep navy, each cut blooming from line-art into colour, white marker doodles showing each line's hidden meaning, outline lyrics that trace and fill. Use when the user runs /anime-doodle-lyrics with a song, lyrics and 3–6 horizontal anime clips with start times."
---

# Anime doodle lyrics

A moody 16:9 lyric video like Eden's Echo's Parvah Nahi from Ye likho ye milega: your anime clips graded deep navy, every cut blooming from line-art into colour, white marker doodles that add the hidden meaning of each line, and lyrics drawn as outlines that trace themselves and then fill.

## Run it

`/anime-doodle-lyrics` with: a song MP3 (or a clip of it), its lyrics and 3–6 horizontal anime clips (with the start time for each).

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Read every line for its deeper meaning and write the user one doodle idea per line before you build.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Watch every clip at 2 frames per second and list the usable moments (time range + what happens). Map each lyric line to the moment that matches it in a shot table, and never use the same moment twice. Use horizontal clips only; never pillarbox a vertical clip.
   Prepare clips: watch each at 2 fps (`python3 .claude/skills/video-core/scripts/analyze_ref.py in/clipX.mp4 ref/clipX`), list usable moments, then cut frames with `bash .claude/skills/video-core/scripts/frames.sh in/clipX.mp4 clips/X 30 <start> <dur>`. Horizontal clips only for 16:9; never pillarbox.
3. Grade all footage the same (this skill's intended look): a soft deep-navy multiply (#1a2550 at 40 %) so the doodles and text glow on top. At every cut, start from an edge-detected line-art version of the new shot (pre-make edge frames with OpenCV Canny into `clips/X_edges/`) and bloom it into full colour over half a second.
4. Doodles: white marker lines with a slightly shaky hand-drawn feel (`k.wobble`, re-seeded every 2 frames), drawn on stroke by stroke with a pen dot, placed next to the subject and never over a face. Make each one show the meaning of its line: hands cupping a falling comet, a question mark that morphs into a heart, rain that grows flowers, a stitched heart that heals while band-aids float away, a red thread that ties two hands, a heartbeat line that ends in a heart.
5. Lyrics: each word is an outline (Cormorant italic for small rows, Kaushan Script for the key word: `fonts.sh cormorant kaushan-script`) that traces itself with a pen dot exactly when it is sung (`strokeText` with a growing dash), then fills in white or warm pink. Keep lyrics mid-frame on the left, centre or right in the empty space, never at the bottom where phone players cover them.
6. Soft light leaks and floating dust, a gentle push-in on every shot, a short fade in and out of the audio, 1920×1080 at 30 fps with the song.

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

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `frames.sh`, `analyze_ref.py`.
