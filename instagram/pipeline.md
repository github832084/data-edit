# From idea to post · the pipeline · draft v1 · Nov 17, 2026

The rule: Claude does the work, and the owner only says yes or no at each gate (🔒). Nothing reaches Instagram without the last yes.

| # | Step | Who does it | Gate | What the owner sees |
|---|---|---|---|---|
| 1 | **Topic** from the 5-topic list or the week plan | Claude | 🔒 G1 | one line: topic, hook, source |
| 2 | **Research + source card**: verse, IAST, meaning, edition, chapter and verse | Claude | 🔒 G2 | a list of claims, each with its source. The owner checks them against his books (the one step that cannot be automated) |
| 3 | **Script** (Hindi, about 6 min) + 3–5 short-Reel hooks | Claude (/ig-reel, /ig-human) | 🔒 G3 | the script file |
| 4 | **Voice**: the owner records on his phone, or Claude makes it with his voice/avatar | owner or Claude | 🔒 G4 | the audio file |
| 5 | **Video, style A**: scenes, verse cards, captions, music; 1080×1920 | Claude (HyperFrames / Remotion skills) | 🔒 G5 | the draft video |
| 6 | **Package**: long Reel + 3–5 short Reels + cover + captions + hashtags | Claude (/ig-caption) | 🔒 G6 | one page with everything |
| 7 | **Post** at the planned time (long Reel first, short Reels on the following days) | Claude, through the Instagram API | 🔒 G7 "post" | the final yes |
| 8 | **Report** 48 h later: views, watch time, sends, follows | Claude (/ig-audit) | — | a short report; feeds next week's plan |

## What is automatic and what is not

- **Fully in the cloud now:** steps 2, 3, 5, 6 and 8.
- **Step 4, voice:**
  - **Own recording:** the owner sends an audio file, and that is all.
  - **AI voice of the owner:** needs about 1 minute of clean recording to clone. Instagram rule: a realistic AI voice must be marked "AI info" (the API has `is_ai_generated=true`).
- **Step 7, auto-posting:** possible with Meta's official Instagram API. It needs a one-time setup by the owner:
  1. Make the Instagram account a **professional (Creator) account**.
  2. Create a **Meta developer app** and give its access token through the secure form (never in chat).
  3. Allow `graph.facebook.com` and `rupload.facebook.com` in this environment.

## Instagram's own rules that the pipeline follows

Read on Nov 17, 2026 from creators.instagram.com, transparency.meta.com and developers.facebook.com.

1. **Originality:** only original or "materially edited" work is recommended to non-followers. Own drawings, own voice and own research are fully original. If most posts in a rolling 30 days are not original, the account stops being recommended. *(Original content guidelines)*
2. **AI label:** a profile built around an AI person needs the "AI-generated profile" label, or its reach is cut. Using AI tools for your own content needs no profile label. A realistic AI voice in a post should be self-disclosed. *(Creators blog, Aug 31, 2026; API `is_ai_generated`)*
3. **What the ranking predicts:** Instagram's own ranking card lists, among others:
   - will you follow the author?
   - will you watch more than 5 seconds?
   - will you watch more than 95% of the video?
   - will you comment, like or reshare?
   - will you tap "Not interested"?

   → So: a strong first 5 seconds, a reason to finish, and a line worth sending. *(transparency.meta.com, Explore ranking)*
4. **Trial Reels:** a Reel can be shown first only to non-followers, then shared to followers if it does well. The API supports it (`trial_params`, auto-graduation `SS_PERFORMANCE`). Good for testing hooks. *(creators.instagram.com/reels; API docs)*
5. **Quality:** high video quality helps Reels reach more people. Best export is up to 2K, 60 fps. *(Creators blog, Apr 9, 2026)*
6. **Translation:** Meta AI can dub Hindi Reels into English and other Indian languages in your own voice. It works best with one clear speaker and little background music. *(Creators blog)*
7. **API limits for posting:**
   - Reel: 3 s to **15 min**, up to 300 MB, H.264/HEVC, AAC audio, 23–60 fps, max width 1920, 9:16 recommended
   - 100 API posts a day
   - no scheduling field, so Claude posts at the planned time itself

   *(developers.facebook.com, content publishing)*
8. **Long horizontal "Features" (up to 90 min):** test only in the US and Brazil, and not in the API docs yet. Video is made in 9:16 now, with scenes that can also be exported 16:9 later.

## Not found in official pages

- Instagram's Help Center page on recommendation guidelines did not load (needs login), so its exact text was not read.
- No official India date for Features.
