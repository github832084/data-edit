---
name: split-screen-ldr-lyrics
description: "60 s 16:9 anime long-distance lyric video (Aaoge Tum Kabhi style): a split-screen couple waking at the same second, a 'Good morning' that flies across the seam, lyrics on his wall, joined walking legs, then him alone through a year of seasons with huge lyrics behind his cutout, ending on a player. Use when the user runs /split-screen-ldr-lyrics with the song (cut points), lyrics and their Flow images and clips."
---

# Split screen LDR lyrics

A 60 s 16:9 anime lyric video like the Aaoge Tum Kabhi video: a long-distance couple wakes up at the same second in a split screen (his side dull and grey, hers bright), she sends a cold “Good morning” that flies across the split onto his phone, the first line writes itself on his wall, their two legs walk as one pair, then he walks alone through a whole year of seasons with big lyrics behind him, ending on a Spotify-style player.

## Run it

`/split-screen-ldr-lyrics` with: the song MP3 (with your cut start and end), the lyrics, and your Flow images and clips (his and her wake-up, waiting, walk-loop and full-body clips, the season clips, the fog clip, album art).

## Every time it runs

- **The only generated images and clips are the ones the user makes** from the prompts this skill gives them (Gemini / Google Flow). Everything else — cutting, joins, lyrics, overlays and the render — is done in code: a canvas page rendered frame by frame in headless Chrome (`render.cjs`), encoded with ffmpeg.
- **If an image or clip is missing, ask for it. Never use a placeholder.**
- **Never guess timings**: every word comes from `align.py` (torchaudio MMS_FA) on the vocal stem.
- **Show a contact sheet** of stills before the full render, and **ask before overwriting files**.
- **Deliver** the MP4 with the song, plus a smaller copy for WhatsApp (`finish.py --whatsapp`, under 20 MB).
- Lyrics never sit on top of a character's face or body: behind the cutout, above the head, or on the floor.
- His side stays dull and drained, her side bright; never regrade the clips beyond that.

## Setup

**Before the first run on a machine:** `bash .claude/skills/video-core/scripts/check_env.sh` (add `--install` to fix what is missing).
Work in `work/<skill>/<job>/` (gitignored): put the user's files in `in/`, data in the job folder, stills in `stills/`, renders in `out/`.
Start the scene from `.claude/skills/video-core/templates/scene.html` and the drawing kit `video-core/lib/kit.js` (captions, easing, halftone, speed lines, bursts, bubbles, wobbly strokes, grain, vignette, blinks, lip-sync, safe zone). Install fonts with `bash .claude/skills/video-core/scripts/fonts.sh <font-slug>...` and load them with `k.fontsource(...)`.

## Method

1. Separate the vocals and force-align every word of the lyrics on the vocal track, exactly as written. Cut the song where the user says (e.g. 0:19 to 1:19: the story plays on the music, the first word lands at 0:40). Show a minute-by-minute table of scenes against the lyric times before you build.
   ```bash
   ffmpeg -ss 19 -to 79 -i in/song.mp3 song_cut.wav
   bash .claude/skills/video-core/scripts/stems.sh song_cut.wav .
   python3 .claude/skills/video-core/scripts/align.py vocals.wav in/lyrics.txt align.json
   python3 .claude/skills/video-core/scripts/beats.py song_cut.wav beats.json
   ```
2. Paint out the small Flow sparkle watermark in every clip, turn the clips into frames, and make contact sheets of each one. Note any place Veo cut or zoomed inside a clip and use it on purpose.
   ```bash
   bash .claude/skills/video-core/scripts/frames.sh in/X.mp4 clips/X 24; python3 .claude/skills/video-core/scripts/paint_out.py clips/X clips/X --corner br; python3 .claude/skills/video-core/scripts/analyze_ref.py in/X.mp4 ref/X
   ```
3. Scene 1, split screen: his wake-up clip in the left half and hers in the right, each cropped to keep the person centred, his side graded dull and desaturated (canvas `filter: saturate(0.35) brightness(0.9)`), hers bright and vivid (`saturate(1.15)`). A thin white seam between them. The alarm rings on both on the first big beat.
4. Scene 2, phones: both halves blur and a phone rises in each. Her chat: she types a long sorry message, deletes it, types only Good morning and sends. His chat shows typing… and his messages from last night. The Good morning bubble flies in an arc across the seam into his phone. Then his face, a small smile, and the seam slides right and pushes her out of frame.
5. Scene 3, the wall: his smile fades, he leans back, the camera rises to the empty sunlit wall, and the first line writes itself there word by word in pencil handwriting, multiplied into the wall (`globalCompositeOperation='multiply'`).
6. Scene 4, legs: his walk-loop clip in the left half and hers in the right, cut at the centre so his back leg and her front leg read as one person walking. Then a small cut to full bodies, still split: him alone and sad, her laughing with the other man. Next line in thin condensed caps between them, then the seam pushes her out.
7. Scene 5, a year passes: chain the season clips (summer, monsoon, October, Diwali night, fog) with short dissolves so it feels like one walk. Make a person cutout for every frame and put the big words BEHIND him: the first chorus as one huge word at a time (AAOGE, then TUM), KABHI in the album red above his head, the next line above his head, “gaayegi yeh zameen” painted on the floor in perspective and sliding with the street, and AASMAAN huge in the sky behind him. Where a cutout edge looks wrong, move that line above his head instead.
   ```bash
   python3 .claude/skills/video-core/scripts/matte.py clips/summer mattes/summer --model isnet-anime   (per season clip)
   ```
8. Scene 6, ending: he stops in the fog and takes out his phone; the last AAOGE sits in front of him, then push into the phone: a red Spotify-style player with the song's album art and the last line lit word by word, then fade to black.
9. Mix: the song plus quiet phone sounds (alarm, typing, send, receive), his side panned left and hers right (ffmpeg `pan` + `amix` into `mix.wav`). Render a 1080p MP4 at 24 fps.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 24 | song + phone SFX mix, AAC 256k |
| WhatsApp copy | 720p, under 20 MB | 24 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `stems.sh`, `align.py`, `beats.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`, `frames.sh`, `paint_out.py`, `matte.py`, `analyze_ref.py`.
