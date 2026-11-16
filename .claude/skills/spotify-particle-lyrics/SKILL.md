---
name: spotify-particle-lyrics
description: "16:9 lyric video in four looks (Kalyani style): a tilted Spotify-style lyrics card with spark bursts on sung words, a monochrome stipple particle portrait that morphs into a second photo with red/white side lyrics, gold motion-graphic lyrics, and a rain-on-glass music player ending. Use when the user runs /spotify-particle-lyrics with a song, lyrics, 1–2 photos, the Spotify logo PNG and a reference reel."
---

# Spotify particle lyrics

A 16:9 lyric video in four looks, like the Kalyani (ARJN × KDS × Fifty4 × Ronn ft. Shreya Ghoshal) video: a tilted Spotify lyrics card where every sung word lights up with glowing sparks, then the artists' photo turned into a monochrome particle portrait that morphs into a second photo while red-and-white lyrics pop on the right and dance on the beat, then gold motion-graphic lyrics with fast blur word changes for the singer's part, and a black-and-white rain-on-glass music player to end.

## Run it

`/spotify-particle-lyrics` with: a song MP3 (or a clip of it), its lyrics, 1–2 photos (the artists, and a second photo to morph into), the Spotify logo PNG and a reference reel for the motion-graphic part.

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Use beats and kicks. Tell the user which lines are rap and which are sung, and propose the sections: Spotify card → particles → Spotify again → motion graphics → rain ending.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Analyze the reference reel at 2 frames per second and write down its fonts, colours, word timing, transitions and camera moves, so the motion-graphic part copies that style.
   ```bash
   python3 .claude/skills/video-core/scripts/analyze_ref.py in/reference.mp4 ref --beats beats.json
   ```
3. Spotify card: a deep maroon card with the cover art, song title, artists and the user's Spotify logo (white behind its transparent bars), lyrics in big Inter bold (`fonts.sh inter`). Tilt the card in 3D (canvas `setTransform` with a perspective-like skew + scale) with a slow camera drift and blur the lines far from the sung one. Each word fades from dark to white with an ease-in-out as it is sung, with a soft glow, a burst of spark particles from across the word, small cross glints and a light point that rides along the word.
4. Particle portrait: remove the photo backgrounds, then turn each one into 20–25k stipple dots (local contrast + edges so the faces read) in white on near-black. Dots breathe with the beat and drift with red and white embers. On a chosen word, morph every dot from the first photo into the second with a fast staggered swirl and a flash ring. At the end, blow the dots apart. No artist names on screen.
   ```bash
   python3 .claude/skills/video-core/scripts/stipple.py in/photo1.jpg dots1.json --n 22000 --cutout --seed 1
   python3 .claude/skills/video-core/scripts/stipple.py in/photo2.jpg dots2.json --n 22000 --cutout --seed 1   # same n -> dot i pairs with dot i
   ```
   Draw dots with fillRect (fast); 22k dots per frame is fine in Chrome.
5. Right-side lyrics during the particles, like the Let Me Love You kinetic video: rows alternating Inter 900 white caps and Instrument Serif italic red (`fonts.sh instrument-serif`), each word popping in with a small overshoot on its sung time, letters bouncing on every beat, and each block blurring out before the next.
6. Motion graphics for the sung part in the reference style: gold serif words stacked and changing fast with a blur in and out, a moon on a starfield, and a curved lyric wall that turns like a cylinder (x = R·sin θ, scaleX = cos θ). Show each lyric only once on screen, never a duplicate big word.
7. Rain ending: a blurred black-and-white music player (cover card, progress bar, lyric rows lighting up as sung) seen through glass, with hundreds of small water drops that each refract the scene (draw a flipped, magnified patch of the blurred player inside each drop circle), a few running drops with trails, grain and a vignette.
8. White flash or blur cuts between sections, a short fade in and out of the audio (`afade` in the final mux), and 1920×1080 at 30 fps with the song.

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

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `stipple.py`, `analyze_ref.py`.
