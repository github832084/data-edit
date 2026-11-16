---
name: watercolor-lyrics
description: "Soft lyric video like Ashu Shukla's 'Phir Se Shuru': the camera pans right across warm paper while autumn watercolour images of one couple reveal (ink lines first, then the wash blooms), leaves fall, lyrics wipe on word by word. Use when the user runs /watercolor-lyrics with a song MP3, lyrics and 10–14 watercolour images (or asks for the image prompts)."
---

# Watercolor lyrics

A soft lyric video like Ashu Shukla's Phir Se Shuru from Ye likho ye milega Part 7: the camera pans right across warm paper while autumn watercolour scenes of one couple draw themselves in (ink lines first, then the wash blooms), leaves fall, and the lyric lines write on word by word.

## Run it

`/watercolor-lyrics` with: a song MP3, its lyrics, and 10–14 watercolour images of the same couple (ask Claude for the image prompts first).

## Every time it runs

- **Draw everything in code**: one `scene.html` canvas page per job, rendered frame by frame in headless Chrome by `render.cjs` and encoded with ffmpeg. No stock footage and no image generators, so the look is the same every time. Files the user attaches (photos, clips, logos) are the only outside pictures allowed.
- **Never guess timings.** Every word, cut and effect is keyed to `align.json` from `align.py` (torchaudio MMS_FA forced alignment) or to `beats.json` from `beats.py`.
- **Show a contact sheet first**: render 8–12 stills across the video (`render.cjs --stills`), tile them with `contact_sheet.py`, show the user, and wait for an OK before the full render.
- **Ask before overwriting files.** `render.cjs` and `finish.py` refuse to overwrite without `--force`; only pass it after the user says yes.
- **Deliver** the master MP4 with the original audio, plus a 720p copy under 20 MB for WhatsApp (`finish.py --whatsapp`).
- The only outside pictures are the user's watercolour images; everything else (paper, leaves, reveals, text) is drawn in code.

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Read the lyrics and plan one scene per line or pair of lines. Write image prompts for each scene that keep the same couple and outfits (her mustard sweater and maroon scarf, his brown corduroy jacket) in an autumn watercolour style, and give them to the user. Wait for the images; if one is missing, ask for it — never use a placeholder.
2. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Find the chorus repeats so they reuse the same timing pattern.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
3. Lay the scenes along one long sheet of warm textured paper and move the camera slowly and constantly to the right.
4. Reveal every image like a painting: the ink lines draw in first (Canny edges of the image, `cv2` in a prep script, drawn on as a mask that grows), then the watercolour wash blooms outward from the middle (radial mask with a noisy edge). Add a few maple leaves falling across the frame.
5. Write each lyric block in Amatic SC (`fonts.sh amatic-sc`) next to its scene, wiping on word by word as it is sung. Place each block where it doesn't cover a face (find faces with OpenCV on each image).
6. Render 16:9 1920×1080 with the song as the audio, in chunks (`--from/--to`) if it is long.

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
