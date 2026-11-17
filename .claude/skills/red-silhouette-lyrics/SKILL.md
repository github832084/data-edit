---
name: red-silhouette-lyrics
description: "Still cinematic 16:9 lyric video (Afsos style): flat orange-red original silhouettes of a guitarist and a standing man on charcoal-green film, hard beat cuts between framings, one small centred serif phrase, rare dry-brush light strokes. Use when the user runs /red-silhouette-lyrics with a song cut, lyrics with | split marks and the title."
---

# Red silhouette lyrics

A still, cinematic 16:9 lyric video like the Afsos video: flat orange-red silhouettes of a guitarist and a standing man on a charcoal-green film background, cutting between wide, medium and close shots on the beat, with one small serif lyric phrase in the centre and dry-brush strokes of light sweeping through.

## Run it

`/red-silhouette-lyrics` with: a song MP3 (a 40–60 s cut works), its lyrics with | marks where you want each phrase to split, and the song title.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Split the lyrics at the user's | marks into short phrases (align the full lines, then split the word list at the marks) and show one phrase at a time. Write a shot table: phrase, shot, and any brush stroke.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Background: flat charcoal green (#1F2622) with a faint soft light in the middle, old-film dust specks, thin vertical scratches that flicker for a frame or two, and fine grain on everything. No gradients on the figures and no other colours.
3. Figures: draw two ORIGINAL silhouettes in code, a guitarist playing and a man standing still, in flat orange-red (#E0462E) with a light paper grain and the guitar body slightly darker. Never trace a real person or a frame from another video. They stand apart and never touch.
4. Shots: hard cuts on the beat, no fades and no camera moves. Use a small set of framings: both figures wide, guitarist medium, man medium in profile, guitarist close, a very close shot of the guitar neck and strings. Leave some phrases completely empty, just the text on the green, so the figures feel like they come and go.
5. Lyrics: one small line of serif type (EB Garamond, `fonts.sh eb-garamond`, about 54 px) in off-white, always in the centre of the frame, even when it sits over a figure. It cuts on with its sung phrase and cuts off at the end of it, with no animation at all.
6. Light strokes: a few times in the video, a dry-brush stroke of green, pink or red paint sweeps across the frame on a strong beat, drawn on along its length with rough bristle edges (many thin parallel seeded strokes with gaps), then gone. Keep them rare so each one feels like an event.
7. Ending: the last phrase sits alone on the green, a final silhouette holds, and the audio fades out over half a second. 1920×1080 at 24 fps with the song.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 24 | the song, AAC 256k |
| WhatsApp copy | 720p, under 20 MB | 24 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
