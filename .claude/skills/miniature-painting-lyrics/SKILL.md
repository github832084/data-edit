---
name: miniature-painting-lyrics
description: "Seamless 16:9 lyric video (Khat style): an Indian miniature painting that comes alive through Gemini image sheets and Google Flow clips joined with no visible cuts, Devanagari lyrics that move with their meaning; includes the real Gemini and Flow prompts. Use when the user runs /miniature-painting-lyrics with a song cut, Devanagari lyrics, title and artist."
---

# Miniature painting lyrics

A seamless 16:9 lyric video like the Khat video: an Indian miniature painting that comes alive, flowing from paper flowers to a diya, a pop-up blue house, her eye, a field of blue flowers and a flying letter with no visible cuts, and Hindi lyrics that move with their meaning. It includes the real Gemini image prompts and Google Flow video prompts.

## Run it

`/miniature-painting-lyrics` with: a song MP3 (a 60–75 s cut works), its lyrics in Devanagari, the song title and the artist name. Later: the 3 Gemini sheets and the Flow clips.

## Every time it runs

- **The only generated images and clips are the ones the user makes** from the prompts this skill gives them (Gemini / Google Flow). Everything else — cutting, joins, lyrics, overlays and the render — is done in code: a canvas page rendered frame by frame in headless Chrome (`render.cjs`), encoded with ffmpeg.
- **If an image or clip is missing, ask for it. Never use a placeholder.**
- **Never guess timings**: every word comes from `align.py` (torchaudio MMS_FA) on the vocal stem.
- **Show a contact sheet** of stills before the full render, and **ask before overwriting files**.
- **Deliver** the MP4 with the song, plus a smaller copy for WhatsApp (`finish.py --whatsapp`, under 20 MB).

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Read the lyrics and write the story in one line, then a table of which picture belongs to each lyric line, and show it to the user.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Give the user the 3 Gemini image prompts. They make each one at the highest quality and save them as sheet-1.png, sheet-2.png and sheet-3.png. Cut each sheet along its grid into 4 separate 1920×1080 frames and name them A to L. All the people are on sheet 1, so they stay consistent without separate character images.
   Prompts: `.claude/skills/miniature-painting-lyrics/prompts.md` (for Khat word for word; for another song keep the style lines, the 2×2 grid and the two-part clip structure, and change only the people, places and objects).
   Cut: `python3 .claude/skills/miniature-painting-lyrics/cut_sheets.py in/ frames/` (finds the thin black grid lines, crops each panel, resizes to 1920×1080, maps panels to letters A–L per the prompt's layout).
3. Give the user the 4 round 1 Flow prompts, one at a time, with the two frames to attach to each. They use Frames to Video at 16:9 with 2 outputs, on a Veo model that takes a first and last frame. Tell them to run clip 3 first, because it's the hardest and shows quickly whether two scenes fit in one clip, and to re-roll if a face melts, a hard cut appears or text shows up.
4. When the 4 clips are back, watch where they feel slow or empty. Cut the first and last frames for the 4 round 2 prompts at the times listed and give the user those prompts. These add the big moments: the ink vine to the temple, the pop-up house, the couple together, and the letter flying over the town.
   ```bash
   python3 .claude/skills/video-core/scripts/analyze_ref.py in/clip1.mp4 ref/clip1   (repeat per clip)
   ffmpeg -ss 6.4 -i in/clip1.mp4 -frames:v 1 frames/x1_first.png   (times are in prompts.md)
   ```
5. Re-cut all 8 clips into about 11 shots that run close to real speed, so nothing looks stretched. Mute the Flow audio. Flow doesn't always land on the exact last frame, so drop any part where a person's look changes. Time each shot to its lyric line and hide the joins with a zoom through an object, a glow from the flame, a soft fade, or a watercolour bloom that spreads across the frame.
   Paint out the Flow sparkle on every frame: python3 .claude/skills/video-core/scripts/paint_out.py clips/1 clips/1_clean --corner br
   Retime with python3 .claude/skills/video-core/scripts/retime.py where a shot must stretch to its line.
6. Lyrics: Devanagari in Tiro Devanagari Hindi with Kalam for the handwritten words (`fonts.sh tiro-devanagari-hindi kalam`), a few words at a time, in the empty part of each shot. Each word appears exactly when it is sung, and each line gets an effect that matches its meaning: words about writing are written on stroke by stroke, the prayer rises out of the diya flame, the house line folds up like the pop-up house, the blue paint line is revealed with a dry-brush stroke, the flower line blows in on the wind, and the khat line is written on the envelope and moves with it. Put a torn paper slip behind any word on a busy shot so it stays readable.
7. Open on the title in Caladea with the artist name small below it (`fonts.sh caladea`), over the hands folding flowers, and fade it out before the first line. End on the hand lifting the letter at the blue door, then fade out. Add light paper grain, 1920×1080 at 30 fps with the song.

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

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `analyze_ref.py`, `paint_out.py`, `retime.py`, `frames.sh`.
In this skill's folder: `prompts.md`, `cut_sheets.py`.
