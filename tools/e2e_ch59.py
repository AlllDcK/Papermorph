"""Keyboard-only walk through chapter 59: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch59.py

Beat numbers follow BEATS in site/ch59/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch59/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1594, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(590)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(59)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(259)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1590)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(4)                                    # q1: like radicals
        await typed("6", "-3"); await keys("Enter"); assert await score("c-like") == 1
        await pg.locator(".box").nth(0).fill("7"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 5

        await at(7)                                    # q2: simplify first; show answer after a miss
        await keys("1"); assert await score("c-simp") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 8

        await at(9)                                    # practice
        await typed("11", "-4", "3", "3", "20"); await keys("Enter"); assert await score("p-like") == 4, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-1", "7", "4", "5"); await keys("Enter"); assert await score("p-simp") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("5", "4", "9", "9", "9"); await keys("Enter"); assert await score("p-per") == 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 59 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 59 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
