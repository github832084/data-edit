---
name: comic-rap-video
description: "Loud desi rap video drawn as a moving comic book (Maruti video style): bold cartoon rappers, a literal funny scene per line, comic panels slamming in, KRAAK/POW bursts, Hindi lyrics popping word by word in a cream caption box, kick shakes and glitches. Use when the user runs /comic-rap-video with a rap MP3, lyrics, title/artist and photos of each rapper."
---

# Comic rap video

A loud desi rap video drawn as a moving comic book, like the Maruti video: bold cartoon rappers, a new scene for every line that shows the lyric literally, comic panels slamming in, POW and KRAAK bursts, and Hindi lyrics popping word by word in a cream comic caption box.

## Run it

`/comic-rap-video` with: a rap song MP3 (a 30–60 s verse works), its lyrics, the song title and artist, and 1–2 photos of each rapper's look.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Keep ad-libs in brackets apart from the main line (align.py marks them `adlib`). Then read every line and pick one literal, funny picture for it ("road pad denge" = the road cracks open behind the car, "gobhi khod denge" = cauliflowers fly out of the field) and show the user the line-by-line scene list.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Draw the cast as your own bold cartoon caricatures from the photos, in thick black outlines and flat colours: the main rapper plus 1–2 crew members, each with their own hair, shades, beard and outfit, and 4–5 poses (hands out, pointing, mic, punch, holding a prop). Draw the props the same way: a boxy red hatchback with the song name on the door, plus anything the lyrics mention (cash, a tyre, a lathi).
   Characters are drawn as code functions `drawX(c, pose, mood, mouth, blink)` in a `cast.js` next to the scene, so the same function draws them in every shot. Save a character sheet (`render.cjs --stills` of a sheet scene showing every pose and mood) as `cast_sheet.png` and reuse the same `cast.js` in later episodes.
3. Give every line its own scene that changes the moment the line starts: sugarcane field at sunset, desert with a buggy, night plaza with a red car, purple speed-line wall, red halftone wall. On some lines, split the frame into comic panels on a dark page that slam in one by one, each on the word it shows.
4. Keep the current line in a cream (#fff4d6) comic narration box at the bottom, slightly tilted (−2°) with a thick black border, in Yatra One (`fonts.sh yatra-one`). Each word pops in exactly when it is sung, the word being sung is red and a little bigger, and sung words stay black. Put the ad-libs in small white speech bubbles beside the box, after the line.
5. Add a comic sound burst on the biggest words: a white spiky star (`k.burst` fill #fff) with the word in Bangers or Yatra One (KRAAK!, POW!, SKRRT! or the Hindi word itself), popping in and fading out in under a second. Use the song's own words whenever they work.
6. Make it hit like the track: camera shake on every kick, a small punch-in and a white flash at the start of each line, RGB split on the hits (draw the frame 3× with channel tints offset ±6 px using `lighter`), and a green digital glitch (sliced horizontal offsets + green tint) on the lines that name the car. Cover everything in light halftone, grain and a vignette, with a thick black page border.
7. Open with a yellow title tag at top left (song name and artist) that leaves after a few seconds. Near the end, line the whole crew up on a sunburst background, then finish on the main rapper slamming a prop into the ground with one last big burst and the song name in Bangers on a red burst, then fade to black. Render 1920×1080 at 30 fps with the song.

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
