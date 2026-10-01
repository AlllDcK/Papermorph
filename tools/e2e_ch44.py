"""Keyboard-only walk through chapter 44: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch44.py

Beat numbers follow BEATS in site/ch44/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch44/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1444, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(440)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(44)

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

        await at(4)                                    # q1: arrangements
        await typed("25", "10000"); await keys("Enter"); assert await score("c-arr") == 1
        await pg.locator(".box").nth(0).fill("120"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 5

        await at(6)                                    # qp: P(8, 3)
        await typed("512"); await keys("Enter"); assert await score("c-npr") == 0
        await pg.locator(".box").nth(0).fill("336"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 7

        await at(9)                                    # q2: permutation vs combination; show answer
        await typed("60", "60"); await keys("Enter"); assert await score("c-pc") == 1
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice 1
        await keys("p", "c", "p", "c", "p", "c", "Enter"); assert await score("p-kind") == 6, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        for v in ["720", "504", "5040", "17576", "190", "36", "20", "35"]:   # practice 2 and 3
            await typed(v); await keys("Enter"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        assert "chapter 44 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 44 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
