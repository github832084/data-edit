---
name: minimal-love-lyrics
description: "Calm minimal 16:9 lyric video like Ashu Shukla's 'Tumhare Aane Se': a dark maroon page with grain, stacked type per line (small white script, one huge coral serif key word, small row below) and a tiny white line icon drawing itself beside it. Use when the user runs /minimal-love-lyrics with a song, lyrics, title and artist."
---

# Minimal love lyrics

A calm, minimal 16:9 lyric video like Ashu Shukla's Tumhare Aane Se from Ye likho ye milega: a dark maroon page with soft grain, every line set as stacked type (a small white script row, one big coral serif word, a small row below) and a tiny white line icon that draws itself beside the words.

## Run it

`/minimal-love-lyrics` with: a song MP3 (or a clip of it), its lyrics and the song title + artist.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. For every line pick the one key word that carries the feeling, and one small icon that shows it.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Page: a dark maroon background (#3b0d16) with a soft lighter glow in the centre, a strong vignette, fine film grain and a few slow drifting specks of dust. Nothing else; the words are the video.
3. Opening: the song title in a coral script font fades in, then the artist name in small thin spaced caps, then both fade out before the first word.
4. Lyrics as a stacked block in the centre: the lead-in words in a small white handwritten script, the key word huge in a coral (#ff7f6e) serif italic (Abril Fatface or Playfair Italic), and the rest of the line in a medium white serif below. Every word blurs in and rises a little exactly when it is sung, and the whole block breathes slightly on the beat.
5. Icons: one thin white line icon per line, drawn on stroke by stroke beside the block (a door that swings open on 'aane', a sun on 'din', two hearts, a paper plane flying a dotted arc, a clock, a couple holding hands). Keep them small and simple, like doodles in a diary.
6. Between lines the block blurs out and the next one blurs in. A short fade in and out of the audio, 1920×1080 at 30 fps with the song.

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
