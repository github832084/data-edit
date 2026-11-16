---
name: video-core
description: "Shared render engine for every video skill in this project (canvas scenes rendered frame by frame in headless Chrome + ffmpeg, MMS_FA forced alignment, beats, lip-sync curves, mattes, contact sheets, WhatsApp export). Use when the user runs /video-core, asks to check or install the video toolchain, or when another video skill points here."
---

# Video core

The engine every video skill in `.claude/skills/` uses. Run `/video-core` to check the machine.

## Check and install

```bash
bash .claude/skills/video-core/scripts/check_env.sh            # report
bash .claude/skills/video-core/scripts/check_env.sh --install  # fix what is missing (ffmpeg, Node, Playwright, Python packages, models)
```

Needs ffmpeg (libx264), Node ≥ 18 with Playwright Chromium, Python 3 with torch, torchaudio, uroman, openai-whisper, demucs, librosa, opencv-python, pillow, mediapipe and rembg. Models download once: MMS_FA (download.pytorch.org), demucs (dl.fbaipublicfiles.com), Whisper (openaipublic.azureedge.net), MediaPipe (storage.googleapis.com). Fonts come from npm `@fontsource/*` packages (`fonts.sh`), never from a font CDN.

## Pipeline every skill follows

1. **Timing** (never guessed)
   - `transcribe.py`: Whisper large-v3 transcript. Show it to the user and let them fix words.
   - `align.py`: MMS_FA word times on the corrected text. Supports Devanagari, `SPEAKER|text` rows, `(ad-libs)` and per-line `--windows`.
   - `stems.sh`: demucs vocals and instrumental. Align lyrics on the vocals.
   - `beats.py`: beats, bars, quarter beats, kicks, hits and loudness.
   - `mouth.py`: per-speaker lip-sync curves.
2. **Footage prep**
   - `frames.sh`: JPEG sequences, colours untouched, refuses HDR.
   - `matte.py`: person cutouts plus `bounds.json`.
   - `retime.py`: piecewise retiming with optical-flow in-betweens.
   - `analyze_ref.py`: cuts, cut grid and 2 fps sheets of a reference reel.
   - `paint_out.py`: watermark removal.
   - `stipple.py`: particle portraits.
   - `vision.py`: face boxes and person masks.
3. **Scene**: copy `templates/scene.html`. It loads `lib/kit.js`, which has captions, easing, halftone, speed lines, bursts, bubbles, wobble/boil strokes, grain, vignette, blinks, mouths and the safe zone. Everything in a scene is a pure function of `t`: no `Date`, `Math.random` or CSS animation.
4. **Approve**: `render.cjs --stills t1,t2,…`, then `contact_sheet.py`. Show the user and wait for an OK.
5. **Render**: `render.cjs --out … --audio …`. It uses parallel workers and refuses to overwrite without `--force`.
6. **Finish**: `finish.py` checks streams, duration and black frames, then makes the WhatsApp copy (720p, under 20 MB).

## Scene contract

```html
<script src="/kit/kit.js"></script>
<script>
Kit.scene({
  async setup(k) { await k.fontsource('inter', 'Inter', [400, 900]); k.ws = k.words(k.data.align); },
  duration: (k) => k.data.align.duration,
  async draw(c, t, k) { /* draw frame at time t on canvas context c (k.W × k.H) */ },
});
</script>
```

`render.cjs --data a.json,b.json` exposes each file as `k.data.<basename>`. Paths in the page are served from the project root; `/kit/` is this `lib/` folder and `/fonts/` is `fonts/`.
