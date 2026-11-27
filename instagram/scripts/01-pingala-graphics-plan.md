# Video 1 · पिंगल · graphics plan v1 · Nov 19, 2026

## A. Our v2 compared with the two references

References:
- **#1** sukshm, "Panini's Ashtadhyayi" (92K views)
- **#2** The Oldest World, "Isha Upanishad"

| What | #1 sukshm | #2 Oldest World | Our v2 | Fix |
|---|---|---|---|---|
| **Main picture** | Detailed gold line-art **people and places** (Panini, sage, student, hut, Cambridge desk) | One **living symbol** made of light particles (orbit, web, eye) that keeps changing | Small generic icons (phone, scale, chip) | Real illustrations of Pingala and his world, plus particle systems for numbers |
| **Same character all through** | Yes: the same scholar returns in many shots | The same light-orb returns | Scholar shown twice, drawn differently | One Pingala character, used in every chapter |
| **Recurring symbols** | Palm leaf = a rule; stacks of books = many rules; sun/moon = time passing | Orb = the whole; rings = the world | Beads only in some shots | **Bead = syllable** (small = लघु, big = गुरु), **palm leaf = sutra**, **gold thread = order**, **sun/moon = time** |
| **Movement inside a shot** | Leaves fly, books line up, people walk, a rope links teacher and student | Particles orbit, rings dissolve and re-form | Things pop in, then stand still | Something always moves: beads travel, threads draw, particles drift, numbers count |
| **Cut style** | One object becomes the next (leaf → card) | The symbol morphs into the next symbol | Fade + flash | Morph cuts: beads become digits, a leaf becomes the sutra card |
| **Text on screen** | Only the term, the verse and a small label ("A ROOT", "EVERY VOWEL") | Verse block with the current word lit; tiny citation | Big keyword that repeats the caption | Show the thing, not the word. Text only for terms, numbers and the source |
| **Verse** | The verse stays at the top for the whole section, with IAST and the reference | Verse + translation; the current word glows | Verse card shown once | Sutra stays at the top during its section; the word being explained glows |
| **Chapters** | Not needed | "I · DWELLING", "II · MOTION" | None | 7 chapter labels: I · छंद, II · लघु-गुरु, III · प्रस्तार, IV · सूत्र, V · binary, VI · मेरु, VII · दावा |
| **Background** | Pure black, small stars | Dark nebula / smoke with depth | Flat gradient + rays | Soft moving nebula, 2–3 layers of depth (parallax) |
| **Screen use** | 16:9, sparse | 16:9 | 9:16, the lower half often empty | Use the whole 9:16 frame: scene in the middle, verse at the top, captions low |
| **Shot length** | 2–5 s | 3–6 s, but always moving | 2–4 s | Keep 2–4 s, with motion inside every shot |

**Biggest gaps (in order):**
1. No real illustrations: our icons look like clip-art.
2. Shots stand still once they appear.
3. No recurring visual language.

## B. What Claude can make here

| Kind of picture | How | Quality | Cost |
|---|---|---|---|
| Gold line-art people and places (like #1) | Local free AI image model (SD-Turbo, about 15 s an image on this machine) → turned into glowing gold lines → drawn on screen line by line | Good. The test images came out close to #1. Faces and hands need retries | Free |
| Particle systems, orbits, mandalas, morphing shapes (like #2) | Code (canvas) | Very good | Free |
| Diagrams, tables, counters, triangles, timelines | Code (SVG) | Very good | Free |
| Moving characters (walking, writing) | Two or three image poses with a cross-dissolve, plus small movements | Fair | Free |
| Paid AI video (Higgsfield etc.) | Not used: the owner wants free tools | n/a | Paid |

## C. Shot plan by point (draft, to refine after demo choices)

Each point gets a main scene, with motion inside it and a morph into the next. Line numbers refer to the script.

| # | Point (lines) | Main scene | Motion | Into next |
|---|---|---|---|---|
| 1 | **Hook** (0–5) | Pingala seated with palm leaf and lamp | Syllables leave his lips as beads → beads double 1·2·4·8 → stream of 0/1 forms a phone screen | The phone fades; the beads return to the palm leaf |
| 2 | **कवि की मुश्किल** (6–12) | Pingala under the moon, chanting to students | A sound wave becomes a line of 24 beads (गायत्री, 3 × 8); the beads get different sizes; a balance tips | The beads line up into two kinds |
| 3 | **लघु और गुरु** (13–24) | Two beads, small and big | "क" drops in as a small bead, "का" as a big one; "सत्य": स swells; 3 empty slots wait | The slots fill with beads |
| 4 | **प्रस्तार** (25–38) | The palm leaf unrolls into 8 rows of beads | Rows draw in one by one; a branching tree doubles 2→4→8→16→64; the columns light in rhythm | The leaf curls into the sutra card |
| 5 | **सूत्र** (39–60) | Sutra stays at the top; the number 6 travels down a path | 6 → 3 → 2 → 1 → 0 with अर्ध/शून्य marks dropping like seals; then back up 1→2→4→8→64; 2³⁰ counter explodes into a cloud of patterns | The word शून्य glows; the particles gather into one orb |
| 6 | **binary** (61–71) | The 8 rows from point 4 return | Each bead flips into 0/1 (gold 0, white 1); the rows sort themselves; a 4·2·1 place-value ruler slides under | The digits rise and stack into a triangle |
| 7 | **मेरु-प्रस्तार** (72–80) | Halayudha (2nd character) writing a commentary | The numbers build a mountain row by row, each sum drawn as two threads joining; a timeline flies to Pascal, 1654 | The timeline stretches to 1703 |
| 8 | **दावा** (81–90) | Leibniz's desk, quill; a chip drawn in gold | The chip assembles from 0/1 particles; "computer?" breaks apart; hype text swells and cracks | Fade to Pingala again |
| 9 | **अंत** (91–93) | Pingala, the palm leaf, the source card | The leaf glows; the follow button draws itself | End |

## D. Demos for Point 1 (Hook, 0:00–0:22)

Four ways to show the same 22 seconds, with the same voice. The owner picks one (or mixes), then we do Point 2 the same way.

| Demo | Look | Like |
|---|---|---|
| **D1 · Line-art story** | AI-made gold line-art Pingala; syllables float out as beads; beads double; they flow into a phone | #1 sukshm |
| **D2 · Light particles** | One point of light → 2 → 4 → 8 → orbiting mandala → a stream of 0/1 → the title written in light | #2 Oldest World |
| **D3 · Manuscript** | A palm leaf unrolls; a Sanskrit line appears syllable by syllable with ल/ग marks above; the marks turn into 0/1 below | the sutra card from our A style, made to move |
| **D4 · Mixed** | D1's Pingala in the middle, with D2's particles around him | #1 + #2 |

## E. Steps after that

1. The owner picks a demo look for Point 1.
2. Point 2: 2–3 demos in the chosen look; pick. Then Points 3–9 the same way, two points at a time.
3. **Voice:** choose a better Hindi voice. Options:
   - **Indic Parler-TTS** (AI4Bharat, free, needs a Hugging Face account and token)
   - **Your own voice:** record about 1 minute for a clone
   - **Your own recording of the full script:** best of all
4. Full render, check, then the short Reels, cover and captions (pipeline steps 6–7).
