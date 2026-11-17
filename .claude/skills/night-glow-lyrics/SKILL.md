---
name: night-glow-lyrics
description: "16:9 lyric video that makes people feel the song (Dooron Dooron style): one night-blue grade with glowing whites, clips mapped to each line's meaning, an Instagram post that dives into the title, varied lyric hierarchy blocks, meaning moments, the last line dissolving to light. Use when the user runs /night-glow-lyrics with a song, lyrics, 2–4 dreamy clips and title/artists."
---

# Night glow lyrics

A 16:9 lyric video that makes people feel the song, like the Dooron Dooron (Paresh Pahuja ft. Harleen Sethi) video: one night-blue look with glowing white light, emotional clips that follow the story of each line, an Instagram post that dives into the title, and lyrics that change style with the music, ending with the last line turning to light.

## Run it

`/night-glow-lyrics` with: a song MP3 (or a clip of it), its lyrics, 2–4 emotional video clips (glowing / dreamy couple clips work best) and the song title + artists.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Read the lyrics for meaning and the feeling of the song, and tell the user the story in one line before you build.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Watch every clip at 2 frames per second and list each usable moment (time range + what happens: holding hands, looking from behind, reaching, alone). Map each lyric line to the moment that matches its meaning in a shot table, and never use the same moment twice.
   Prepare clips: watch each at 2 fps (`python3 .claude/skills/video-core/scripts/analyze_ref.py in/clipX.mp4 ref/clipX`), list usable moments, then cut frames with `bash .claude/skills/video-core/scripts/frames.sh in/clipX.mp4 clips/X 30 <start> <dur>`. Horizontal clips only for 16:9; never pillarbox.
3. One look for the whole video: night blue grade (this skill grades the clips on purpose: multiply #1b2a6b at 35 %, lift whites with a `screen` pass of #cfe0ff), glowing whites, soft light motes drifting, slow push-ins and crossfades between shots. One font family: Inter 300 tracked caps for small words and Instrument Serif italic for the lyrics, white with a soft blue glow and a dark shadow under the text.
4. Opening: the first clip quiet with no text, then an Instagram post of the second clip (likes, the lyric as the caption, a hashtag) that the camera dives into, landing on the song title in big glowing serif with the artists in small caps.
5. Lyric variety, timed to the voice: for the key lines a hierarchy block placed in the empty space beside the people (a small caps row, one huge serif key word, a medium row), entering with a smooth slide, rise, scale or letter-by-letter fade on the sung words. For the in-between lines a simple centred line at the bottom. Mix both so it never looks like captions.
6. Meaning moments: split lines like mitti / pari into a grey dusty word and a glowing word with sparkles, let words like dooron dooron drift apart letter by letter, and make the last line (kahan main) dissolve into light.
7. Dim any blown-out clip moment (brightness + contrast per shot) so the text always wins. Short fade in and out of the audio, 1920×1080 at 30 fps with the song.

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
