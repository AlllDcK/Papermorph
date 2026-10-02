"""Keyboard-only walk through chapter 60: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch60.py

Beat numbers follow BEATS in site/ch60/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch60/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1604, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(600)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(60)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(260)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1600)
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
        await typed("21", "2", "3"); await keys("Enter"); assert await score("c-mult") == 1
        await pg.locator(".box").nth(1).fill("3"); await pg.locator(".box").nth(2).fill("2"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 4

        await at(6)                                    # q2: divide
        await typed("3", "10", "6"); await keys("Enter"); await ok(); assert await score("c-div") == 2
        await keys("Enter"); assert await ev("P.i") == 7

        await at(9)                                    # q3: rationalize; show answer after a miss
        await keys("2"); assert await score("c-rat") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice
        await typed("56", "5", "1/2", "8", "4"); await keys("Enter"); assert await score("p-md") == 3, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("5", "2", "2", "2", "3", "1", "2", "6", "3"); await keys("Enter"); assert await score("p-rat") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("63", "72", "126", "9"); await keys("Enter"); assert await score("p-area") == 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 60 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 60 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
