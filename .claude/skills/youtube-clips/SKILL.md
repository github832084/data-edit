---
name: youtube-clips
description: "Find the 5 best 30–60 s moments in a long 16:9 video or YouTube link, reframe each to 9:16 by following the speaker's face, and add captions and a title card. Use when the user runs /youtube-clips with a long video or a YouTube link."
---

# YouTube clips

Find the best moments in a long YouTube video and turn each into a vertical clip.

## Run it

`/youtube-clips` with: a long 16:9 video or a YouTube link.

## Every time it runs

- **Word-level timings for everything**: transcribe with `transcribe.py`, then time every word with `align.py` (MMS_FA) on the corrected text. Every graphic lands on the word it belongs to.
- **Safe zone**: keep all text out of the top 250 px and the bottom 420 px of the 1080×1920 frame (Instagram buttons and caption). Use `k.SAFE` / `k.inSafe()` in the scene.
- **Never re-grade or filter the face** unless this skill's steps say so: footage goes through `frames.sh`, which keeps the original colours, and is drawn untouched.
- **Render 1080×1920 at 30 fps with the original audio.**
- **Show 3 snapshots** (`render.cjs --stills` at three key moments) before the final render, and **ask before overwriting files** (`--force` only after a yes).

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Get the video and transcribe it.
   Link: `yt-dlp -f 'bv*[height<=1080]+ba/b' -o in/source.mp4 <url>` (only for videos the user owns or has the rights to clip).
   ```bash
   ffmpeg -i in/source.mp4 -vn -ac 1 -ar 16000 audio.wav; python3 .claude/skills/video-core/scripts/transcribe.py audio.wav . --model large-v3; python3 .claude/skills/video-core/scripts/align.py audio.wav transcript.txt align.json --windows whisper_windows.json
   ```
2. Score every moment for hook strength, a complete thought, and energy: read the transcript in 30–60 s windows that start and end on sentence boundaries; energy from loudness (`beats.py` rms) and speech rate.
3. Pick the top 5 moments, each 30–60 seconds, starting on a strong first line. Show the user the list (times, first line, why) before cutting.
4. Reframe each to 9:16 by following the speaker's face.
   ```bash
   python3 .claude/skills/youtube-clips/reframe.py in/source.mp4 <start> <end> clips/clip1   # face-tracked, smoothed 9:16 crop to a frames folder
   ```
5. Add captions and a title card for each clip.

### Approve and render

1. **3 snapshots → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w 1080 --h 1920 --data ... --stills a,b,c --stills-dir stills`, show them, wait for a yes.
2. **Render**: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>.mp4 --w 1080 --h 1920 --fps 30 --data ... --audio <original audio>`.
3. **Check**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>.mp4 --expect-audio <audio>` (add `--whatsapp out/<name>_whatsapp.mp4` if the user wants a WhatsApp copy).

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| Reel | 1080×1920 | 30 | original audio, AAC 256k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `transcribe.py`, `align.py`, `frames.sh`, `matte.py`, `vision.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `beats.py`.
In this skill's folder: `reframe.py`.
