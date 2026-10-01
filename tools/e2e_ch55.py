"""Keyboard-only walk through chapter 55: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch55.py

Beat numbers follow BEATS in site/ch55/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch55/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1554, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(550)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(55)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(255)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1550)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(4)                                    # q1: the ac pair
        await keys("1"); assert await score("c-pair") == 0
        await keys("2"); await ok(); await keys("Enter"); assert await ev("P.i") == 5

        await at(7)                                    # q2: four numbers, any valid order
        await typed("3", "1", "2", "5"); await keys("Enter"); await ok(); assert await score("c-fac") == 1
        await keys("Enter"); assert await ev("P.i") == 8

        await at(10)                                   # practice 1: one wrong row, then fixed
        await typed("3", "1", "1", "5", "1", "3", "7", "2", "2", "7", "3", "5", "1", "-2", "3", "-4"); await keys("Enter")
        assert await score("p-fac") == 3, await ev("JSON.stringify(SCORE)")
        await pg.locator(".box").nth(5).fill("2"); await pg.locator(".box").nth(7).fill("3"); await keys("Enter"); await ok()
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("n", "y", "n", "y", "n", "y", "Enter"); assert await score("p-can") == 6
        await keys("Enter"); await pg.wait_for_timeout(200)
        for k in ["2", "1", "2"]:                      # practice 3
            await keys(k); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        assert "chapter 55 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 55 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
