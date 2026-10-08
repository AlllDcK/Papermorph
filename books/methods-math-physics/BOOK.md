# Методы математической физики — book plan

Read this compact current state for chapter work. The chapter map/status lives in `chapters.md`; storyboards, errata and feedback live in `chapters/chNN.md`.

Source: В. А. Треногин, И. С. Недосекина, «Методы математической физики. Практикум», МИСиС, 2012 (196 pp.).

## Intake
- Readers: university students (physics/chemistry and applied-math programmes) who know calculus, first-order linear ODEs and basic Fourier series · Tone: clear, calm lecturer; explains *why*, never childish · Narration language: Russian · Guide character: the default infinity guide.
- Slug: `methods-math-physics` · Primary language code: `ru` · Asset approach: code/SVG only.
- Source: `book.pdf` (copy of `book/Trenogin_…pdf` in the repo) · Page map: `sections.json` (PDF page = printed page) · 196 pages, 15 chapters in 4 units.
- Pending user confirmation (defaults chosen for the pilot): voice, unit split, chapter list in `chapters.md`, colour meanings below.

## Conventions (proposed in the pilot; later chapters follow them once approved)
- Look: engine chalkboard; one picture per beat, formula column on the left (x ≈ 80–760), the live picture (rod, graph, domain) on the right (x ≈ 840–1540). Long derivations are built one line at a time with `eqLine`-style rows, older rows dimmed.
- Colour meanings (same meaning across the book):
  - initial data φ(x), the bottom edge t = 0 of the domain: `COL.int` (yellow);
  - boundary data α₀(t), α_l(t), the side edges, the rod ends, the boundary-fitting function w: `COL.whole` (blue);
  - sources f(x, t): `COL.rat` (pink);
  - the solution u(x, t): `COL.chalk`; the rod is filled with the heat ramp `HEAT` (cold blue-grey → amber → coral);
  - Fourier modes k = 1, 2, 3, 4: `MODE = [COL.irr, COL.real, COL.nat, COL.task]` (green, violet, coral, amber);
  - emphasis / "look here": `COL.task`.
- Notation: as in the book — u_t − a²u_xx = f, Q = {0 < x < l, t > 0}, φ_k, f_k(t), T_k(t), λ_k = (kπ/l)². Summation index over odd terms is `n` (k = 2n − 1), never `l` (the book reuses `l` in ex. 1.2). Numbers use a decimal comma on screen (0,5).
- Narration: Edge TTS `ru-RU-DmitryNeural`, rate `-6%`. Say symbols in words, Cyrillic phonetics: «икс», «тэ», «у», «эль», «ка», «а квадрат», «фи», «альфа», «лямбда ка», «пи», «синус икс», «е в степени минус тэ». Partial derivatives: «производная у по тэ», «вторая производная у по икс».
- Questions: act on the picture where possible (`pickEls` on domain edges, modes, curves); numbers through `blanks` (a decimal comma is accepted); exponent boxes via `supBlanks` (a box raised into an exponent). Practice sets reuse the book's own problems (§ *.5) with verified answers.
- Subject conventions: "формальное решение" = the series built by the Fourier method before convergence is checked; mention convergence only as "проверяется позже (п. 4.3)".

## Visual models / available helpers
All helpers live in `site/methods-math-physics/ch01/index.html` (prefix `mp`); move the ones a second chapter needs into a shared `lib/mp.js` and load it after the engine.
- **Rod + profile** (ch01; later heat chapters 3, 4, 12–14): `mpRod` (heat-coloured cells, `rod.set(u)`), `mpClamps` (blue ends), `mpGraph` / `mpCurve` / `mpSet` (profile on [0, L]), `mpClock` (`t = 0,00`), `mpRun` (model time τ over a tween), `heat(v)` ramp, `mpVArrow` (amplitude arrow).
- **Domain Q** (ch01; ch05, 12, 13): `mpDomain` + `DOM` geometry; `domPicks()` gives pickEls targets (left, bottom, right, inside).
- **Mode spectrum** (ch01; ch02, 03, 05–08): `mpBars` (`bars.set([T1, T2, …])`), `mpTrio` (three mode graphs side by side).
- Layout: `mpRow` (words + math on one baseline; `cm(colour, …)` for coloured math), `mpBox` (amber frame), `mpFrame` (frame a token), `mpBrace`, `mpArrow`, `dotAt`; questions: `supBlanks` (answer box raised into an exponent; sign-agnostic via `test`).
- **String** (planned, ch05, ch15): a vibrating string drawn like the profile graph.
- Engine additions in this book's `lib/engine.js` (marked "this book"): Russian UI text; `M()` parts `Sub(x)`, nested `E([...])`/`Sub([...])`, `Lim(lo, hi)` for ∑/∫, fractions of part arrays `F([...], [...])`; `rat()` accepts a decimal comma; `window.TIMINGS_PLACEHOLDER` turns captions on with a note.

## Current decisions
- Pilot = chapter 1 (§§ 1.1–1.4 + selected problems from § 1.5).
- Edge TTS host `speech.platform.bing.com` was blocked by the session's network policy: ch01 ships with silent placeholder clips timed from the text (`tools/methods-math-physics/placeholder_audio.py`, which flags `TIMINGS_PLACEHOLDER` so lessons show captions). When the host is allowed, run `tts.py` (see chapters/ch01.md); the flag disappears and the beats re-sync to the real word marks.
- Planning files (`BOOK.md`, `chapters.md`, `chapters/`, `sections.json`), narration sources and tools are committed with `git add -f` despite `.gitignore`, so the work survives the cloud session; the PDF and `pages/` stay out.
