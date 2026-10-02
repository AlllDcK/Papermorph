---
name: animebook
description: Turn a book (PDF) into an animated, narrated, interactive web book — a static site whose chapters are drawn step by step in SVG, narrated with Edge TTS synced word by word, with quick checks inside the picture, graded end-of-chapter practice, a cover, a contents page and a bookshelf. Use it for any part of that pipeline: splitting a PDF into chapters, planning a book, making or fixing a chapter (animation, narration, questions), reviewing and testing lessons, the contents page, publishing. Also when the user only says "do the next chapter", "fix this animation" or "add a question here".
---

# AnimeBook

You turn a reference book into an animated book. Each chapter is one web page holding one 16:9 picture (a 1600×900 SVG stage plus a control bar). A lesson is a list of **beats**; each beat is one narration clip plus the animation timed to its words. Quick checks pause inside the picture; full-screen practice and a score card end the chapter. Everything is drawn in code: no images from the book, no stock art.

The pipeline below is fixed; it was worked out over a full 68-chapter book. The design inside it is yours (see *Creative freedom*). The user may add their own requests at any point; they override defaults here.

## Project layout

```
book.pdf, sections.json        reference book and its page map (private)
book_pages/chNN/               page images + text.md per chapter (private)
BOOK.md                        the book plan: decisions, conventions, chapter status, errata — keep it current
content/chNN/narration.en.json narration script with [[marks]]; TTS cache beside it
tools/e2e_chNN.py              per-chapter keyboard test
site/                          the only published folder
  index.html, lib/bookshelf.*  bookshelf (once there are books)
  <book>/index.html            cover + contents        (assets/templates/book.html)
  <book>/unit-art.js           unit sketches           (assets/templates/unit-art.js)
  <book>/lib/engine.js, .css   this book's engine copy (assets/engine/)
  <book>/chNN/index.html       a lesson                (assets/templates/chapter.html)
  <book>/chNN/audio/en/        beat MP3s + timings.js
```

`SKILL` below means this skill's folder. Needs: `uv` (scripts run as `uv run --with <deps>`), `ffmpeg` (ffprobe, for clip lengths), network access for Edge TTS, and Playwright's Chromium for review (`uv run --with playwright playwright install chromium`). Audio needs a local server: `python3 -m http.server 8765 -d site`.

## Pipeline

Gates marked **(user)** need the user's go-ahead; everything else you just do.

1. **Intake (user).** Start BOOK.md from `SKILL/assets/templates/BOOK.md`. Ask once, briefly: readers (age, level), tone, narration language (others come later), anything to skip or add, a guide character if any, where it will be published. Offer defaults; record answers in BOOK.md.
2. **Split.** `SKILL/scripts/outline.py book.pdf` prints the bookmark tree; rerun with `--level N -o sections.json` at the chapter depth (no bookmarks: write sections.json by hand from the contents pages). Check it against the book's contents, then `SKILL/scripts/split_pages.py book.pdf` (needs `--with pymupdf`) for page images and each chapter's `text.md`.
3. **Book map (user).** Skim every chapter's `text.md` (text only). Write in BOOK.md: units and chapters with minute estimates, a colour per unit, and the recurring visual models across the book (number line, timeline, map, graph, …) — these become engine helpers. Show the user the chapter list and the visual approach.
4. **Pilot chapter (user).** Make chapter 1 completely (chapter loop below). This is where look, pacing, voice and question style get approved; expect several rounds. Record every decision in BOOK.md under *Conventions*; later chapters follow them. Build helpers for the recurring models now, not halfway through the book.
5. **Chapter loop.** One chapter at a time, each in a fresh context (see *Budget*). Commit per unit if the user agrees.
6. **Finish the book.** Contents page with a sketch per unit, cover text, bookshelf entry, whole-book `check_blank.py` and all tests. Deploy only when asked. See `references/site.md`.

## Chapter loop

