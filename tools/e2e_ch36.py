"""Keyboard-only walk through chapter 36: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch36.py

Beat numbers follow BEATS in site/ch36/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch36/index.html")


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

        await at(3)                                    # q1: pick the crossing point
        await keys("ArrowLeft", "Enter"); assert await score("c-cross") == 0   # (-1, 0): first line only
        assert "only" in await pg.inner_text(".card .fb")
        await keys("ArrowRight", "ArrowRight", "ArrowUp", "ArrowUp", "Enter")   # (1, 2)
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 4

        await at(7)                                    # q2: same line
        await keys("2"); assert await score("c-count") == 0
        await keys("3"); assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 8

        await at(9)                                    # practice 1
        await typed("1", "4", "5", "0", "-6", "-4", "-1", "3"); await keys("Enter")
        assert await score("p-sol") == 4, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("3", "2", "1", "2", "3", "Enter"); assert await score("p-count") == 5   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("y", "n", "y", "n", "y", "Enter"); assert await score("p-yes") == 5   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 36 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 36 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
