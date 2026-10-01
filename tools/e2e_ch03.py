"""Keyboard-only walk through chapter 3: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch03.py

Beat numbers follow BEATS in site/ch03/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch03/index.html")


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

        await at(4)                                    # q1: tap ÷ in 18 − 6 ÷ 3 + 1
        await keys("ArrowRight", "Enter"); assert await score("c-first") == 0        # − is wrong
        await keys("ArrowRight", "Enter"); assert "Correct" in await pg.inner_text(".card .fb")
        await pg.wait_for_timeout(1900)
        assert await ev("S.q1[3]._st.o") < .05, "÷ collapsed into its result"
        await keys("Enter"); await typed("17"); await keys("Enter"); assert await score("c-value") == 1
        await keys("Enter"); assert await ev("P.i") == 5

        await at(8)                                    # q2: × comes first in 8 × 5 ÷ 4 − 3
        await keys("ArrowRight", "Enter"); assert await score("c-md") == 1
        await keys("Enter"); await typed("8"); await keys("Enter")
        assert await score("c-md-value") == 0 and await pg.locator(".box.bad").count() == 1
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")   # Esc leaves the box, then S
        await keys("Enter"); assert await ev("P.i") == 9

        await at(10)                                   # q3: tickets
        await typed("31"); await keys("Enter"); assert await score("c-tickets") == 1
        await keys("Enter"); assert await ev("P.i") == 11

        await at(12)                                   # practice 1: simplify
        await typed("8", "17", "8", "38", "24", "11", "5.5"); await keys("Enter")
        assert await score("p-simplify") == 7, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("3", "5", "1", "3", "2", "5", "Enter"); assert await score("p-first") == 6   # practice 2: first operation
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("f", "t", "f", "t", "f", "t", "Enter"); assert await score("p-tf") == 6       # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 3 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 3 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
