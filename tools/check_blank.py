"""Find opening blanks: narration has started but the picture is still empty.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/check_blank.py            # every chapter
    uv run --with playwright tools/check_blank.py ch05 ch06  # some chapters
    LIMIT=0.6 uv run --with playwright tools/check_blank.py  # stricter

Prints chapter, beat index, beat id, empty from, empty until, seconds, for each lesson beat whose
picture stays empty longer than LIMIT (default 1 s) near its start. Question beats are skipped.
No output means no opening blank.
"""
import asyncio, sys, json
from playwright.async_api import async_playwright
LIMIT = float(__import__("os").environ.get("LIMIT", "1.0"))
JS = r"""
(i) => {
  seek(i, false);
  const b = BEATS[i], tm = TIMINGS[b.id];
  const first = (tm.cues[0] || [0])[0];
  // A leaf is visible if its box has size, nothing hides it, and the opacity product up to the scene is > .05.
  const vis = () => {
    let n = 0;
    for (const e of scene.querySelectorAll('text,path,circle,rect,ellipse,line,polygon')) {
      if (e.closest('.qlayer')) continue;
      let o = 1, x = e;
      while (x && x !== scene) { o *= +(x.getAttribute('opacity') ?? 1); if (x.style && x.style.visibility === 'hidden') o = 0; x = x.parentNode; }
      if (o < .05) continue;
      const r = e.getBoundingClientRect();
      if (r.width < 2 && r.height < 2) continue;
      n++;
    }
    return n;
  };
  const out = [];
  for (let t = 0; t <= Math.min(tm.dur, 12); t += .2) { P.t = t; evalTo(t); out.push([+t.toFixed(1), vis()]); }
  return { id: b.id, ask: !!b.ask, first, dur: tm.dur, out };
}
"""
async def main(chs):
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1600, "height": 960})
        rows = []
        for ch in chs:
            await pg.goto(f"http://localhost:8765/{ch}/index.html?beat=0&t=0"); await pg.wait_for_timeout(300)
            n = await pg.evaluate("BEATS.length")
            for i in range(n):
                r = await pg.evaluate(JS, i)
                if r["ask"] or r["id"] in ("finish",): continue
                # blank = the longest run of empty frames that starts before 3 s, measured from the first word
                empty = [t for t, c in r["out"] if c == 0]
                if not empty: continue
                start = max(empty[0], r["first"])
                end = next((t for t, c in r["out"] if t > empty[0] and c > 0), r["dur"])
                gap = end - start
                if gap > LIMIT and empty[0] < 3: rows.append((ch, i, r["id"], round(start, 1), round(end, 1), round(gap, 1)))
        for row in rows: print(*row)
        await b.close()
chs = sys.argv[1:] or [f"ch{n:02d}" for n in range(1, 69)]
asyncio.run(main(chs))
