---
name: red-rap-lyrics
description: "Fast rap lyric video in one red grade (Hola Amigo style): a red glass lyrics card peeling in over a tilted word wall, neon words on a rainy street with ripple reflections, a stipple particle portrait with stacked italic lyrics, a 3D word tower the camera eases through, a DAMN! slam, swear masking. Use when the user runs /red-rap-lyrics with a rap MP3, lyrics, a photo of the rapper and reference reels."
---

# Red rap lyrics

A fast rap lyric video in one red grade, like the Hola Amigo (KR$NA ft. Seedhe Maut) video: a red glass lyrics card that peels in like a page over a tilted wall of lyric words, then neon words standing on a rainy street with ripple reflections, then the rapper's photo turned into a monochrome particle portrait with stacked italic lyrics lighting up word by word, and a 3D tower of words where the camera eases to every new word, ending on a DAMN! slam.

## Run it

`/red-rap-lyrics` with: a rap song MP3 (or a clip of it), its lyrics (Hindi in Devanagari works), one photo of the rapper and your reference reels for each section.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Keep the lyrics exactly as written. Split the song into 4 sections and tell the user which lines go in each.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Analyze each reference reel at 2 frames per second and write down its fonts, sizes, colours, how words appear and the exact ease of every camera move, so each section copies its reference.
   ```bash
   python3 .claude/skills/video-core/scripts/analyze_ref.py in/ref1.mp4 ref/1 --beats beats.json   # one per reference
   ```
3. Section 1, lyrics card: a dark red glass card (cover art, song title, artists, star and dots icons) that unfolds from a page curl at the corner. Behind it, a huge tilted wall of the lyric words in deep red, drifting slowly. The lines scroll up with an ease-in-out and each word goes from dim red to glowing white exactly when it is sung.
4. Section 2, rainy street: a dark red night street with city blocks, street lamps and their light cones, rain streaks and splash ripples. Each line stands on the ground as 2–3 rows (a big bold condensed row, then a smaller row in red neon that flickers on), word by word on the voice, with a rippling reflection on the wet road below (flipped text, sine-offset slices, fading alpha). Slow push-in.
5. Section 3, particle portrait: remove the photo background and turn the rapper into 20–35k white stipple dots on a deep red-black glow. The dots fly in, breathe with the beat and drift off the edges with red and white embers. Beside him, each line as stacked italic condensed rows (Teko, `fonts.sh teko`), each row scaled to a similar width, all words dim grey first and flashing white (keywords red) when sung.
   ```bash
   python3 .claude/skills/video-core/scripts/stipple.py in/rapper.jpg dots.json --n 28000 --cutout
   ```
6. Section 4, word tower: place every word in 3D on a corner (simple 3D→2D projection in the scene), front-face words right-aligned to the corner and some words on the side face, key words big and red. On every sung word, move the camera (target, yaw, pitch, roll, distance) to that word with a smooth ease-in-out, then pull back to show the whole tower at the end of the verse.
7. End on the last ad-lib as a huge white condensed word (DAMN!) that slams in with a shake and red echo trails. Mask and mute any swear words the user names: show the first letter plus *** and replace only the voice with the instrumental stem at that moment, so the beat keeps playing (build `mix.wav`: original song, but `no_vocals.wav` inside each swear word's aligned span with 20 ms crossfades).
8. Red flash or zoom-blur cuts between sections, grain and a vignette on everything, 30 fps with the song. Render 9:16 1080×1920 and 16:9 1920×1080.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 9:16 | 1080×1920 | 30 | the song, AAC 256k |
| 16:9 | 1920×1080 | 30 | the song, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `stipple.py`, `analyze_ref.py`.
