---
name: mythology-luminous-diorama
description: "Turn an Indian or Hindu mythology voiceover into a luminous 2.5d temple-diorama animation reel, with consistent characters, actual character motion, timed Hindi/English captions, music, SFX and vertical video delivery. Use when the user requests this specific visual style; inspect available generation and rendering tools before promising an MP4."
---

# Luminous 2.5D Temple-Diorama Animation

## Visual direction

**Reference match:** IMG_1039.PNG, IMG_1047.PNG and IMG_1048.PNG; secondary reference IMG_1042.PNG.

**Look:** Flat illustrated mythological characters arranged inside a luminous layered stage: ornate arches, deep indigo night skies, brass lamps, glowing doorways and carefully controlled gold light. Here 2.5D means separate illustrated depth planes, not full 3D character modelling.

**Palette and rendering:** Night blue #101B38, dark maroon #3C1019, aged gold #D4A23B, amber #F5A83B and ivory #FFF0C7. Reserve the brightest values for the narrative focal point. Use bounded bloom and sparse dust motes; preserve crisp linework.

**Characters:** Use elegant simple illustrated figures, medium-thin outlines and consistent proportions. Build enough articulated or replacement poses to bow, turn, walk, reach and react. Lock iconography and clothing before adding ornamental frames. Keep sacred objects distinct and readable against gold architecture.

**Animation grammar:** Build 5–7 layers: sky, distant architecture, middle architecture, character, foreground columns, lighting and sparse particles. Set conservative parallax ratios so near planes move more than far planes. Add real character acting as well as flame flicker, cloth motion and light changes. Use doorway reveals, a slow 3–6% push, or a lateral move; do not perform all three at once. Avoid lens orbits through flat sprites.

**Framing:** Design a vertical arch to frame the subject. Use symmetry for an introduction or revelation, then move to an asymmetric medium shot for action. Keep a clean caption band outside ornate crowns, lamps and the brightest bloom. Use negative space to establish scale rather than making characters unreadably small.

**Caption treatment:** Use a restrained serif for English or Noto Serif Devanagari for Hindi, cream lettering with a soft dark backing. Place in the upper or lower safe band according to the composition and keep it stable within the scene. Limit all-caps English to short headings; no ornamental pseudo-Devanagari fonts.

**Music and SFX:** Use a slow tanpura-like drone, soft bansuri or bowed-string melody and restrained bells at 65–85 BPM. Let a major reveal briefly thin out the music before a warm chord enters. Add lamp/fire ambience, a reverberant step or a distant temple bell where motivated. Do not use invented chants.

**Preferred implementation:** Use layered SVG or transparent illustrations with an available compositor. Keyframe light masks and depth planes separately from the character rig. A code-generated diorama is acceptable when it meets the visual standard; label flat-layer animation accurately. If using generative video, reject architecture warping and unstable arches.

**Shot example:** Illustrative 6-second shot: foreground pillars drift apart during a slow push toward a doorway; a figure steps into the light, stops and bows. The lamps flicker independently, the clothing settles, and the final second holds the emotional pose. Keep the supplied narration continuous through the reveal.

**Style rejection checks:** Reject excessive sparkles, blown-out faces, decorative temple symbols without context, perspective shifts that expose flat cards, and a whole reel consisting only of camera pushes.


## Task and defaults

Act as a director, character designer, animator, editor and sound designer. Turn the user's supplied voiceover into a complete animated storytelling reel in this file's visual direction. Execute production with the available tools; do not stop at suggestions when rendering is possible.

- Default to 9:16, 1080×1920, 30 fps, original voiceover language and the audio's actual duration. If only a script is supplied, use its length to estimate duration and label that estimate; do not force every story into 60 seconds. Do not shorten, rewrite, translate, synthesize or replace the supplied voice without permission.
- Use Hindi captions for Hindi audio and Roman captions for English. For Hinglish, match the supplied transcript's script; otherwise default to Roman Hinglish and state that choice. Keep names and Sanskrit terms consistent.
- Use this document independently. Its screenshot filenames are descriptive provenance only; the images are not bundled or required. Do not request them again if the written direction is sufficient. If images are supplied, study visual traits but never copy their platform UI, usernames, logos or engagement counters.
- The visual categories are practical production directions, not a measured popularity ranking. Still screenshots establish appearance, not original motion, audio, software or factual accuracy.

