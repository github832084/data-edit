---
name: editorial-motion-graphics
description: Make a short explainer video from an idea in Higgsfield's Editorial Motion Graphics style - script, visual scenes, voiceover, subtitles and final video from a topic and source facts. Use when the user says "editorial motion graphics", "explainer from an idea", or "make an explainer about [topic] in motion graphics style".
---

# Higgsfield Editorial Motion Graphics

Starts from a topic and source facts. Higgsfield builds the script, visual
scenes, voiceover, subtitles and final video.

Skill page: https://higgsfield.ai/skills/editorial-motion-graphics

## Setup

This skill runs on Higgsfield, not locally. Two routes:

1. **Claude chat (connector).** In Claude, go to Customize → Connectors, add a
   custom connector named `Higgsfield` with the URL
   `https://mcp.higgsfield.ai/mcp`, and sign in to Higgsfield. Then send the
   brief below in a chat with that connector on.
2. **Claude Code.** Use the `higgsfield-video-explainer` /
   `higgsfield-faceless-video` skills in this folder, which drive the
   Higgsfield CLI (`higgsfield` must be installed and signed in).

Generation uses Higgsfield credits; check the balance first and tell the user
the expected cost before generating.

## Brief

Collect the topic and the source facts from the user, then use:

> Create a 30-second vertical explainer about [topic] in an editorial motion
> graphics style. Use these source facts: [facts]. Build a clear hook, three
> visual beats, English voiceover, and readable subtitles. Show me the script
> and scene plan before generation.

Always show the script and scene plan and wait for approval before generating.
Only state facts the user supplied or that you have verified.
