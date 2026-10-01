"""Keyboard-only walk through chapter 35: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch35.py

Beat numbers follow BEATS in site/ch35/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch35/index.html")


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

        await at(3)                                    # q1: read slope and point, signs flipped first
        await typed("3", "2", "4"); await keys("Enter"); assert await score("c-read") == 0
        await pg.locator(".box").nth(1).fill("-2"); await pg.locator(".box").nth(2).fill("-4"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 4

        await at(5)                                    # q2: plot the named point
        await keys(*["ArrowLeft"] * 4, "ArrowUp", "ArrowUp", "Enter"); assert await score("c-plot") == 0   # (-4, 2)
        assert "flipped" in await pg.inner_text(".card .fb")
        await keys(*["ArrowRight"] * 8, *["ArrowDown"] * 4, "Enter")   # (4, -2)
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 6

        await at(8)                                    # q3: slope-intercept
        await typed("4", "-6"); await keys("Enter"); assert await score("c-si") == 1
        await keys("Enter"); assert await ev("P.i") == 9

        await at(10)                                   # q4: standard form
        await typed("17"); await keys("Enter"); assert await score("c-std") == 1
        await keys("Enter"); assert await ev("P.i") == 11

        await at(12)                                   # practice 1
        await typed("5", "3", "1", "-2", "9", "-1", "5", "4/3", "0", "-1", "-2", "-7"); await keys("Enter")
        assert await score("p-read") == 4, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("11", "10", "-31", "7/2"); await keys("Enter"); assert await score("p-b") == 4   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-1", "17", "-2", "-11", "4", "16", "-1", "2"); await keys("Enter")   # practice 3
        assert await score("p-std") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 35 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 35 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
