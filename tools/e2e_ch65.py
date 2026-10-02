"""Keyboard-only walk through chapter 65: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch65.py

Beat numbers follow BEATS in site/ch65/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch65/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1654, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(650)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(65)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(65)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(265)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1650)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(4)                                    # q1: a, b, c
        await typed("2", "-5", "-6"); await keys("Enter"); assert await score("c-abc") == 0
        await pg.locator(".box").nth(1).fill("5"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 5

        await at(6)                                    # q2: formula; an equivalent form is accepted
        await typed("6", "148", "4"); await keys("Enter"); await ok(); assert await score("c-qf") == 1
        await keys("Enter"); assert await ev("P.i") == 7

        await at(9)                                    # practice
        await typed("-5", "1", "-6", "-2", "-4", "1.5", "2/3", "-2"); await keys("Enter"); assert await score("p-int") == 4, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-7", "41", "2", "1", "97", "8", "1", "40", "4"); await keys("Enter"); assert await score("p-rad") == 2
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-5", "73", "4", "-2", "5"); await keys("Enter"); assert await score("p-move") == 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 65 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 65 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
