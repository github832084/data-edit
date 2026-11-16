# Video editing skills

Claude Code loads these automatically from `.claude/skills/` when you work in this repo.
They are copied unmodified from the vendors' official repositories.

| Skill | What it does | Source |
|---|---|---|
| `remotion-best-practices` | Router for all Remotion skills: create, markup, captions, multimedia (trim/crop), render, Studio preview, maps | [remotion-dev/skills](https://github.com/remotion-dev/skills) @ `3e20ac7` |
| `hyperframes` | Make, edit, animate and render video from HTML (explainers, vertical clips, captions, overlays) | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) @ `5d5e2c0` (Apache-2.0) |
| `hyperframes-cli` | Scaffold, preview, edit timelines and render with the HyperFrames CLI | same |
| `hyperframes-registry` | ~450 ready-made transitions, titles, kinetic type, caption and chart blocks | same |
| `media-use` | Music, SFX, voiceover, transcripts, transcript-based cuts, audio ducking, colour grades | same |
| `higgsfield-generate` | Generate images and video with Higgsfield models | [higgsfield-ai/skills](https://github.com/higgsfield-ai/skills) @ `2700040` (MIT) |
| `higgsfield-faceless-video` | End-to-end faceless short-form video pipeline | same |
| `higgsfield-video-explainer` | Explainer videos with Higgsfield | same |

## Prerequisites

- Node.js 18+ and `ffmpeg`/`ffprobe` on `PATH`.
- Remotion: `npx create-video@latest` (the skill walks Claude through it).
- HyperFrames: the skill installs/uses the `hyperframes` CLI via npx.
- Higgsfield: install the Higgsfield CLI and sign in (needs a Higgsfield account and credits).
- Some `media-use` features use HeyGen or Gemini API keys; free local tools are used otherwise.

## Telemetry

`media-use` scripts send coarse anonymous usage events to PostHog. Opt out with
`HYPERFRAMES_NO_TELEMETRY=1` or `DO_NOT_TRACK=1`.

## Example prompts

- "Create a 30-second vertical Remotion video announcing our launch, and open the Studio preview."
- "Add animated word-by-word captions to `clip.mp4`."
- "Cut the filler words and long pauses out of `interview.mp4` using its transcript."
- "Make a 60s HyperFrames explainer with a title card, chart and background music ducked under the voiceover."
- "Use Higgsfield to make a faceless short about the history of Sanskrit grammar."

## Updating

Re-run `npx skills add remotion-dev/skills`, `npx skills add heygen-com/hyperframes`,
`npx skills add higgsfield-ai/skills`, or re-copy the folders from those repos.
