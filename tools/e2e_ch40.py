"""Keyboard-only walk through chapter 40: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch40.py

Beat numbers follow BEATS in site/ch40/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch40/index.html")


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

        await at(4)                                    # q1: mean
        await typed("5"); await keys("Enter"); assert await score("c-mean") == 0
        await pg.locator(".box").nth(0).fill("6"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 5

        await at(7)                                    # q2: click the median
        await keys("ArrowRight", "ArrowRight", "ArrowRight", "Enter"); assert await score("c-median") == 0
        assert "not in order" in await pg.inner_text(".card .fb")
        await keys("ArrowLeft", "ArrowLeft", "Enter"); assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 8

        await at(10)                                   # q3: mode and range
        await typed("4", "8"); await keys("Enter"); assert await score("c-moderange") == 1
        await pg.locator(".box").nth(0).fill("7"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 11

        await at(12)                                   # q4: outlier, then show answer path
        await keys("1"); assert await score("c-outlier") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 13

        await at(14)                                   # practice 1
        await typed("14", "15", "15", "10"); await keys("Enter"); assert await score("p-five") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("1", "0", "2", "1", "0", "2", "Enter"); assert await score("p-modes") == 6, await ev("JSON.stringify(SCORE)")   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("7", "6.5", "5", "9"); await keys("Enter"); assert await score("p-six") == 4   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 40 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 40 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
