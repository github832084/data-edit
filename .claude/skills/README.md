# Video editing skills

Claude Code loads these automatically from `.claude/skills/` when you work in this repo.
Third-party skills are copied unmodified from their repositories (only `.git`, CI files and README demo GIFs left out).

## The 5 skills from "5 Claude Video Editing Skills" (Higgsfield blog, @davidho)

| # | Skill folder | Job | Source |
|---|---|---|---|
| 1 | `ghost-editor` | Polish talking-head footage into a vertical reel: best takes, captions clear of the face, graphics, SFX | [kurbaitaev/ghost-editor](https://github.com/kurbaitaev/ghost-editor) @ `ce17272` (MIT) |
| 2 | `ffmpeg-skill` | 42 local FFmpeg tools: cut pauses, captions, reframe, loudness, exports | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) @ `f1c97cb` (MIT) |
| 3 | `editorial-motion-graphics` | Explainer from an idea via Higgsfield (connector `https://mcp.higgsfield.ai/mcp`) | [skill page](https://higgsfield.ai/skills/editorial-motion-graphics) (setup notes written here) |
| 4 | `shorts` (`/shorts`) | Long video → scored short clips with Remotion captions | [AgriciDaniel/claude-shorts](https://github.com/AgriciDaniel/claude-shorts) @ `a369fad` (MIT) |
| 5 | `openmontage` | Build original videos from a reference's structure | [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) (AGPL-3.0; setup skill only, the project is cloned separately) |

Setup per skill (from the article):

1. **Ghost Editor** – built and tested on Apple-silicon Macs. Run `bash .claude/skills/ghost-editor/scripts/doctor.sh`, fix each `MISS`, then `python3 .claude/skills/ghost-editor/scripts/library_restore.py` (~60 MB of SFX/music/emoji). Optional Gemini key in `.claude/skills/ghost-editor/.env` for reference-video analysis and visual checks.
2. **FFmpeg Skill** – needs FFmpeg, ffprobe and Python 3.10+. Check with `python3 .claude/skills/ffmpeg-skill/scripts/_contract.py doctor`. Transcription needs a local engine (`pip install faster-whisper`) or an existing transcript.
3. **Editorial Motion Graphics** – add the Higgsfield connector in Claude (Customize → Connectors) and sign in; uses Higgsfield credits.
4. **Claude Shorts** – run `bash .claude/skills/shorts/setup.sh` (faster-whisper, Remotion deps), start a new session, type `/shorts`. Windows needs WSL 2.
5. **OpenMontage** – `git clone https://github.com/calesthio/OpenMontage.git ~/OpenMontage && cd ~/OpenMontage && make setup`, then open that folder in Claude Code.

Prompts from the article:

1. "Edit my talking-head recording into a 30–45-second vertical reel in the clean style. Select the strongest takes, remove repeated lines, keep captions clear of my face, and use restrained graphics and sound effects. Show me the edit plan before rendering."
2. "Remove long pauses from my video without cutting words. Make a 9:16 version with the speaker in frame, add readable subtitles, and balance speech loudness. Export a new MP4 and check the duration, framing, captions, and audio. Keep the original file."
3. "Create a 30-second vertical explainer about [topic] in an editorial motion graphics style. Use these source facts: [facts]. Build a clear hook, three visual beats, English voiceover, and readable subtitles. Show me the script and scene plan before generation."
4. "Find three self-contained clips from this recording, around 30–60 seconds each. Show the timecodes, opening hook, and reason for each choice. After I choose, render 9:16 versions with Clean captions for Instagram Reels. Keep the original meaning."
5. "Analyze this reference's hook, pacing, and editing structure. Propose three original 45-second videos about [my topic] using my own content. Keep the useful storytelling principles, with new wording and visuals. Show the plan, required tools, cost estimate, and a sample before full production."

Tip from the article: start with one short test, review the first export at normal speed (cut points, caption accuracy, face visibility, audio), and keep revisions specific.

## Other video skills

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

## The 92 video-core skills


Each folder is a Claude Code skill: run `/<name>` and attach what its SKILL.md asks for. All of them share
the render engine in `video-core/` (run `/video-core` once on a new machine to check and install tools).

Work happens in `work/<skill>/<job>/` (gitignored). Every skill shows stills or a contact sheet before the full
render and never overwrites files without asking.

| Family | Skills |
|---|---|
| Characters & cartoons | anime-reel, titan-anime, anime-fight, madhubani-kahani, katha-video, shadow-puppet, kids-story, pusho-reel, baba-pusho, woof-woof, street-interview, latent-reel |
| Comic book | podcast-comic, latent-comic, comic-reel, mirzapur-video, maut-ke-bare-mai-sochte-ho, madira-peekar-soo-gaye, podcast-cartoon |
| Explainers & news | news-report, podcast-explainer, personal-explainer, blueprint-explainer, 3d-explainer (Blender), watercolor-map (Remotion) |
| Lyric videos | lyric-video, hindi-lyric-video, sketch-music-video, kinetic-lyrics, ink-line-lyrics, party-lyrics, rap-video, comic-rap-video, aarti-video, neon-lyrics, paper-cutout, bairan-style, glow-lyrics, minimal-lyrics, watercolor-lyrics, spotify-particle-lyrics, pink-spotify-clip-lyrics, night-glow-lyrics, red-rap-lyrics, glass-to-neon-lyrics, breakup-chat-lyrics, phone-chat-lyrics, red-sun-lyrics, red-silhouette-lyrics, night-city-lyrics, anime-doodle-lyrics, minimal-love-lyrics |
| Gemini / Flow assets | miniature-painting-lyrics, crayon-rain-lyrics, split-screen-ldr-lyrics, one-take-forest-lyrics, sketch-doodle-edit, crayon-carousel |
| Beat & photo edits | beat-transition-edit, scribble-edit, flicker-edit, painted-beat-edit, sketch-to-motion, shutter-stack |
| Talking head | talking-head-edit, personal-short-form-reels, personal-broll-library, depth-ui-reel, youtube-clips, educational-youtube-editor, ranking-format, business-short-form-reels, match-cut, led-matrix-text, glass-stat-card, particle-chart, particle-text, price-tag-zoom, podcast-reel-edit, dark-red-timeline-motion-graphics, instagram-ui-hinglish, hindi-pastel-reel-edit, kinetic-talking-head-edit, red-kinetic-collage-edit, iphone-style-by-aansh, rgb-glitch-live, magazine-cover, comic-halftone, breaking-news, neon-outline, cinema-scope, triptych-timecode |

## Instagram Agent Skill (13 skills)

Copied unmodified from [Jakeschincariol/instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill) @ `d03c56b` (MIT), using the guide's "project only" method.

| Skill | Job |
|---|---|
| `ig-reel` | Three scored hooks, the script, on-screen text and a timed beat sheet |
| `ig-viral` | What works in your niche, ranked by each account's own median |
| `ig-caption` | The caption, linted, with the 125-character feed preview |
| `ig-carousel` | Cover, slide copy and 1080×1350 slides |
| `ig-story` | The day's story sequence and stickers |
| `ig-profile` | Profile score out of 100 and a rewrite |
| `ig-plan` | The week's posts, formats, times and accounts to engage with |
| `ig-human` | Strips em dashes, slop words and invisible characters, then scores the draft |
| `ig-comment` | Comments on other people's posts |
| `ig-reply` | Replies to your own comments, in priority order |
| `ig-dm` | Keyword delivery, first message, collab pitch and follow-ups |
| `ig-repurpose` | One video or newsletter into a week of posts |
| `ig-audit` | Post-mortem on your insights |

Nothing is posted, commented or sent for you; every skill ends in copy-ready text.
The skills share `~/.claude/instagram/` (`voice.md`, `swipe.md`, `plan.md`, `log.md`). The voice template is in `ig-reel/templates/voice.md`.
In a cloud session that folder is lost when the session ends, so keep your filled-in `voice.md` in the repo and copy it there at the start.
