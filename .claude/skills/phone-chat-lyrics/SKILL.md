---
name: phone-chat-lyrics
description: "Emotional 16:9 lyric video (Barsaat × Spider-Man style): the singer's lyrics arrive as unanswered chat messages on the hero's phone, story beats acted out by the footage, a tear that becomes the first raindrop, title behind his head, an unsent 'I love you', ending on the embrace. Use when the user runs /phone-chat-lyrics with a song cut, lyrics, title and 5–8 clips with time ranges."
---

# Phone chat lyrics

An emotional 16:9 lyric video like the Barsaat (Banjaare) Spider-Man video: the singer's lyrics arrive as chat messages on the hero's phone while he reads them and never replies, day sinks into night on the right line, an eye on pure black sheds a tear that becomes the first raindrop, the title sits behind his head, he types I love you and deletes it, and it ends on the fall and the last embrace.

## Run it

`/phone-chat-lyrics` with: a song MP3 (a 40–60 s cut works), its lyrics, the song title, and 5–8 clips with the time range you want from each (one must show someone looking at a phone).

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

1. Separate the vocals, force-align every lyric word on the vocal stem, and find the beats. Find the bar length and cut on the bars. First work out whose voice the song is in and who it is sung to, then tell the user the story in one line and write a shot table: lyric line, clip, time range, what the moment means. Use the user's time ranges exactly, and say before using anything else from a clip.
   ```bash
   bash .claude/skills/video-core/scripts/stems.sh in/song.mp3 .            # vocals.wav + no_vocals.wav
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json   # lyrics exactly as written, one sung line per row
   python3 .claude/skills/video-core/scripts/beats.py in/song.mp3 beats.json               # beats, bars, kicks, hits, per-frame loudness
   ```
   Check `align.py` warnings: re-align any squeezed line with `--windows`. Check the tempo by ear; pass `--bpm-hint` if it is off.
2. Prepare the clips first and look at them. Many vertical clips are really widescreen footage stored sideways: rotate them. Crop every clip to fill 1920×1080 with no black bars, no pillarboxing, and crop out any watermark. Flip a shot horizontally if that makes the person face the phone. Find the real cut points so no stray frame gets in. Slow shots down so they feel soft; use motion interpolation where a clip would stutter, and if something ugly crosses the lens, dissolve across it on a bar.
   ```bash
   python3 .claude/skills/video-core/scripts/analyze_ref.py in/clipX.mp4 ref/X   # cut points + 2 fps sheets
   bash .claude/skills/video-core/scripts/frames.sh in/clipX.mp4 clips/X 30 <start> <dur> "transpose=1,crop=...,hflip"   # geometry only, never colour
   python3 .claude/skills/video-core/scripts/retime.py clips/X clips/X_slow --map "0:0,<out_len>:<src_len>" --in-fps 30
   ```
3. Phone: a realistic dark phone on the right side of the frame, only in the shots where the person is looking down at it, and full-screen shots everywhere else. It eases in with blur, sits slightly tilted and breathes a little, with a soft light glow behind it. Top bar with the time, a small round photo, her name and online; a Message box at the bottom. Add one detail from the character's world (for Spider-Man, a thin spider-web crack in the glass).
4. Lyrics in the phone: every line is a grey received bubble. Typing dots (and typing… in the top bar) appear about a second before, the bubble blurs in just before the first word, and each word brightens from dim to white exactly when it is sung. Old messages stay in the chat and scroll up, so the unanswered pile keeps growing all video.
5. Full-screen lyrics in the empty side of the shot, never over a face: one font only, Optima or something equally classic (`fonts.sh marcellus` or `cormorant`), never a typical AI-looking font. Two or three rows: lead-in words in small tracked caps or italic, the one word that carries the feeling huge in a warm gold gradient. Every word eases in from a soft blur word by word on the voice and blurs out the same way, with no pops or bounces. Add a soft dark gradient behind the text only where it needs it.
6. Story beats: make the footage act out the words. When a line says night is coming, slowly sink the whole picture from day into deep blue while keeping the reds (this skill's one intended grade change). When a line is the turning point, time the action to it (he pulls his mask on at the key word and tips off the building as the line ends), and put the leaving line on the leap or a lonely swing. Put a line about being irreplaceable on the shot of their photo.
7. Eye shot: put the close-up of the eye on pure black with the lyric in the black space, and fade everything else to black. A tear swells at the corner, falls, and lands as the first raindrop, and its ripple opens into the next scene. A round shape like the moon can dissolve into the eye.
8. From there the rain grows: thin angled streaks plus refracting drops on the lens, but no rain in warm flashback shots. Cross-cut the two people alone at sunset, one shot per bar, then a warm memory shot.
9. Title on the instrumental break: on a shot of him from behind, the song title in big gold letters behind his head (cut a mask of the head so it passes in front), with a gap between the letters so his head hides none of them and the subtitle on clear sky. Add old-film dust and one thin vertical scratch.
   ```bash
   python3 .claude/skills/video-core/scripts/matte.py clips/back mattes/back --model u2net_human_seg
   ```
10. The unsent message: he finally answers. The camera pushes into the phone, he types I love you letter by letter in the Message box, the cursor waits, he deletes it letter by letter, then the top bar changes to last seen and the screen goes dark. Keep raindrops off the phone here so it reads.
11. Ending: the fall and the catch on the last lyric, the last thing we see is them holding each other, then a slow fade to black. Grain and a soft vignette on everything, a short fade in and out of the audio, 1920×1080 at 30 fps with the song.

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
