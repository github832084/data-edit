---
name: openmontage
description: Build an original video from the structure of a reference Reel, Short or local clip using OpenMontage (calesthio/OpenMontage). Analyzes the reference's hook, pacing and editing structure, then proposes and produces new videos on the user's topic. Use when the user says "openmontage", "build from this reference", "make a video like this reel", or "copy the structure/pacing of this short".
---

# OpenMontage

OpenMontage is a full video-production project (AGPL-3.0), not a single skill
folder. Its own agent skills live in the project's `.claude/skills/` and depend
on its Python tools, so it is used from its own checkout, not copied in here.

Source: https://github.com/calesthio/OpenMontage

## Setup (once)

Prerequisites: Python 3.10+, FFmpeg, Node.js 22.23.4+ (or 24.22.1+, 26.12.1+).

1. Ask the user where to put the project (default: `~/OpenMontage`). Do not
   clone it inside this repository.
2. Clone and set up, following the repository's Quick Start:
   ```bash
   git clone https://github.com/calesthio/OpenMontage.git ~/OpenMontage
   cd ~/OpenMontage
   make setup
   ```
   `make setup` installs Python requirements, the Remotion composer's npm
   packages and the free offline Piper TTS.
3. Tell the user to open `~/OpenMontage` in Claude Code (a new session there),
   so OpenMontage's own skills and `CLAUDE.md` load, and to add their reference
   video.

Available visuals and costs depend on which providers the user connects
(see the project's `setup-api-key` skill). Never add API keys the user has not
provided.

## Starting prompt

Once the user is in the OpenMontage project, suggest:

> Analyze this reference's hook, pacing, and editing structure. Propose three
> original 45-second videos about [my topic] using my own content. Keep the
> useful storytelling principles, with new wording and visuals. Show the plan,
> required tools, cost estimate, and a sample before full production.

Keep the result original: reuse structure and pacing, never the reference's
footage, wording, characters or music.