## 1. Check inputs and execution capability

Inspect the actual uploaded audio, transcript, reference images and available tools. Obtain audio duration, sample rate and a time-aligned transcript with the tools available. Ask for the missing audio only when the task requires the original recording and it is absent; proceed with useful planning meanwhile.

Choose the first viable production route:
1. **Media tools connected:** generate original character references and scenes, animate them, create or license music/SFX, and render the edit. Read the actual tool schemas. Never invent model IDs, APIs, downloadable assets or generation results.
2. **Code and rendering available:** construct original illustrated/vector or sprite assets appropriate to this style; animate character rigs or replacement drawings; render frames and mix audio with available software such as a canvas engine, Blender, Python and FFmpeg. Check installed versions before writing library-specific code. Simple procedural scoring is acceptable if it sounds good and is identified honestly.
3. **Required production capability unavailable:** finish the timecoded production package with exact asset prompts, animation cues, captions and edit instructions; name the specific missing capability. Do not call a storyboard, slideshow or HTML preview a finished reel. If transcript alignment is unavailable, label timings provisional and request transcript/audio support only as needed.

Honor existing spend authorization and service limits. Estimate external generation costs when exposed; do not silently commit to an unapproved paid plan or bypass a service approval. Avoid spending on every scene before validating a short sample. Do not imply a skill file itself supplies video models or paid credits.

## 2. Preserve the story and establish characters

Treat the narration as the editorial master. Check important names, relationships, event order and iconography against the user's chosen telling or a reliable accessible source when available. Distinguish Valmiki Ramayana, Ramcharitmanas, Mahabharata, Puranic and regional/oral versions where it materially affects a scene. Do not present an unverified popular anecdote as a confirmed passage. Flag uncertainty privately in production notes; never silently change the voiceover or invent chapter/verse citations.

Keep the depicted form consistent with the selected episode: age, complexion, dress, weapons, mounts, symbols and number of limbs/heads. Avoid automatically adding attributes from another incarnation or era. Do not map darker skin to villainy, conflate all Indian traditions with Hindu narratives, or modernize settings without a request. Use original designs; existing films and creator screenshots are visual references, not reusable licensed assets.

Create a compact character bible: ID, narrative role, relative height, face, hairstyle, costume palette, distinguishing attributes, props, allowed expressions, views/poses and continuity constraints. Build one model sheet per recurring character. Reuse references, rig IDs and palette values across all shots; a seed alone does not guarantee identity.

## 3. Turn speech into a precise visual timeline

Transcribe and align to the real recording. Preserve audible wording, meaningful pauses and the natural Indian pronunciation of names. Correct transcription mistakes without changing meaning. Use word alignment where supported; otherwise align phrases manually against waveform/audio and mark unresolved timing.

Segment by narrative beat, not equal time blocks. For a typical minute, begin with approximately 10–16 shots and adapt to the narration and style. Show the first narrative event within 0–2 seconds; no obligatory logo intro. Let a decision or reaction breathe. Do not fabricate a cliffhanger or CTA that the recording does not contain.

Create a shot table with: shot ID; in/out time; exact VO phrase; characters; setting; framing; action and reaction; camera move; caption cue; music/SFX cues; required assets; transition. Keep the timeline contiguous. Handle clip overlaps explicitly so dissolves do not shorten the overall timeline. Use at least three purposeful shot scales over a typical reel.

For every shot, write one keyframe prompt and one animation prompt. Use this structure, replacing every field with actual content:
- Keyframe: selected style + locked character descriptions/reference IDs + exact setting + pose + composition + palette/light + caption-safe negative space + 9:16 + no baked-in text/UI/watermarks.
- Animation: actual supported duration + starting pose + one principal action + character reaction/follow-through + environment motion + one camera choice + end pose + continuity locks. Disable generated dialogue/music when possible; preserve the supplied VO as the sole narrator.

