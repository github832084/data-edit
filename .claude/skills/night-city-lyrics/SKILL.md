---
name: night-city-lyrics
description: "Dreamy 16:9 lyric video like MITRAZ's 'Akhiyaan': an opening drawn eye with the title, two eyes under the moon, silhouettes on a purple hill, gold handwritten lyrics writing along a glowing line through a night city of lit windows, a pink bokeh sunset where the two meet. Use when the user runs /night-city-lyrics with a song, lyrics, title and artist."
---

# Night city lyrics

A dreamy 16:9 lyric video like MITRAZ's Akhiyaan from Ye likho ye milega: an opening drawn eye with the song title, two eyes looking at each other under the moon, two silhouettes walking on a purple hill, gold handwritten lyrics that write themselves along a glowing line through a night city of lit windows, and a pink bokeh sunset where the two silhouettes finally meet.

## Run it

`/night-city-lyrics` with: a song MP3 (or a clip of it), its lyrics and the song title + artist.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Read the lyrics and tell the user the love story in one line (who is missing whom, where they meet) before you build.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Opening, during the intro: one small star of light in the black that stretches into a thin line, then opens into a big hand-drawn eye with a starry iris and lashes; the song title in thin spaced caps fades in under it. Then two smaller eyes side by side under a full moon, glancing at each other on the first lines.
3. Draw every scene flat, in silhouettes and soft gradients: a purple dusk hill with two small people walking, a night city skyline made of hundreds of tiny lit windows that flicker on one by one, a pink-orange sunset full of soft bokeh circles, and a cream paper page with simple line drawings (two teacups, a polaroid, two hands making a heart) for the memory lines. Pick the scene that fits each line.
4. Lyrics: a handwritten script font in warm gold (`fonts.sh sacramento` or `dancing-script`) with a soft glow. Each word writes itself on when it is sung, sitting on a thin glowing line of light that curves through the scene like a path (place glyphs along a spline with rotation from its tangent); older words fade a little as new ones come. Keep the words in the empty sky or on the path, never over the people.
5. Story beats: on the chorus the two silhouettes walk toward each other from both sides of the sunset, a tiny eye floats between them, and they stop close on the last line. Slow camera drift and soft crossfades between scenes, light dust and stars drifting.
6. A short fade in and out of the audio, 1920×1080 at 30 fps with the song.

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

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
