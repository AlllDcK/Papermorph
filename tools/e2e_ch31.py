"""Keyboard-only walk through chapter 31: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch31.py

Beat numbers follow BEATS in site/ch31/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch31/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(400)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(40)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(250)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1500)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        await at(4)                                    # q1: plot (−4, 2) with arrow keys
        await keys("ArrowUp", "ArrowUp", *["ArrowRight"] * 4, "Enter"); assert await score("c-plot") == 0   # (4, 2)
        await keys(*["ArrowLeft"] * 8, "Enter"); assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 5

        await at(6)                                    # q2: quadrant
        await keys("3"); assert await score("c-quad") == 0
        await keys("4", "Enter"); assert await ev("P.i") == 7

        await at(9)                                    # practice 1
        await keys("3", "1", "2", "5", "4", "Enter"); assert await score("p-quad") == 5
        await keys("Enter"); await pg.wait_for_timeout(300)
        await keys(*["ArrowRight"] * 5, "Enter"); assert await score("p-p1") == 1          # (5, 0)
        await keys("Enter"); await keys(*["ArrowLeft"] * 7, *["ArrowUp"] * 3, "Enter"); assert await score("p-p2") == 1
        await keys("Enter"); await pg.wait_for_timeout(200)
        # click the grid for the last one
        box = await ev("(() => { const s=$('stage'), p=s.createSVGPoint(); p.x=S.P.PX(0); p.y=S.P.PY(-5); const q=p.matrixTransform(s.getScreenCTM()); return [q.x,q.y]; })()")
        await pg.mouse.click(*box); assert await score("p-p3") == 1
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-1", "4", "9", "2", "7", "12"); await keys("Enter"); assert await score("p-dr") == 2   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 31 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 31 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
