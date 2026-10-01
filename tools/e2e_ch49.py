"""Keyboard-only walk through chapter 49: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch49.py

Beat numbers follow BEATS in site/ch49/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch49/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1494, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(490)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(49)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(250)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1500)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(3)                                    # q1: multiply
        await typed("16", "5"); await keys("Enter"); assert await score("c-mult") == 1
        await pg.locator(".box").nth(0).fill("10"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 4

        await at(7)                                    # q2: divide
        await typed("2", "-7"); await keys("Enter"); assert await score("c-div") == 1
        await pg.locator(".box").nth(1).fill("11"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 8

        await at(9)                                    # q3: who is correct; show answer after a miss
        await keys("4"); assert await score("c-who") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice
        await typed("9", "6", "4", "-5", "4"); await keys("Enter"); assert await score("p-exp") == 5
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("5", "4", "-2"); await keys("Enter"); assert await score("p-chain") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("y", "n", "n", "y", "n", "y", "Enter"); assert await score("p-can") == 6, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 49 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 49 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
