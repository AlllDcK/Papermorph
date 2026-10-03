# Elementary Mathematics — book plan

Read this compact current state for chapter work. The chapter map/status lives in `chapters.md`; storyboards, errata and feedback live in `chapters/chNN.md`.

## Intake
- Display name: Elementary Mathematics (user, 2026-10-03). Inspired by [Everything You Need to Ace Math in One Big Fat Notebook](https://www.hachettebookgroup.com/titles/workman-publishing/everything-you-need-to-ace-math-in-one-big-fat-notebook/9780761160960/?lens=workman-publishing-company); this credit is displayed on the book cover.
- Readers: middle schoolers (11–14) · Tone: light, upbeat, notebook-style (warm, a little funny, never childish) · Narration language: English · Guide character: default infinity guide · Publish to: local preview only for now.
- Slug: `math-notebook` · Primary language code: `en` · Asset approach: code/SVG only.
- Source: `book.pdf` · Page map: `sections.json` · 530 pages, 63 chapters in 6 units.
- Current scope: paused after ch03 for cost (user, 2026-10-03); ask before making ch04+.
- Units: 1 The Number System (ch1–14) · 2 Ratios, Proportions, and Percents (15–26) · 3 Expressions and Equations (27–39) · 4 Geometry (40–50) · 5 Statistics and Probability (51–54) · 6 The Coordinate Plane and Functions (55–63).
- Source note: the PDF bookmark for ch29 points to page 1; the map uses page 195.

## Conventions (approved in the pilot on 2026-10-03; later chapters follow them)
- Look: engine chalkboard (`COL.board` background, chalk text, `UI` sans, `MATH` serif). Number families keep the engine hues everywhere: natural coral, whole blue, integer yellow, rational pink, irrational green, real violet. `COL.task` (amber) marks "look here"; good/bad for feedback only.
- Narration: `en-US-AndrewMultilingualNeural`, rate −4%. Read math in words ("negative two point three eight", "the square root of two").
- Questions: quick checks act on the picture (sorter into the number map, tap on the number line, grid classification); practice on `SCREEN`.
- Sign colours: engine `POS` (blue) = positive, `NEG` (coral) = negative, chalk = zero (matches signed tiles, ch11–13). Family hues only in number-type chapters.
- Amber `COL.task` also means distance / absolute value (tapes, the | | bars), from ch03.
- Subject conventions: whole numbers start at 0, natural numbers at 1. Repeating decimals use an overbar. Approximations use ≈ and "…".

## Visual models / available helpers
- Number map (nested rings, `RINGS`/`buildVenn`/`sorter`, engine): number-type chapters (1, 34).
- Number line (`numberLine`, `X`, `dot`, `landDot`, `move`, engine): ch1–3, 11–14, 38.
- Repeat bar: `OV('3')` math part in this book's engine (`['0.', OV('3')]` = 0.3̄); added in ch01, for decimal chapters.
- ch01 chapter helpers (copy or promote when reused): `note` (family title + lines beside the map), `ringIn`, `vnum`/`fly` (numbers in or into the map), `sideEq` (equation aligned on =), `mark` (labelled point on the line), `tapDots` (tap with visible candidate dots).
- ch02 number-line helpers: `pnBand` (tint one side), `pnHops` (unit hops from 0), `pnFlip` (flip a dot across 0, recolour), `pnTip`, `pnArrow`, `pnCoin`, `pnDotFx` (answer dot), `pnBlanks` (blanks with a sentence before each box; accepts leading + and thousands commas). Reuse in ch03, 11–14.
- ch03 helpers: `avTape` (distance tape on the number line, lift/slide, tw or fx), `avVTape` (vertical), `BAR` token, `sv(v)` (signed-colour token), `avRow`/`showT`, `avBox` (dashed "do this first"), `avDiver`, `avSub`. Reuse in ch11–14, ch38.
- Signed tiles (`tile`, `cancelPairs`, engine): ch11–13. Fraction rows, decimal point hops, algebra tiles, balance, coordinate plane: engine, for later units.

## Current decisions
- Pilot chapter 1 approved by the user (2026-10-03). Its look, pacing, question mix and side-notes layout are the model for later chapters; `site/math-notebook/ch01/index.html` is the reference implementation.
- Layout used in ch01: number map on the left (engine `RINGS`), notes column at x ≥ 1290; number line −4…4 with `AXIS.u = 160`.
- Local preview: `python3 -m http.server 8765 -d site` (Papermorph preview; use port 8793 if 8765 is occupied).
- Tests: `tools/math-notebook/smoke_chNN.py` (keyboard runs through quick checks; ch01–ch03).
- Registering: `python3 tools/math-notebook/register.py N minutes` (UNITS, previous CHAPTER.next, chapters.md row).
