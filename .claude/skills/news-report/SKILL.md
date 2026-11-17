---
name: news-report
description: "Hinglish tech-news report in Fireship style: flat dark background, recreated source cards with red boxes and highlights, memes, a hard cut every 1.5–3 s, the user as anchor. Use when the user runs /news-report with a topic or 2–3 article links, and again when they send the voice MP3."
---

# News report

A Hinglish tech-news report in Fireship style: flat dark background, screenshot cards with red boxes and highlights, memes, and a hard cut every two seconds, with you as the anchor.

## Run it

`/news-report` with: a news topic or 2–3 article links. Later: the voice MP3 and (for 9:16) 3–5 face cutouts of you (neutral, smile, shock, serious) as transparent PNGs.

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

1. Read the links, fact-check every claim against at least two sources, and write a 60-second Hinglish script: a BREAKING cold open, 2–3 stories, and a comment-keyword CTA. Give it ready for ElevenLabs v3: Hindi in Devanagari, brand names in English, [tone] tags like [excited] [serious]. List the sources under the script. Stop here until the voice MP3 arrives.
2. When the voice MP3 arrives, force-align it and plan a hard cut every 1.5–3 seconds.
   ```bash
   python3 .claude/skills/video-core/scripts/align.py in/voice.mp3 lines.txt align.json
   ```
   Place cuts on word starts: walk the words and cut at the first word boundary after 1.5 s, forcing one before 3 s. Write `cuts.json` with what each shot shows.
3. Recreate each source as a flat card (release notes, pricing table, leaderboard, tweet) on #242021, with a thin red box and an orange highlighter on the key line, then a zoom-in.
   Cards are drawn in code from the facts (never screenshots): rounded panel, system-like sans font, the key line gets an orange (#ff9f1c, 40 % alpha) marker swipe that grows left→right on its word, a 3 px red (#ff3b30) box draws on, then the camera eases in 1.0→1.35 on that line.
4. In the 9:16 version, put the user's face cutout at the bottom, changing expression with the tone of each line.
   Pick the cutout per line from its [tone] tag; it sits above the bottom safe zone and bobs slightly with `mouth.json` loudness.
5. Add sound effects on the same cues (whoosh on cuts, ding on numbers, a sting on BREAKING) and credit every source on screen.
   Small `Source: site.com` label bottom-left of every card. Mix SFX into `mix.wav` with ffmpeg `adelay`+`amix`.
6. Render 9:16 and 16:9.

### Approve and render

1. **Stills → contact sheet → OK.** `node .claude/skills/video-core/scripts/render.cjs --page scene.html --w W --h H --data align.json,beats.json,mouth.json --stills t1,t2,... --stills-dir stills` then `python3 .claude/skills/video-core/scripts/contact_sheet.py stills/sheet.jpg stills/*.png`. Show it and wait.
2. **Render** each format: `node .claude/skills/video-core/scripts/render.cjs --page scene.html --out out/<name>_<format>.mp4 --w W --h H --fps FPS --data ... --audio <original audio>`.
3. **Check and finish**: `python3 .claude/skills/video-core/scripts/finish.py out/<name>_<format>.mp4 --whatsapp out/<name>_<format>_whatsapp.mp4 --expect-audio <audio>`. Fix any FAIL line, then give the user both files.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 9:16 | 1080×1920 | 30 | original audio, AAC 256k |
| 16:9 | 1920×1080 | 30 | original audio, AAC 256k |
| WhatsApp copy (each format) | short side 720 px, under 20 MB | 30 | AAC 128k |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `align.py`, `beats.py`, `mouth.py`, `render.cjs`, `contact_sheet.py`, `finish.py`, `fonts.sh`.
