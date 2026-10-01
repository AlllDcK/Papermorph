"""Keyboard-only walk through chapter 43: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch43.py

Beat numbers follow BEATS in site/ch43/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch43/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1443, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(430)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(43)

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

        await at(3)                                    # q1: independent events
        await typed("1/6"); await keys("Enter"); assert await score("c-ind") == 0
        await pg.locator(".box").nth(0).fill("1/8"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 4

        await at(6)                                    # q2: without replacement
        await typed("9/25"); await keys("Enter"); assert await score("c-dep") == 0
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 7

        await at(8)                                    # q3: two choice questions
        await keys("2"); assert await score("c-kind1") == 0
        await keys("1"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        await keys("2"); await ok(); assert await score("c-kind2") == 1
        await keys("Enter"); assert await ev("P.i") == 9

        await at(10)                                   # practice 1
        await keys("i", "d", "i", "d", "i", "d", "Enter"); assert await score("p-kind") == 6, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("1/4", "1/12", "1/12", "1/6"); await keys("Enter"); assert await score("p-ind") == 4   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("1/45", "1/9", "2/9", "0"); await keys("Enter"); assert await score("p-dep") == 4   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 43 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 43 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
