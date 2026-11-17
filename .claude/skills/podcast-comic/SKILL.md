---
name: podcast-comic
description: "Podcast clip retold as a 9:16 comic book (Raj Shamani 'ladke ko kab jaanoge' style): the guest drawn in his studio below, a new halftone comic panel slamming in on top for every point, burst words and Hindi speech-bubble captions. Use when the user runs /podcast-comic with the clip, Devanagari transcript and guest/studio screenshots."
---

# Podcast comic

A podcast clip retold as a 9:16 comic book: the guest drawn in the studio below (bookshelf, Break the Cage poster, mic), and a new comic panel slams in on top for every point he makes, with a burst word and Hindi speech-bubble captions.

## Run it

`/podcast-comic` with: the podcast clip (MP3 or MP4), the transcript in Devanagari, and 1–2 screenshots of the guest and studio.

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

1. Split the transcript into one row per point, and force-align every word (torchaudio MMS_FA). If a line looks squeezed, re-align it inside its own time window.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/clip.mp3 points.txt align.json
   python3 .claude/skills/video-core/scripts/mouth.py in/clip.mp3 align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
   For squeezed lines: python3 .claude/skills/video-core/scripts/align.py in/clip.mp3 points.txt align.json --windows align.json --pad 0.4
2. Draw the guest as a comic character that looks like the screenshot (hair, beard, outfit) and the studio behind him (bookshelf, poster, framed wall, mic). Lip-sync him and switch his mood per line: calm, smile, angry, sad.
   Characters are drawn as code functions `drawX(c, pose, mood, mouth, blink)` in a `cast.js` next to the scene, so the same function draws them in every shot. Save a character sheet (`render.cjs --stills` of a sheet scene showing every pose and mood) as `cast_sheet.png` and reuse the same `cast.js` in later episodes.
   Look at the screenshots yourself and note hair shape, beard, glasses, outfit colours and studio layout before drawing. Draw, never trace.
3. Top panel: a new comic panel for every point (TEST #1, TEST #2 … then FINAL VERDICT), each with its own halftone colour, a drawing for that point and a burst word that pops on the key word with a sound effect.
   Panel slams down from above with `outBack` + 4 frames of shake at the point's first word. `k.halftone` in the panel colour; `k.burst` on the key word.
4. Captions: a white speech bubble on the seam between the two panels, 2–3 words, only the spoken word in red, the tail pointing at the guest.
   `k.bubble` centred on the seam (y ≈ 960), tail to the guest's mouth; `k.caption` inside with `color:'#111', hi:'#e00', strokeW:0`.
5. Keep everything inside the Instagram safe zone. Render 1080×1920 at 30 fps.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 9:16 | 1080×1920 | 30 | original audio, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
