"""Keyboard-only walk through chapter 51: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch51.py

Beat numbers follow BEATS in site/ch51/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch51/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1514, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(510)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(51)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(251)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1510)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(2)                                    # q1: monomial times binomial
        await typed("15", "21"); await keys("Enter"); assert await score("c-mono") == 0
        await pg.locator(".box").nth(0).fill("-15"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 3

        await at(5)                                    # q2: FOIL
        await typed("2", "8"); await keys("Enter"); await ok(); assert await score("c-foil") == 1
        await keys("Enter"); assert await ev("P.i") == 6

        await at(8)                                    # q3: fill the grid (two rows)
        await typed("6", "-4", "-24", "10", "24"); await keys("Enter"); assert await score("c-grid") == 1
        await pg.locator(".box").nth(3).fill("2"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 9

        await at(10)                                   # q4: divide; show answer after a miss
        await keys("2"); assert await score("c-div") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 11

        await at(12)                                   # practice
        await typed("1", "1", "8", "12", "20", "-2", "12"); await keys("Enter"); assert await score("p-mono") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("8", "15", "5", "14", "6", "15", "4", "10", "4", "1"); await keys("Enter"); assert await score("p-bin") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("7", "7", "3", "4", "-6", "4", "3", "1"); await keys("Enter"); assert await score("p-div") == 3, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 51 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 51 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
