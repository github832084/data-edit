---
name: pink-spotify-clip-lyrics
description: "Poetic 16:9 lyric video (Alfaaz style): a tilted pink Spotify-style lyrics card, then meaning-led motion graphics (a self-drawing neon rose, knockout letters filled with the clip, a cinema letterbox, a dotted footstep path of letters, a split-screen ending), with the user's clips softly behind. Use when the user runs /pink-spotify-clip-lyrics with a song, lyrics, 1–3 clips with start times, cover image and Spotify logo."
---

# Pink Spotify clip lyrics

A poetic 16:9 lyric video like the Alfaaz (Hamza Malik × Zain Zohaib) video: a tilted pink Spotify lyrics card, then motion graphics that follow the meaning of each line (a rose that draws itself, letters cut out of the clip, a cinema letterbox, a dotted footstep path with the words along it, and a split screen for the last line), with your emotional clips playing softly behind the lyrics.

## Run it

`/pink-spotify-clip-lyrics` with: a song MP3 (or a clip of it), its lyrics, 1–3 emotional video clips (with the start time for each), a cover image and the Spotify logo PNG.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Read the lyrics for meaning and propose one visual idea per line or pair of lines (rose, path, kiss, stars, split), plus the section times.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Prepare the clips: trim each from the user's start time, slow them to fit their section and turn them into numbered frames so every film frame has an exact clip frame. Keep them dim and soft (darker gradient on the text side, slight blur), never brighter than the lyrics.
   ```bash
   bash .claude/skills/video-core/scripts/frames.sh in/clip1.mp4 clips/1 24 <start> <dur>
   python3 .claude/skills/video-core/scripts/retime.py clips/1 clips/1_slow --map "0:0,<section_len>:<dur>" --in-fps 24 --out-fps 30
   ```
3. Spotify card in pink: a pink card with the cover art, song title, artists and the user's Spotify logo, lyrics in big Inter bold. Tilt the card in 3D with a slow camera drift and blur the lines far from the sung one. Each word fades to white as it is sung, with a soft glow and a few spark particles.
4. Rose section: a neon pink line-art rose that draws itself stroke by stroke beside stacked lyric blocks, mixing Great Vibes script, Inter bold caps and Instrument Serif italic (`fonts.sh great-vibes inter instrument-serif`), each word blurring in on its sung time.
5. Clip sections: Spotify-style lyrics over the first clip, then big Inter 900 words with the clip showing only inside the letters (knockout: draw text, then the clip with `source-in`), ending with the camera flying through one letter into the full clip.
6. Story sections: a cinema letterbox with subtitles and one key word in pink script, then a dotted footstep path across the frame with the lyric's letters placed along it, and a soft pink glow on words like kiss or love.
7. Last line as a split screen: the clip on one side with the first half of the line, an empty dark side with the second half turning to dust (letters sampled to particles that drift away).
8. Soft blur or light-leak transitions between sections, a short fade in and out of the audio, and 1920×1080 at 30 fps with the song (plus a 4K copy if asked: `--w 3840 --h 2160`).

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

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `frames.sh`, `retime.py`.
