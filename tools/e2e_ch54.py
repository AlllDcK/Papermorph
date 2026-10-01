"""Keyboard-only walk through chapter 54: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch54.py

Beat numbers follow BEATS in site/ch54/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch54/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1544, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(540)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(54)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(254)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1540)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(4)                                    # q1: pick the factor pair
        await keys("ArrowRight", "Enter"); assert await score("c-pair") == 0
        await keys("ArrowRight", "Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 5

        await at(7)                                    # q2: factor pair in either order
        await typed("-16", "3"); await keys("Enter"); await ok(); assert await score("c-fac") == 1
        await keys("Enter"); assert await ev("P.i") == 8

        await at(9)                                    # q3: who is correct; show answer after a miss
        await keys("1"); assert await score("c-who") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice: a wrong pair first, then fixed
        await typed("7", "2", "3", "10", "-6", "-1", "-12", "-5", "-3", "2", "-9", "5"); await keys("Enter"); assert await score("p-fac") == 5, await ev("JSON.stringify(SCORE)")
        await pg.locator(".box").nth(11).fill("6"); await keys("Enter"); await ok()
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("n", "y", "n", "y", "n", "y", "Enter"); assert await score("p-can") == 6
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("12", "-4", "-2", "-16", "-11", "-1", "-7", "5"); await keys("Enter"); assert await score("p-sign") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 54 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 54 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
