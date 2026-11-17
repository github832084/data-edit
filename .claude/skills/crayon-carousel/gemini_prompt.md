# Gemini prompt for the crayon drawings

Give the user this prompt. They attach one photo at a time in Gemini, run it, and save the result next to
the photo with `_drawing` at the end of the name (`IMG_2041.jpg` → `IMG_2041_drawing.png`).

> Redraw this photo as a colourful children's crayon drawing on plain white paper. Keep exactly the same
> pose, outfit, colours and place, with the same people in the same positions and framing. Use bold, waxy
> crayon strokes with visible texture, slightly wobbly outlines and simple shapes, a bit childlike and
> playful, with white paper showing between strokes. No text, no signature, no border.

If Gemini changes the framing a lot, ask the user to re-run it with: "Keep the exact same framing and
crop as the original photo."
