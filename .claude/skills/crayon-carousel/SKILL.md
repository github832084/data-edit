---
name: crayon-carousel
description: "Instagram crayon carousel (How to do this with Claude Ep 3): each 1080×1350 slide puts a Gemini crayon drawing of the user's photo on top labelled 'One day' over the real photo labelled 'Day one'. Use when the user runs /crayon-carousel with 3–10 photos and their *_drawing crayon versions."
---

# Crayon carousel

The trending crayon carousel from How to do this with Claude (Ep 3): every slide puts a crayon drawing of your photo on top, labelled “One day”, over the real photo labelled “Day one”, ready to post as an Instagram carousel.

## Run it

`/crayon-carousel` with: 3–10 of your photos, and their crayon drawings from Gemini saved next to them with _drawing at the end of the name.

## Every time it runs

- **The only generated images are the crayon drawings the user gives you.** Lay out the slides and draw the text in code (Python Pillow, `make_slides.py`).
- **Keep the person fully in frame in both halves, and never stretch an image** (crop to fill only).
- **Show the first slide before making the rest**, and ask before overwriting files.

## Setup

Fonts: `bash .claude/skills/video-core/scripts/fonts.sh caveat` (the script finds Caveat there). Put the photos and drawings in `work/crayon-carousel/<job>/in/`.

## Method

1. First give the user a Gemini prompt that redraws each photo as a colourful crayon drawing on white paper (same pose, outfit and place, bold wax-crayon strokes, a bit childlike). They make the drawings and save them next to the photos with _drawing at the end of the name.
   Prompt: `.claude/skills/crayon-carousel/gemini_prompt.md`. Stop until the drawings arrive; list any photo without a drawing and ask for it.
2. Make one 4:5 slide (1080×1350) per photo: the crayon drawing on the top half and the real photo on the bottom half, both cropped to fill, with a thin white gap (8 px) between them.
3. Crop each half around the person (find the face with OpenCV, else the body; else centre) so nobody gets cut off.
4. Write “One day” on the top-left of the drawing and “Day one” on the top-left of the photo, in a handwritten white font (Caveat) with a soft shadow so it reads on any background.
5. Export every slide as a numbered PNG, in the same order as the photos, plus one contact sheet so the user can check them all at once.

### Approve and render

1. **First slide → OK**: `python3 .claude/skills/crayon-carousel/make_slides.py in/ out/ --only 1` and show `out/slide_01.png`.
2. **All slides**: `python3 .claude/skills/crayon-carousel/make_slides.py in/ out/` (refuses to overwrite without `--force`) → `out/slide_01.png …` and `out/contact_sheet.jpg`.

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| Carousel slides | 1080×1350 PNG, numbered | — | — |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `fonts.sh`, `vision.py`, `contact_sheet.py`.
In this skill's folder: `make_slides.py`, `gemini_prompt.md`.
