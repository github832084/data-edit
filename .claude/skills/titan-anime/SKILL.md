---
name: titan-anime
description: "Anime episode in an Attack-on-Titan-style walled world (giant walls, green capes, horses, flags, titans) with the user's own original characters telling a lesson. Use when the user runs /titan-anime with a script and per-line voice MP3s."
---

# Titan anime

An anime episode set in an Attack on Titan-style world: giant walls, green capes, horses, flags and titans, with your own original characters telling the story.

## Run it

`/titan-anime` with: the script and the voice MP3 for each line (01.mp3, 02.mp3 …).

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

1. Read the script and plan shots in a walled-city world: wall tops at sunset, a gate, a training ground, a castle in the clouds, titans peeking over the wall. Write `shots.json` and join the line MP3s as in /anime-reel.
2. Design original characters (never copy real anime characters): anime faces, green capes with a wing emblem, brown harness straps. Save a character sheet so they look the same in every shot.
   Characters are drawn as code functions `drawX(c, pose, mood, mouth, blink)` in a `cast.js` next to the scene, so the same function draws them in every shot. Save a character sheet (`render.cjs --stills` of a sheet scene showing every pose and mood) as `cast_sheet.png` and reuse the same `cast.js` in later episodes. The wing emblem is your own design (two simple abstract wings), not the show's crest.
3. Use the world as metaphors for the lesson: the wall is the limit you break, the gate opens when you succeed, the Survey Corps-style flag is your mission.
4. Lip-sync every voice line, add speed lines, impact frames and shake on the big moments, and a horse ride for the “mission” beat.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py voice.wav lines.txt align.json   # rows as SPEAKER|text
   python3 .claude/skills/video-core/scripts/mouth.py voice.wav align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
   Horse ride: side-on gallop cycle (4 leg poses looping at 8 fps), parallax wall and fields behind.
5. Captions: 2–3 words with the spoken word in the speaker's colour, plus a small episode badge (ZERO SE FREELANCE · EP 3).
   Ask the user for the episode number if it is not in the script.
6. Render 9:16 for reels and a 16:9 copy.

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