1. **Read** `book_pages/chNN/text.md`; open a page image only where a diagram matters. Note concepts, worked examples, exercises and answers. **Recompute every answer**: reference books have errors. Fix them in your version and log them in BOOK.md.
2. **Storyboard**: a short beat list — what each beat shows, why it is true, where the quick checks go. → `references/authoring.md`
3. **Narration**: write `content/chNN/narration.en.json` (template in `SKILL/assets/templates/`), then `uv run --with edge-tts SKILL/scripts/tts.py content/chNN/narration.en.json site/<book>/chNN/audio/en`. Only changed beats are re-synthesized.
4. **Beats**: write `site/<book>/chNN/index.html` from the template or the closest finished chapter. API → `references/engine.md`.
5. **Review**: `SKILL/scripts/shot.py chNN --url …` and read the contact sheets; then `SKILL/scripts/check_blank.py site/<book> chNN --url …` must print nothing. → `references/review.md`
6. **Test**: `tools/e2e_chNN.py` from the template: every question wrong then right, one Show answer, the finish card, every beat rebuilt; no console errors.
7. **Register**: add the chapter to `UNITS` in the book's index.html, set the previous chapter's `CHAPTER.next`, update BOOK.md (status, errata, new conventions).

## Non-negotiables

- **Original work.** Never copy the book's wording, examples or page images; rewrite and redraw. Book pages and the PDF are never published.
- **Correct over faithful.** Facts and answers are verified, not trusted; tell the user what you corrected.
- **Picture and voice agree.** Every action is timed by a narration mark (`m('mark')`), never by guessed seconds. The picture is never empty while the narration speaks.
- **The picture teaches.** On-screen text is the key formula or phrase, placed beside what it describes, not a transcript. Captions (CC) exist but are optional.
- **Questions.** Only on what was just taught; never two question beats in a row (except the final practice); every question can be played by keyboard; a wrong answer gets feedback about that specific mistake and a Show answer; a right answer animates the object it is about. Grade the meaning (equivalent forms, any order where order does not matter).
- **One picture.** Everything happens inside the 16:9 stage; no paper-and-pencil tasks.
- **Deterministic beats.** A beat's `run` only schedules tweens: seeking rebuilds the scene by replaying earlier beats, so no timers, randomness or clock reads in `run`.
- **Engine change → rerun every chapter's test.** Each book has its own engine copy; improve `SKILL/assets/engine/` too when a change is general.
- **Publishing, pushing and deploying only when the user asks.**

## Creative freedom

The process is fixed; the design is yours. For each idea pick the visual argument that makes it obvious — rearrange, split, morph, balance, slide, count, compare — and invent scenes, helpers, question types and motion as the content needs. The templates are skeletons, not styles to copy; don't reuse an old chapter's choreography unless it truly fits. Judge every animation by one question: does watching it show *why*? Once the pilot is approved, keep the book consistent: palette, type, character, controls, question feel.

## Budget

A book is long; spend tokens on design, not on re-reading.

- **Fresh context per chapter** (a new session, or a subagent briefed with the chapter number, BOOK.md and the files to touch). Anything later chapters need lives in files — BOOK.md, `references/` — not in conversation memory.
- **Text before images**: read `text.md`; open a page image only for a diagram.
- **Don't read engine.js**; use `references/engine.md` and grep for one function when needed.
- **Screenshots as sheets**: read the 4-up contact sheets from `shot.py` (open and end frames first), single shots only where a sheet shows a problem. Don't re-screenshot what a test already proves.
- **Write a page in one pass**, fix with small edits, and don't re-read a file you just wrote.
- **Short output**: the scripts print summaries; pipe long output through `tail`.
- **Regression only after engine changes**, run in the background.

## References

- `references/authoring.md` — chapter shape, storyboard, narration and marks, questions and practice, content rules.
- `references/engine.md` — the engine: stage, drawing, timing, question types, player; the known traps.
- `references/review.md` — screenshots, what to look for, blank check, end-to-end tests, regression.
- `references/site.md` — starting a book folder, cover and contents, unit sketches, guide character, bookshelf, deploying.
