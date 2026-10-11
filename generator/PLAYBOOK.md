# Daily what-if Reel run

This is the procedure the daily scheduled task follows. Each run researches trends, picks the 2 best of 5 ideas, makes both videos, and queues them for the uploader. Queued videos post automatically, with no human review, so fact-checking and safety checks happen here.

## 1. Set up

- Work in a clone of `hardik-143/instagram-reels-uploader` on `main`, freshly pulled.
- Read `generator/topics_log.md`. Never repeat a topic listed there, and avoid close variants.
- Check that Pillow, NumPy and `ffmpeg` are available. Install whatever is missing.

## 2. Research trends (last ~14 days)

- If the vidIQ tools are available, call `vidiq_instagram_tiktok_outlier_search` with a "what if" hypothetical-scenario query. Use the audience `Culture/Region: India; Global: true; Demographics: curious teens and young adults 16-30 who like science, space and fun facts;` and a `datePostedAfter` of 14 days ago. Note which concepts, formats and hooks are overperforming.
- Use web search for festivals, launches, sports events and science news in India and worldwide over the next 7–10 days.

## 3. Generate 5 ideas, pick the best 2

Score each idea from 1 to 5 on each of these, then pick the two highest totals:

- Trend evidence: a similar concept or format is overperforming right now, or the idea is tied to an upcoming event.
- Fit: it can be made with the existing characters and backgrounds, or a small addition.
- Facts: its key claims can be verified from reliable sources.
- Hook: there's a clear escalation and a funny or surprising twist.
- Audience: it has an Indian angle or works globally.

Hard rules. Skip any idea that:

- features real, named living people as characters;
- spreads doomsday predictions, health misinformation, or political or religious controversy;
- encourages a dangerous challenge (if the topic invites copying, add a safety line, as the breath-holding Reel does);
- uses copyrighted characters or music.

## 4. Fact-check

Verify every number and factual claim in the narration and caption with web search, using primary sources where possible. If a claim can't be verified, rewrite it as clearly hypothetical or drop it. Round sensibly ("about 400 km/h").

## 5. Build each video

- Copy the closest `generator/vid_*.py` and write `generator/vid_<slug>.py`. Use an intro, 5–8 scenes of about 7 s each, a twist scene and an outro, for 45–90 s in total. `generator/README.md` documents the config.
- Run `python3 vid_<slug>.py preview <times>` and look at the contact sheet. Fix any overlap between bubble, captions, characters and props, any glyph that renders as a box (avoid arrows and uncommon symbols), and any text that's cut off.
- Render, then check with `ffprobe` that the duration is right and with `volumedetect` that there's audio.

## 6. Queue it

- Create `videos/<slug>/` with `video.mp4` (a regular Git file, not LFS) and `metadata.json`:
  - `queuedAt`: the current UTC time in the form `YYYY-MM-DDTHH:MM:SSZ`.
  - `caption`: 600–900 characters, fact-led and in plain English. Open with the hook, give the real numbers, and end with a "YOU" question and 👇.
  - `hashtags`: 8 tags matching `^#[\p{L}\p{N}_]+$`, always including `#whatif` and `#reelsindia`.
- Run `npm test`, `npm run queue`, and `node src/publish.mjs <slug> --dry-run` for each new slug.
- Add both topics to `generator/topics_log.md`, along with the 3 ideas that weren't picked under "Backlog ideas".
- Commit `generator/vid_<slug>.py`, the new `videos/<slug>/` folders and the log. Fetch `origin/main`, rebase if needed, and push.

## 7. Report

Finish with a short summary: the 5 ideas with their scores, the 2 that were made, the trend evidence for each, and anything that failed.
