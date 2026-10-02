# Review and tests

Serve the site first (audio needs HTTP): `python3 -m http.server 8765 -d site`. For a book in `site/<book>/`, pass `--url http://localhost:8765/<book>/` to the scripts. Python's server has no Range requests, so setting `audio.currentTime` jumps back to the start; tests let audio play or use `seek()`.

## 1. Load check

Open `…/chNN/index.html?beat=0&t=0` (or run `shot.py` with one spec). Any console error usually means a redeclared engine name, a missing mark, or a constant used in `BEATS` before it is defined.

## 2. Screenshots

```sh
uv run --with playwright --with pillow SKILL/scripts/shot.py chNN --url … --out /tmp/shots
```

Every beat at 1.2 s (`open`), middle and end, saved as 4-up contact sheets `chNN_sheet_{open,mid,end}_K.png`. Read the `open` and `end` sheets; look at `mid` or a single shot only to chase a problem; use `shot.py chNN 5:7.5` for a specific moment. One browser at a time, and pick times after fades finish.

Look for:

- the picture empty or unrelated at `open`;
- text over drawings, labels colliding, anything clipped or off the stage;
- a question card covering the object it asks about;
- leftovers from the previous beat, half faded;
- wrong mathematics in the drawing: points off their values, unequal spacing, an area not matching its label;
- text too small to read at half size, or too much text at once;
- inconsistent colours for the same idea.

## 3. Opening blanks

```sh
uv run --with playwright SKILL/scripts/check_blank.py site/<book> chNN --url …
```

No output means no beat leaves the picture empty for more than 1 s after the narration starts (`LIMIT=0.6` for stricter). Fix the beat's opening, don't raise the limit.

## 4. End-to-end test

Copy `SKILL/assets/templates/e2e.py` to `tools/e2e_chNN.py` and fill in the chapter's questions: each answered wrong then right (first-try score 0), at least one Show answer, the finish card, R back to the start, then `seek` through every beat; no console errors. Run `uv run --with playwright tools/e2e_chNN.py` (set `URL` for a book folder).

- Keyboard only (plus one mouse pass for drag questions).
- With focus in an answer box only Enter and Esc are handled; press Esc before S (Show answer).
- Playwright's `text=Check` matches case-insensitively and by substring ("Quick check"); buttons include their key label ("1Rational"). Use CSS classes or indexes.
- A multi-row `blanks`/`grid` question scores one per row.
- Enter on the finish card opens the next chapter; use R in tests.

## 5. Regression

After any engine change, run every chapter's test (in the background, two at a time):

```sh
ls tools/e2e_ch*.py | xargs -P 2 -I{} sh -c 'uv run -q --with playwright {} >/dev/null 2>&1 || echo "FAIL {}"'
```

Also rerun `check_blank.py` for the whole book when timing logic changes.
