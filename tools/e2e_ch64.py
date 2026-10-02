"""Keyboard-only walk through chapter 64: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch64.py

Beat numbers follow BEATS in site/ch64/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch64/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1644, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(640)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(64)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(64)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(264)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1640)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(3)                                    # q1: complete the square
        await typed("121", "49/2"); await keys("Enter"); assert await score("c-add") == 1
        await pg.locator(".box").nth(1).fill("12 1/4"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 4

        await at(5)                                    # q2: solve; show answer after a miss
        await typed("5", "1", "29"); await keys("Enter"); assert await score("c-solve") == 0
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 6

        await at(9)                                    # practice
        await typed("1", "36", "81/4", "1/9"); await keys("Enter"); assert await score("p-add") == 4, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("9", "2", "6", "-2", "1", "11", "-5", "3", "3"); await keys("Enter"); assert await score("p-solve") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-1/2", "4", "-18", "0"); await keys("Enter"); assert await score("p-two") == 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 64 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 64 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
