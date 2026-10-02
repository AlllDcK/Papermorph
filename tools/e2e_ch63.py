"""Keyboard-only walk through chapter 63: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch63.py

Beat numbers follow BEATS in site/ch63/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch63/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1634, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(630)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(63)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(63)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(263)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1630)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(3)                                    # q1: square root property (sign of the typed value ignored)
        await typed("12", "3/49"); await keys("Enter"); assert await score("c-sqrt") == 1
        await pg.locator(".box").nth(1).fill("-3/7"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 4

        await at(5)                                    # q2: find the mistake
        await keys("1"); assert await score("c-err") == 0
        await keys("2"); await ok(); await keys("Enter"); assert await ev("P.i") == 6

        await at(7)                                    # q3: h ± k√n; show answer after a miss
        await typed("5", "1", "18"); await keys("Enter"); assert await score("c-bin") == 0
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 8

        await at(9)                                    # practice
        await typed("5", "10", "3", "2/3"); await keys("Enter"); assert await score("p-sqrt") == 4, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-1", "1", "15", "-7", "5", "2", "3", "2", "3"); await keys("Enter"); assert await score("p-bin") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("2", "0", "1", "0", "1", "2", "Enter"); assert await score("p-count") == 6
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 63 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 63 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
