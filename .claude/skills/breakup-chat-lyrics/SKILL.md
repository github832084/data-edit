---
name: breakup-chat-lyrics
description: "16:9 heartbreak lyric video (Choo Lo style): a red glass music card plays out a breakup chat during the intro, becomes a karaoke lyrics card over a giant red word wall, shatters into clips with lyrics in the sky, burns the title in fire letters, and ends in pink neon rain with a falling star. Use when the user runs /breakup-chat-lyrics with a song, lyrics, cover art, 3–6 clips/photos and 2–4 chat lines."
---

# Breakup chat lyrics

A 16:9 heartbreak lyric video like the Choo Lo (The Local Train) video: during the instrumental intro, a red glass music card plays out a breakup chat (your message, “Read”, typing dots, her reply), then turns into a karaoke lyrics card over a wall of giant red words, shatters into full-screen clips with the lyrics in the empty sky, burns the song title in fire inside giant cut-out letters, and ends in pink neon with rain and a falling star.

## Run it

`/breakup-chat-lyrics` with: a song MP3 (or a 40–60 s cut), its lyrics, the cover art, 3–6 clips or photos for the mood, and the 2–4 chat lines you want in the intro.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Find the length of the instrumental intro (time of the first aligned word). Split the song into parts: chat intro, glass card, clips, fire title, neon ending. Tell the user which clip goes with which lines and use every clip only once.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Chat intro (during the instrumental, before the first word): a dark red frosted-glass card with the cover art, song title and artist like a music app, tilted slightly in 3D. Inside it, play a chat like a real phone: the user's red bubble pops in with a soft bounce, a small “Read” appears under it, then three typing dots, then her grey reply slides in. Space the messages across the intro so the last one lands a beat before the vocals, then blur the chat away.
3. Glass card: the same card becomes the lyrics screen. Each word fills from dim to bright exactly when it is sung, the next line waits blurred below, and a soft shine sweeps across on every line change. Behind it, a slow scrolling wall of the lyric words in giant deep-red caps.
4. Crack the card with thin light lines, then shatter it into glass shards flying toward the camera with a red bloom into the clips.
5. Clips: each one full-screen in its natural colours with a slow push-in. Place the lyrics in the empty space (the sky above a person, the ground below a horizon, never over a face): a small tracked caps row, one big Inter 800 caps row and one word in pink script that writes itself on, all word by word on the voice. Make still photos alive: twinkling stars, a shooting star, drifting clouds or light.
   Prepare clips: watch each at 2 fps (`python3 .claude/skills/video-core/scripts/analyze_ref.py in/clipX.mp4 ref/clipX`), list usable moments, then cut frames with `bash .claude/skills/video-core/scripts/frames.sh in/clipX.mp4 clips/X 30 <start> <dur>`. Horizontal clips only for 16:9; never pillarbox.
6. Fire title: during the instrumental break, cut the song title out of black as giant Inter 900 letters with the band name above in small tracked caps, so a fire clip burns only inside the letters. Then let the letters grow until the fire fills the screen. (Ask the user for a fire clip; if none, draw the fire in code with layered noise flames.)
7. Pink neon ending: every clip in a pink duotone, darker at the bottom. Lyric words drop in one by one, flicker on like a neon sign and land with a splash ripple on a wet floor that mirrors them. Add light rain, one falling star near the end, and finish on the song title in glowing neon script, then fade out.
8. Grain and a soft vignette on everything, white flashes or red burns between parts, a short fade in and out of the audio, 1920×1080 at 30 fps with the song.

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