## 4. Generate and animate

Create a 4–6-second representative shot internally, inspect it, and repair the approach before producing the remaining scenes. Continue without waiting for a new approval unless the user or tool requires one. Reuse successful assets and rerender failed shots only.

Make each action-bearing beat visibly animated: changing pose, a turn, a gesture, steps, interaction or a coherent action cycle. Camera zooms, sparkles and moving captions alone do not satisfy this. Limited animation is intentional, but it must tell the story through character motion. Allow held poses on quiet moments. Preserve physical contact, ground placement, screen direction and facial identity. Render titles and subtitles in the editor, never inside generative scene art.

## 5. Captions, music and sound

Build UTF-8 SRT captions and an editable styled format such as ASS or the project's native text timeline. Use phrase groups of roughly 3–7 words, no more than two lines, normally 0.8–2.5 seconds depending on speech. Avoid rapidly flashing single words. Split Hindi at word boundaries, never through a conjunct or matra. Check complex-script shaping and use an available licensed font with proper glyph coverage.

At 1080×1920 start with 54–68 px caption type, adjusting for actual font and language. Use a working content-safe rectangle around x=90–900 and y=240–1500; this is a conservative editing guide, not a permanent platform guarantee. Check the intended platform's preview when available. Follow the style-specific caption position. Move text away from faces/hands and avoid collisions with headings. Highlight one meaningful word per phrase at most; render captions against the actual audio, aiming for no more than about 100 ms visible drift.

Use original or appropriately licensed instrumental music and SFX. Keep a record of source, license or generation provenance. Do not reuse film soundtracks, unlicensed devotional recordings or fabricated Sanskrit chants. Never claim music is royalty-free without evidence. Design a score arc with setup, tension and resolution where the narration supports it. Place sound effects against visible actions, not random edit points.

Keep narration dominant; begin music roughly 18–24 dB below the voice and adjust by ear with ducking. Avoid harsh de-essing, excessive denoising and repeated loud impacts. Aim for a finished mix around −16 to −14 LUFS integrated and true peak at or below −1 dBTP, treating these as production targets rather than platform requirements. Check both headphones and small-speaker intelligibility. Preserve natural pauses and intelligible final syllables.

## 6. Render, verify and deliver

Export an actual MP4 with H.264, yuv420p, 1080×1920, constant 30 fps and AAC 48 kHz when supported, using sufficient bitrate for line art. Target the real VO length to within one frame, or explicitly account for any agreed closing tail. Include the full final word and a clean audio fade; never silently truncate the recording.

Inspect first/middle/last frames of every shot, every transition and the full reel at normal speed with audio. Check actual metadata, decode success, contiguous timing, no black gaps, no missing assets, stable anatomy, exact attribute counts, hands/props, readable Hindi, spelling, caption synchronization, audio balance and visual-style consistency. Fix defects and rerender affected scenes. Never report listening or visual playback checks that were not possible.

Deliver: (1) captioned reel.mp4, (2) captions.srt, (3) clean reel without burned captions if practical, (4) editable project/source plus asset manifest, (5) short production notes covering selected telling, assumptions, rights and remaining limitations. Reuse assets between captioned and clean exports. Name real files and link only outputs actually created. If rendering is blocked, clearly label the deliverable production-package.md and specify the missing capability; do not claim completion of video production.


## Reference provenance

Primary visual evidence: the supplied screenshots listed above. Lighting, parallax and music are recommended production choices; screenshots alone do not establish the original motion or sound.

## Example request

"Use mythology-luminous-diorama to turn my attached Hindi voiceover into a complete 9:16 storytelling reel. Preserve my recording, use the visual rules in this file, animate the characters, and add readable captions, music and synchronized sound effects. Render the MP4 with available tools; report any genuinely missing production capability."
