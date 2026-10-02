"""Keyboard-only walk through chapter 61: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch61.py

Beat numbers follow BEATS in site/ch61/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch61/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1614, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(610)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(61)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(61)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(261)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1610)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(3)                                    # q1: a, b, c
        await typed("-1/3", "4", "4"); await keys("Enter"); assert await score("c-abc") == 0
        await pg.locator(".box").nth(1).fill("0"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 4

        await at(6)                                    # q2: pick the parabola; show answer after a miss
        await keys("ArrowRight", "Enter"); assert await score("c-par") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 7

        await at(8)                                    # practice
        await keys("y", "n", "n", "y", "y", "n", "Enter"); assert await score("p-quad") == 6, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("8", "-2", "9", "1", "0", "-7", "-3", "1", "5"); await keys("Enter"); assert await score("p-abc") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("y", "y", "n", "y", "n", "Enter"); assert await score("p-sol") == 5
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 61 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 61 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
