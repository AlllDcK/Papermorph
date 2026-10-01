"""Keyboard-only walk through chapter 48: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch48.py

Beat numbers follow BEATS in site/ch48/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch48/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1484, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(480)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(48)

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

        await at(4)                                    # q1: add
        await typed("7", "5"); await keys("Enter"); assert await score("c-add") == 0
        await pg.locator(".box").nth(1).fill("17"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 5

        await at(6)                                    # q2: subtract (choice)
        await keys("1"); assert await score("c-sub") == 0
        await keys("2"); await ok(); await keys("Enter"); assert await ev("P.i") == 7

        await at(8)                                    # q3: perimeter; show answer path
        await typed("6", "6"); await keys("Enter"); assert await score("c-per") == 0
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 9

        await at(10)                                   # practice
        await keys("2", "1", "3", "1", "2", "3", "Enter"); assert await score("p-name") == 6, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("4", "13", "17", "12", "3", "5"); await keys("Enter"); assert await score("p-add") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("4", "8", "5", "9", "4"); await keys("Enter"); assert await score("p-sub") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 48 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 48 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
