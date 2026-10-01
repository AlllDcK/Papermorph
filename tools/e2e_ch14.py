"""Keyboard-only walk through chapter 14: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch14.py

Beat numbers follow BEATS in site/ch14/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch14/index.html")


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

        await at(3)                                    # q1: decimal and simplest fraction
        await typed("0.35", "35/100"); await keys("Enter"); assert await score("c-convert") == 0
        await keys(*["Backspace"] * 6); await pg.keyboard.type("7/20"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 4

        await at(6)                                    # q2
        await typed("22.5"); await keys("Enter"); assert await score("c-pct") == 1
        await keys("Enter"); assert await ev("P.i") == 7

        await at(9)                                    # q3
        await typed("108"); await keys("Enter"); assert await score("c-whole") == 0
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice 1
        await typed("17/20", "0.17", "40", "6.5", "2.5"); await keys("Enter")
        assert await score("p-convert") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("5.1", "60", "75", "45", "125"); await keys("Enter")      # practice 2
        assert await score("p-solve") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("t", "f", "f", "t", "t", "f", "Enter"); assert await score("p-tf") == 6   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 14 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 14 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
