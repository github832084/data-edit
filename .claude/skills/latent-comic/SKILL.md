---
name: latent-comic
description: "India's Got Latent clip retold as a 9:16 comic book (MC Stan episode style): judges at the desk on top switching shots where the original cuts, the speaker's close-up below with a gag per line, halftone, bursts and speech bubbles. Use when the user runs /latent-comic with the show clip (MP4, MP3) and optional transcript."
---

# Latent comic

An India's Got Latent clip retold as a 9:16 comic book: the judges at the show's desk on top, a close-up of whoever is talking below with a gag for every line, halftone dots, bursts and speech-bubble captions.

## Run it

`/latent-comic` with: the show clip (MP4, plus the MP3 if you have it), the transcript if you have one, and screenshots of each judge.

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

1. Make a contact sheet of the clip, find every camera cut with ffmpeg scene detection, and work out who says each line from who holds the mic and whose mouth moves. Write the lines as SPEAKER|text.
   ```bash
   python3 .claude/skills/video-core/scripts/analyze_ref.py in/clip.mp4 ref --threshold 0.3   # cuts.json + 2 fps sheets
   ```
   Look at the sheets; if there is no transcript, run transcribe.py first and label rows with the user.
2. Force-align every word (torchaudio MMS_FA). If a line looks squeezed, re-align it inside its own time window, and cap words that stretch over a pause.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/clip.mp3 lines.txt align.json   # rows as SPEAKER|text
   python3 .claude/skills/video-core/scripts/mouth.py in/clip.mp3 align.json mouth.json   # per-speaker mouth-open curve for lip sync (--max-word 1.0)
   ```
3. Draw each judge as a comic caricature from the screenshots (hair, glasses or shades, beard, outfit) and the show's blue cube mic. Lip-sync only the person talking. The others look at the speaker and laugh on the audience laughs.
   Characters are drawn as code functions `drawX(c, pose, mood, mouth, blink)` in a `cast.js` next to the scene, so the same function draws them in every shot. Save a character sheet (`render.cjs --stills` of a sheet scene showing every pose and mood) as `cast_sheet.png` and reuse the same `cast.js` in later episodes.
   Audience laughs: loud broadband hits in `beats.py` of the clip that fall between words.
4. Top panel: the show's desk (dark curtain with a blue and red glow, phones, juice cartons, the red buzzer). Switch between the three-judge shot and the wide five-judge shot exactly at the times in `ref/cuts.json`.
5. Bottom panel: the speaker's close-up slams in fresh for every line, with a gag drawn for that line (a calendar for “3 saal baad”, a drunk globe, a range meter, a pile of shoes) and a burst word like WAAH! or HAHAHA!.
6. Captions: a comic speech bubble on the seam, 2–4 words, the tail pointing at the speaker and the spoken word in their colour. Keep everything inside the Instagram safe zone. Render 1080×1920 at 30 fps.

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

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `analyze_ref.py`, `transcribe.py`.
