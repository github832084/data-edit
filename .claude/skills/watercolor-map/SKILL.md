---
name: watercolor-map
description: "Painted watercolor world map route animation built in Remotion with real world-atlas data: a pin drops on the start city, a plane flies the real great-circle route with a dashed red trail, the destination washes in. Use when the user runs /watercolor-map with two places like 'Bengaluru → California'."
---

# Watercolor map

A painted watercolor world map: a pin drops on the start city, a plane flies the real great-circle route, and the destination washes in with colour.

## Run it

`/watercolor-map` with: two places, like “Bengaluru → California”.

## Every time it runs

- **Build it in Remotion.** Animate only with `useCurrentFrame()` and `interpolate()` / `spring()`, never CSS animations or transitions.
- **Use real map data** (world-atlas TopoJSON) **and the real great-circle route** from `d3.geoInterpolate`, never a hand-drawn line.
- **Show 5 stills** across the video (`npx remotion still` at 5 frames) before the full render, and ask before overwriting files.
- **Render 1920×1080 at 30 fps**, and a 1080×1920 version if the user asks.

## Setup

Copy the project template once per job: `cp -r .claude/skills/watercolor-map/template work/watercolor-map/<job>` then `npm install` inside it (Remotion, d3-geo, topojson-client, world-atlas and the Caveat font, all from npm). If Remotion cannot download its own browser, point it at an installed Chromium: `export REMOTION_CHROME=/path/to/chrome`.

## Method

1. Set up a Remotion project with d3-geo, topojson-client and world-atlas.
   The template in this folder already has them. Put the two places and their coordinates in `src/route.json`: look the coordinates up in `cities.json` (in this folder); for a place that is not there, use its well-known coordinates and add it to `cities.json`. Distance = great-circle km (`d3.geoDistance × 6371`).
2. Fit a map projection around the route and paint every country as an uneven watercolor wash using SVG turbulence, displacement and edge-pooling filters, with paper grain on top.
   `geoNaturalEarth1().fitExtent()` on a GeoJSON MultiPoint of the route plus 25 % padding. The template's `<Watercolor>` filter = feTurbulence → feDisplacementMap (uneven edges) + an inner darker edge from feMorphology/feComposite (pooling) + a paper grain feTurbulence overlay.
3. Draw the great-circle route with d3's geoInterpolate and fly a small plane along it, turned to its heading, leaving a dashed red trail.
   Sample `geoInterpolate(a,b)` at 200 points; plane position = projected point at progress p, heading = angle to the point at p+0.005. Trail = the sampled path up to p with `strokeDasharray`.
4. Camera: start close on the first city, zoom out to follow the plane, then zoom into the destination.
   Camera is a transform on the map `<g>`: scale and translate from `interpolate(frame, [...], [...], {easing: Easing.inOut(Easing.cubic)})`.
5. Add handwritten labels for both places, a running km counter, and an end title card.
   Labels in Caveat (from the `@fontsource/caveat` npm package, so no font CDN is needed); km counter = `Math.round(interpolate(...))` formatted with commas.

### Approve and render

1. **5 stills → OK**: `npx remotion still src/index.ts Map out/still_<n>.png --frame=<n>` for 5 frames spread across the video, tile them with `python3 .claude/skills/video-core/scripts/contact_sheet.py out/sheet.jpg out/still_*.png`, show the user and wait.
2. **Render**: `npx remotion render src/index.ts Map out/map_16x9.mp4` (and `MapVertical` for 1080×1920 if asked). Refuse to overwrite an existing file without a yes.
3. **Check**: `python3 .claude/skills/video-core/scripts/finish.py out/map_16x9.mp4 --whatsapp out/map_16x9_whatsapp.mp4` if the user wants a WhatsApp copy (the map has no audio unless they add music; the audio check will say so).

## Render settings

| Output | Size | FPS | Audio |
|---|---|---|---|
| 16:9 | 1920×1080 | 30 | none, or music the user adds |
| 9:16 (on request) | 1080×1920 | 30 | same |

## Helper scripts

Shared (in `.claude/skills/video-core/scripts/`): `contact_sheet.py`, `finish.py`.
In this skill's folder: `template/ (Remotion project)`, `cities.json`.
