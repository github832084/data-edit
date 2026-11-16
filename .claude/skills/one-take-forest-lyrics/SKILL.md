---
name: one-take-forest-lyrics
description: "Seamless 16:9 one-take lyric video (Iss Tarah style): Flow clips retimed and joined with no visible cuts, big Hindi hero words placed between the forest and the people (matte + camera track) moving with their meaning, a TV-zoom देखा moment, and a gold-particle ending. Use when the user runs /one-take-forest-lyrics with the song, lyrics and their Flow clips."
---

# One take forest lyrics

A seamless 16:9 lyric video like the Iss Tarah video: Google Flow clips joined into one take with no visible cuts, Hinglish lines with big Hindi hero words sitting behind the characters in the forest, every word moving with its meaning, and a sad ending where she turns to gold particles.

## Run it

`/one-take-forest-lyrics` with: the song MP3, the lyrics, and your Flow clips.

## Every time it runs

- **The only generated images and clips are the ones the user makes** from the prompts this skill gives them (Gemini / Google Flow). Everything else — cutting, joins, lyrics, overlays and the render — is done in code: a canvas page rendered frame by frame in headless Chrome (`render.cjs`), encoded with ffmpeg.
- **If an image or clip is missing, ask for it. Never use a placeholder.**
- **Never guess timings**: every word comes from `align.py` (torchaudio MMS_FA) on the vocal stem.
- **Show a contact sheet** of stills before the full render, and **ask before overwriting files**.
- **Deliver** the MP4 with the song, plus a smaller copy for WhatsApp (`finish.py --whatsapp`, under 20 MB).
- Never change the colour grade of the clips.
- Show a contact sheet of stills, **and frame strips across every join** (5 frames either side), before the full render.

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Find the true tempo and the bars, and check it by ear because beat trackers can be off by a few BPM (`--bpm-hint`).
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Look at contact sheets of every clip and list the moments that matter. Retime each clip with a piecewise map so its events land on the words, with optical-flow in-betweens for the slow parts. Skip any bad frames at the start or end of a clip, such as a reference sheet or a jump to another shot.
   ```bash
   python3 .claude/skills/video-core/scripts/analyze_ref.py in/X.mp4 ref/X
   bash .claude/skills/video-core/scripts/frames.sh in/X.mp4 clips/X 24
   python3 .claude/skills/video-core/scripts/retime.py clips/X clips/X_rt --map "0:0,3.2:2.1,6.0:5.4" --in-fps 24 --out-fps 30 --skip-start 2
   ```
3. Make a person matte for every frame (u2net human seg) and a camera track of the background. Draw the lyrics between the forest and the people, so characters walk in front of the words, and lock the words to the world so they move with the camera.
   ```bash
   python3 .claude/skills/video-core/scripts/matte.py clips/X_rt mattes/X --model u2net_human_seg
   python3 .claude/skills/one-take-forest-lyrics/track_bg.py clips/X_rt mattes/X track_X.json   # per-frame background similarity transform (tx, ty, scale, rot), people masked out
   ```
4. Fonts: Rozha One for the big Hindi hero words, Playfair Display Italic for the Hinglish lines (`fonts.sh rozha-one playfair-display`). Cream text with a two-pass dark shadow, so it reads on the bright sky. Measure where the bodies stand from the mattes (`bounds.json`) before placing any word, and keep lines off faces.
5. Give each hero word its own move from its meaning: दुआ rises from his open hands, सजदा bows flat to the ground, मीरा splits into मी and रा and opens around her, jhanke shakes on the beat, agar trembles, जाना burns into the light, and bhar lo rotates in a ring around them.
6. Joins: every clip change must keep the same object in the same place. Measure the TV or his face on both sides of the join (`track_bg.py --point x,y` gives that point's path), then move and scale each shot so it stays locked through the join and eases back afterwards. Hide what is left with dust, petals or a flash.
7. देखा moment: freeze the TV frame, turn her into pixel particles while the screen goes white with the word on it, zoom into the screen, then zoom out of the blank TV in the next clip as she climbs out.
8. Ending: keep the music on the beat if the clips need extra seconds, by reusing the instrumental from whole bars earlier (splice `no_vocals.wav` bars into `mix.wav` at bar boundaries). Finish on his small smile, then fade to white with the song title.

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

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `frames.sh`, `retime.py`, `matte.py`, `analyze_ref.py`.
In this skill's folder: `track_bg.py`.
