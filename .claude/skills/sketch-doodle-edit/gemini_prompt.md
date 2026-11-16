# Gemini prompt for the pencil sketch

Give the user this prompt with their photo attached. They save the result as `sketch.png` next to `photo.jpg`.

> Turn ONLY the people in this photo into a clean, detailed pencil sketch: graphite lines and soft shading on
> white, like a hand-drawn portrait. Keep everything else in the image exactly the same as the original photo:
> the sky, background, ground, colours, lighting, framing and size. Do not move, resize or crop anything.
> The people must stay in exactly the same position and pose. No text.

If the sky or background changes, ask them to regenerate with: "The background must be pixel-identical to the
original; only redraw the people."
