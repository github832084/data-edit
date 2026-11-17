---
name: glow-lyrics
description: "Dreamy flat-vector lyric video like MITRAZ's 'Khwahish': purple dusk scenes, story silhouettes, a glowing figure in a golden birdcage, bloom on every light, the lyric line glowing in word by word. Use when the user runs /glow-lyrics with a song MP3 and lyrics."
---

# Glow lyrics

A dreamy lyric video like MITRAZ's Khwahish from Ye likho ye milega Part 7: flat vector scenes at purple dusk, silhouettes that tell the story (a boy alone on a bench, the girl he misses glowing inside a golden birdcage), soft bloom on every light, and the lyric line glowing in word by word.

## Run it

`/glow-lyrics` with: a song MP3 and its lyrics, one sung line per row.

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

1. Read every lyric line and tell the user the feeling and one picture for it, then separate the vocals and force-align every word.
2. Paint flat vector scenes in a dusk palette (deep purple #2a1a4a, violet #5b3a8c, magenta #b24592, a pale pink horizon #f7c6d9): layered clouds that drift slowly, a calm sea with thin light lines, a beach.
3. Tell the story with silhouettes and glowing figures: the singer as a dark silhouette, the person he misses as a soft white glowing figure, and one strong symbol (a golden birdcage on puppet strings) that comes back through the song.
4. Add bloom to every light source and glowing figure (draw lights to an offscreen layer, blur 24 px, add with `lighter`), plus fine grain over the whole frame. Move the camera slowly between scenes with soft cross-dissolves, never hard cuts.
5. Show the sung line at the top in a rounded font (`fonts.sh quicksand`), each word fading in white with a soft glow exactly when it is sung.
6. Render 16:9 1920×1080 and a 9:16 version with the song as the audio.

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
