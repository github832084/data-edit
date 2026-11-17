---
name: red-sun-lyrics
description: "Quiet aching 16:9 lyric video (Kaisey Jiyun style): crumpled indigo paper, a huge crimson disc, a bare black tree losing one red leaf per line, a lonely figure, a tiny ink drawing inside the disc per line, red calligraphy lyrics blurring in. Use when the user runs /red-sun-lyrics with a song cut, lyrics, title and artist."
---

# Red sun lyrics

A quiet, aching 16:9 lyric video like the Kaisey Jiyun video: crumpled indigo paper, a huge crimson disc in the sky, a bare black tree that loses one red leaf for every line, a lonely figure sitting under it, one small black line drawing inside the disc for each line, and red calligraphy lyrics that blur in word by word.

## Run it

`/red-sun-lyrics` with: a song MP3 (a 30–60 s cut works), its lyrics, the song title and the artist name.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Read every line and pick one tiny picture that means it (a tear, two people holding hands, a rain cloud, a heart, a sunrise, a crescent, a broken heart, a shooting star, a question mark), then show the user the list.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Background: crumpled indigo paper (deep blue #141A78 to #0D1158) with soft fold lines (seeded polygon facets with subtle light/dark) and light beams drifting slowly across it. A huge crimson disc (#E5334A with a warmer glowing centre) rises in the first seconds and pulses very slightly with the song.
3. The tree: a bare black tree grows from the ground line in front of the disc during the title, branch by branch (recursive seeded branches drawn on by depth). A small hunched figure sits under it in thin line art. Red leaves sit on the branches, and one falls on every lyric line (swaying fall) and settles on the ground, so the tree is nearly empty by the end. Make as many leaves as there are lines, plus three.
4. Inside the disc, the picture for each line draws itself in thin black ink as the line is sung, holds, and fades before the next one. Keep each drawing small and simple, so it reads like a thought.
5. Lyrics: flowing red calligraphy (Great Vibes) in the empty side of the frame, a small line above and the key word bigger below, in a lighter pink for the small words. Each word blurs in exactly when it is sung. The title opens in the same script with the artist name under it in thin condensed capitals (Saira Extra Condensed: `fonts.sh great-vibes saira-extra-condensed`), and fades out before the first line.
6. Ending: the last leaf falls, the lyrics clear, and everything fades slowly to black. Light paper grain on everything, a short fade in and out of the audio, 1920×1080 at 30 fps with the song, plus a 9:16 version with the disc and tree on top and the lyrics below.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 30 | the song, AAC 256k |
| 9:16 | 1080×1920 | 30 | the song, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
