# Оптимальное управление гиперболическими системами — book plan

Read this compact current state for chapter work. The chapter map/status lives in `chapters.md`; storyboards, errata and feedback live in `chapters/chNN.md`.

Source: А. В. Аргучинцев, «Оптимальное управление гиперболическими системами», М.: ФИЗМАТЛИТ, 2007 (168 pp.; scanned PDF with a cp1251 text layer: decode each character 0xA0–0xFF as cp1251; formulas read from page images).

## Intake
- Readers: students (upper-year applied mathematics / control) who know ODEs, first-order PDEs at the level of "solution is constant along a line", basic Lebesgue language (a.e., L∞). The book is a research monograph; lessons explain ideas and structure of proofs, not every estimate · Tone: clear, calm lecturer · Narration language: Russian · Guide character: the default infinity guide.
- Slug: `optimal-control-hyperbolic` (the user's path `books/mybook/` did not exist; the PDF arrived at `book/Arguchintsev_…pdf` and is copied to `books/optimal-control-hyperbolic/book.pdf`) · Primary language code: `ru` · Asset approach: code/SVG only.
- Source map: `sections.json` (PDF page = printed page + 1) · 231 PDF pages; lessons = the book's sections (§), units = the book's chapters (Глава 1–5).
- Scope now: §§ 1.1–1.4 (lessons 1–4), as requested by the user, for review.
- Pending user confirmation (defaults chosen): voice, the toy example, colour meanings below, one lesson per section.

## Conventions (proposed; later lessons follow them once approved)
- Look: engine chalkboard. The running picture is the rectangle Π in the plane (s, t): s to the right, t **upwards** (as in the book's characteristic pictures), so the left side s = s0 is a timeline where control enters. Formulas on the left (x ≈ 70–800), Π on the right (x ≈ 900–1500), or Π on the left when a control/adjoint timeline is drawn beside its left side.
- Colour meanings (same meaning across the book):
  - initial data x⁰(s), p(s), bottom edge t = t0: `COL.int` (yellow);
  - the "+" family (aᵢ > 0), components x⁺, the left side s = s0, the boundary ODE state x⁺(s0, t): `COL.whole` (blue);
  - the "−" family (aᵢ < 0), components x⁻, the right side s = s1, q(t): `COL.rat` (pink);
  - aᵢ = 0 family: `COL.dim`;
  - control u(t), the set U, Δu, needle: `COL.nat` (coral);
  - cost: J, φ, F, the top edge t = t1: `COL.irr` (green);
  - adjoint ψ, p and Pontryagin functions H, h: `COL.real` (violet);
  - emphasis / "look here": `COL.task` (amber).
- Notation: as in the book — (1.1) ∂x/∂t + A(s, t)∂x/∂s = f(x, s, t), Π = (s0, s1) × (t0, t1), S, T, D_A x, x⁺/x⁻, u(t) ∈ U, g, J, φ, F, ψ, p, H, h, needle (τ, ε, ū), η. Equation numbers as in the book ((1.1)–(1.8), (2.1)–(2.5), (3.1)–(3.12), (4.1)–(4.3)). Decimal comma on screen.
- Running toy example (all four lessons; verified in `chapters/ch02.md`): s, t ∈ [0, 1], n = 1, a = 1, f = 0, x(s, 0) = 0; left side x(0, t) = y(t) with ẏ = u, y(0) = 0, U = [−1, 1]; J(u) = ∫₀¹ (3s − 1) x(s, 1) ds. Then x(s, 1) = y(1 − s) ("the top edge is a photograph of the boundary history"), ψ(s, 1) = 1 − 3s, ψ(0, t) = 3t − 2, p(t) = (3t − 1)(1 − t)/2, u* = −1 on [0, 1/3), +1 on (1/3, 1], J* = −4/27; J(±1) = 0.
- Narration: Edge TTS `ru-RU-DmitryNeural`, rate `-6%`. Symbols in words: «эс», «тэ», «икс», «икс плюс», «а итое», «пси», «пэ», «аш», «фи», «эпсилон», «тау», «у с чертой», «дэ а икс» (D_A x), «пи» for Π («прямоугольник пи»), «дельта». Lessons are called «параграф».
- Questions: act on the picture where possible (`pickEls` on Π's sides and characteristic families); numbers through `blanks` (decimal comma and fractions accepted); `grid` for classifying; `choice` for statements with a per-option explanation. Practice uses the toy example and small transport problems with verified answers.
- Subject conventions: "характеристика" = solution of ds/dt = aᵢ(s, t); "точка входа" = the boundary point where it enters Π as t grows; the adjoint gets its data where forward characteristics leave Π.

## Visual models / available helpers
Shared helpers live in `site/optimal-control-hyperbolic/lib/oc.js` (prefix `oc`, loaded after the engine):
- **Domain Π** (all lessons): `ocDomain(p, {x0, y0, w, h, …})` → `{ g, X(s), Y(t), bottom, left, right, top, label }` for s, t ∈ [0, 1]; `ocEdgePicks(D)` gives `pickEls` targets.
- **Characteristics**: `ocTrace(a, s, t, dir)` integrates ds/dt = a(s, t) to the boundary; `ocChar(D, pts, color)` draws one; `ocFamily(D, a, color, …)` a family.
- **Field**: `ocField(D, f, …)` colours Π by a function x(s, t) (cells), `.set(f)` to redraw; `ocRamp(v)` the colour ramp.
- **Graphs**: `ocGraph(p, {x0, y0, w, k, lo, hi, az, …})` for a function of z ∈ [0, 1] (`az: .5` puts the vertical axis in the middle, e.g. h over U = [−1, 1]); `ocCurve`, `ocSet`, `ocRun` (model time).
- **Timelines beside the left side**: `ocVGraph(p, D, {…})` a graph of a function of t drawn vertically along the side (control u, state y, adjoint p).
- Layout: `ocRow` (words + math on one baseline; `cm(colour, …)`), `ocBox`, `ocArrow`, `ocBrace`, `dotAt`, `mline`, `text`, `fmt`.
- Engine additions in this book's `lib/engine.js` (marked "this book"): Russian UI text, `Sub()`, nested `E([...])`, `Lim(lo, hi)`, part-array fractions, decimal comma in `rat()`, `window.TIMINGS_PLACEHOLDER` captions (all from the previous Russian book); `Ov(x)` overline (Π̄ — the combining macron does not render) and `Tl(x)` tilde (x̃); `CHAPTER.label` ('§ 1.1') on the cover and finish card («§ 1.1 пройден», «Следующий параграф», «Оглавление»).
- Toy-example data shared by all lessons: `TOY` and `U_STAR`, `U_ONE`, `U_MINUS` in `lib/oc.js`.
- Tests: `tools/optimal-control-hyperbolic/e2e.py` (question types of § 1.1 + rebuild of every beat of lessons 1–4).

## Current decisions
- One lesson per section of the book; the contents page shows them as § 1.1, § 1.2 … (`SEC` in `index.html`), units as «Глава N».
- Edge TTS host `speech.platform.bing.com` is blocked by this session's network policy: lessons ship with silent placeholder clips timed from the text (`tools/optimal-control-hyperbolic/placeholder_audio.py`, flags `TIMINGS_PLACEHOLDER`, captions on). When the host is allowed, run `tts.py` per lesson (see each `chapters/chNN.md`).
- Planning files, narration sources and tools are committed with `git add -f` despite `.gitignore`; the PDF and `pages/` stay out.
