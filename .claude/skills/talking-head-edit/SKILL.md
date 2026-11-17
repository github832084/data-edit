---
name: talking-head-edit
description: "Full edit of a raw 9:16 talking-head clip: word captions in the user's palette (#1f3a2c / #a8ecfc), split-screen windows showing what they name, full-screen demo cutaways on 'main dikhata hoon'/'dekho', a comment-keyword CTA; the face is never re-coloured. Use when the user runs /talking-head-edit with a 9:16 clip (plus the images, GIFs, sites, PDFs and demo videos it mentions)."
---

# Talking head edit

Your raw clip, fully edited: captions on every word, the screen splits into two windows to show what you're talking about, and demo videos play full screen. Your face is never re-coloured.

## Run it

`/talking-head-edit` with: a 9:16 talking-head clip, plus the images, GIFs, websites, PDFs and demo videos it talks about.

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

1. Prep the clip: frames, transcript and word timings.
   ```bash
   bash .claude/skills/video-core/scripts/frames.sh in/clip.mp4 clips/me 30          # stops if the clip is HDR: convert it first (see /talking-head-edit)
   ffmpeg -i in/clip.mp4 -vn -ac 1 -ar 16000 audio.wav
   python3 .claude/skills/video-core/scripts/transcribe.py audio.wav . --lang hi --model large-v3   # Hinglish/Hindi; use --lang en for English
   ```
   Show `transcript.txt` to the user if any word looks wrong, then:
   ```bash
   python3 .claude/skills/video-core/scripts/align.py audio.wav transcript.txt align.json
   ```
2. If it's iPhone HDR footage, convert it with Apple's avconvert. Never use an ffmpeg colour filter, and never change brightness or grade the face.
   `frames.sh` detects HDR (HLG/PQ) and stops. On a Mac: `avconvert --source in/clip.mov --preset PresetHighestQuality --output in/clip_sdr.mov` (or `PresetHEVCHighestQualitySDR` if available on that macOS). avconvert only exists on macOS: on Linux, stop and ask the user to convert it on their Mac or export SDR from Photos.
3. Start on the full face. When the user names a thing, move them into the bottom window and show it in the top window (image, GIF, website scroll, PDF pages), with 20 px rounded corners and no gap at the bottom. Ask for every asset named; website scrolls = a full-page screenshot the user gives you (or one taken with Playwright if they give the URL), scrolled with easing. PDF pages: `pdftoppm -r 110`. The window move eases over 0.35 s (`inOut`) on the naming word.
4. When they say “main dikhata hoon” or “dekho”, pause the clip (hold its timeline), play the demo video full screen, then carry on. The output timeline = clip time + inserted demo durations; build an edit list `edl.json` and map every caption time through it.
5. Use 2–3 word captions with the spoken word in light blue, in the user's palette: deep green #1f3a2c (caption plate) and light blue #a8ecfc (active word).
6. End with a comment-keyword CTA: a comment box typing the word (letter by letter), then a DM bubble sliding in.

### Approve and render

1. **3 snapshots → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w 1080 --h 1920 --data ... --stills a,b,c --stills-dir stills`, show them, wait for a yes.
2. **Render**: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>.mp4 --w 1080 --h 1920 --fps 30 --data ... --audio <original audio>`.
3. **Check**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>.mp4 --expect-audio <audio>` (add `--whatsapp out/<name>_whatsapp.mp4` if the user wants a WhatsApp copy).

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| Reel | 1080×1920 | 30 | original audio, AAC 256k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `transcribe.py`, `align.py`, `frames.sh`, `matte.py`, `vision.py`, `render.cjs`, `contact_sheet.py`, `finish.py`.
