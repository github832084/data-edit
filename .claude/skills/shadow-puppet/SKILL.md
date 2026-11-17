---
name: shadow-puppet
description: "Kids story told like tholu bommalata shadow puppets: black pin-jointed cut-out silhouettes with pattern holes on a glowing orange screen, Hindi narration lines. Use when the user runs /shadow-puppet with a story voiceover MP3 and the script."
---

# Shadow puppet

A kids story told like tholu bommalata shadow puppets: black cut-out characters with pin joints moving against a glowing orange screen.

## Run it

`/shadow-puppet` with: the story voiceover MP3 and the script.

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

1. Force-align the voiceover and split the story into scenes.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/voice.mp3 lines.txt align.json
   python3 .claude/skills/video-core/scripts/mouth.py in/voice.mp3 align.json mouth.json   # per-speaker mouth-open curve for lip sync
   ```
2. Draw every character and prop as a flat black silhouette with small cut-out holes for patterns (use `globalCompositeOperation='destination-out'` for the holes), and add pin joints so arms, legs and jaws swing (each limb is a child transform rotating around its pin; jaw angle from `mouth.json`).
3. Light the screen from behind: a warm orange glow (#ff8a1f → #b33a00) with a soft hot spot, a faint lamp flicker (`k.noise1(t*6)` on brightness, ±4 %), and the fabric texture of the screen (fine cross-weave pattern at low alpha).
4. Move the puppets with a slight wobble as if held by sticks (draw thin dark sticks to the bottom edge), and let characters come closer to the screen (sharper, `filter: blur(0)`) or move back (softer, larger, blur 4–8 px) for emphasis.
5. Put the Hindi narration line at the bottom in a clean Devanagari font (`fonts.sh noto-sans-devanagari`), with the key word in red.
6. Render 16:9.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 30 | original audio, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
