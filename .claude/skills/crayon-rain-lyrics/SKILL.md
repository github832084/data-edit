---
name: crayon-rain-lyrics
description: "Quiet sad 16:9 lyric video (Finding Her style): a minimal crayon world in slow rain built from the user's Flow images and clips, handwritten Hindi lyrics, a thought bubble into her spring, lyrics on the wet road behind a walking matte, a phone lyrics player, lightning in his room, and an unread chat. Use when the user runs /crayon-rain-lyrics with the song, Devanagari lyrics and their Flow images and clips."
---

# Crayon rain lyrics

A quiet, sad 16:9 lyric video like the Finding Her video: a minimal crayon world in slow rain, handwritten Hindi lyrics that write on word by word, a thought bubble that opens into her spring, lyrics lying on the wet road, a phone player whose lyrics fill word by word with sparkles, lightning in his room with glowing words on the wall, and a chat she never reads.

## Run it

`/crayon-rain-lyrics` with: the song MP3, the lyrics in Devanagari, and your images and Flow clips (walk clip, her spring clip, bus stand image, phone close-up, bedroom image, her portrait).

## Every time it runs

- **The only generated images and clips are the ones the user makes** from the prompts this skill gives them (Gemini / Google Flow). Everything else — cutting, joins, lyrics, overlays and the render — is done in code: a canvas page rendered frame by frame in headless Chrome (`render.cjs`), encoded with ffmpeg.
- **If an image or clip is missing, ask for it. Never use a placeholder.**
- **Never guess timings**: every word comes from `align.py` (torchaudio MMS_FA) on the vocal stem.
- **Show a contact sheet** of stills before the full render, and **ask before overwriting files**.
- **Deliver** the MP4 with the song, plus a smaller copy for WhatsApp (`finish.py --whatsapp`, under 20 MB).
- Keep the movement slow and calm, with smooth ease-out on every transition. Only one hard cut (into the dark room).

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Split the song into 5 scenes (rain walk, her spring, bus stand and phone, sleepless room, chat) and show the user which lines go in each scene before you build.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Paint out the small Gemini sparkle watermark in every image and clip, and turn the clips into 30 fps frames. Never change their colours.
   ```bash
   bash .claude/skills/video-core/scripts/frames.sh in/walk.mp4 clips/walk 30
   python3 .claude/skills/video-core/scripts/paint_out.py clips/walk clips/walk --corner br
   python3 .claude/skills/video-core/scripts/paint_out.py in/busstand.png in/busstand.png --corner br
   ```
3. Scene 1, rain walk: the walk clip full screen with soft crayon rain drawn on top. The first line writes on word by word in big cream crayon handwriting in the open space at the top right. The second line lies on the wet road in street perspective and slides with the ground; make a person matte for every frame so he walks over the words. On the word about dreams, three small dots rise from his head and puff into a crayon thought bubble with her portrait inside, and the camera eases toward it.
   ```bash
   python3 .claude/skills/video-core/scripts/matte.py clips/walk mattes/walk --model u2net_human_seg   # draw: frame → road words → frame clipped by matte
   ```
   Road perspective: draw the text into an offscreen canvas, then draw it row by row with shrinking width toward the vanishing point, offset by the ground's scroll speed.
4. Scene 2, her spring: the camera flies into the bubble until her spring clip fills the frame. Add a few falling petals and write the lines in the sky in graphite with one key word in rose pink. At the end, wash the colour out to rainy grey-blue and dissolve to the bus stand.
5. Scene 3, bus stand: write the start of the line in chalky crayon above the shelter, kept clear of the streetlamp, and lay the last words on the wet road in perspective. Then push into the phone, dissolve through the phone close-up, and show a Spotify-style now-playing screen with a teal lyrics card. The current line fills word by word in white with a soft glow and small sparkles lifting off each word, and the card scrolls with the song.
6. Scene 4, hard cut on the first word to the dark room: darken the bedroom image and flash it back to full brightness on 4 key words, like lightning. Scratch the lyrics onto the empty wall in chalk, one word at a time, with a soft blue-white glow that gets brighter in every flash.
7. Scene 5, chat: a WhatsApp-style dark chat on a phone over the blurred room. Her name and her portrait as the picture, last seen on an old date, her old voice note playing with the playhead moving. His lyrics appear as green messages that fill word by word, each with a single grey tick. On the last word the voice note stops, the screen dims, and it fades to black after a 2 second tail.

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

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `frames.sh`, `paint_out.py`, `matte.py`.
