# Chapter worker brief (Elementary Mathematics; slug `math-notebook`)

You make ONE chapter of the animated book, end to end, then report back in a few lines. The coordinator registers it.

## Paths (repo root `/Users/a1212/Projects/AnimeBook`)
- Skill: `SKILL=/Users/a1212/Projects/AnimeBook/.claude/skills/papermorph` — read `$SKILL/SKILL.md` (Chapter loop), then only the references you need: `references/authoring.md` (storyboard, narration, questions), `references/engine.md` (API), `references/review.md` (delivery pass).
- Book state: `books/math-notebook/BOOK.md` (conventions + helper index — follow it), `books/math-notebook/chapters.md` (your row).
- Source text: `books/math-notebook/pages/chNN/text.md` (already extracted). Render page images when diagrams/fractions are lost in the text: `uv run --with pymupdf $SKILL/scripts/split_pages.py books/math-notebook/book.pdf --sections books/math-notebook/sections.json --out books/math-notebook/pages --only chNN`. Look only at the pages you need.
- Write: `books/math-notebook/chapters/chNN.md` (storyboard, errata, verified answers — same shape as `chapters/ch01.md`), `content/math-notebook/chNN/narration.en.json`, `site/math-notebook/chNN/index.html`, audio via `uv run --with edge-tts $SKILL/scripts/tts.py content/math-notebook/chNN/narration.en.json site/math-notebook/chNN/audio/en`.
- Reference implementation (approved pilot): `site/math-notebook/ch01/index.html` — same head (incl. `<link rel="expect" …>`), `CHAPTER`, helper style, beat shape, intro card ("Unit U · <unit name> · Chapter N", title on one or two lines), wrap, `final1…` "Chapter practice   N of M", `finish`. Copy patterns; don't copy its number-map content unless the topic needs it. If an earlier chapter already has a helper you need (see BOOK.md helper index), copy it from that chapter.
- Preview server: `http://localhost:8765/` serves `site/` (book at `http://localhost:8765/math-notebook/`). If it doesn't answer, start your own: `python3 -m http.server 8793 -d /Users/a1212/Projects/AnimeBook/site` in the background (do not stop any existing preview server).

## Rules
- English narration, voice/rate from BOOK.md; middle-school readers, light and warm, explains why. Usually 6–10 minutes; let the content decide. Teach the chapter's own scope from the source; re-create examples (don't copy the book's drawings); verify every number and answer you use; never judge irrationality from finitely many digits.
- The picture argues: things move, split, line up, compare. Same colour = same meaning (BOOK.md palette). Open each clearing beat with its subject on screen. Questions act on the picture where possible; 2–3 quick checks between lesson beats; 2–4 practice sets.
- Shared engine `site/math-notebook/lib/engine.js`: prefer chapter-local helpers (prefix names to avoid collisions with engine globals). Only add to the engine in a backward-compatible way; if you do, re-run `check_blank.py` for all existing chapters and report it.
- Do NOT edit other chapters, `site/math-notebook/index.html`, `chapters.md` or `BOOK.md` — report what should change instead. Don't commit, push or publish.
- Delivery pass (review.md): `shot.py chNN --url http://localhost:8765/math-notebook/ --out /tmp/animebook-mn-chNN` (beat spec indices are 0-based), read the sheets once, fix clear defects (overlap, clipping, cards covering the asked object, leftovers, wrong geometry, crowded text), recheck those beats; `check_blank.py site/math-notebook chNN --url http://localhost:8765/math-notebook/` (no output = clean). Smoke-test any new question type by keyboard (note: call `hideCover()` before `seek(i,false)` in Playwright).
- Keep your context small: don't read whole engine files; grep for the functions you use.

## Report (≤ 10 lines)
Files written; minutes (sum of audio + question time, rounded); delivery result (errors, blank check, defects fixed / unresolved); errata vs. the book; new helpers (name, file, purpose) and any proposed BOOK.md convention; anything the coordinator must register.
