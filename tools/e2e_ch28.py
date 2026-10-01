"""Keyboard-only walk through chapter 28: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch28.py

Beat numbers follow BEATS in site/ch28/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch28/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(400)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(40)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(250)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1500)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        await at(3)                                    # q1
        await keys("1"); assert await score("c-rw") == 0
        await keys("2", "Enter"); assert await ev("P.i") == 4

        await at(6)                                    # q2
        await typed("32", "180"); await keys("Enter"); assert await score("c-use") == 0
        await pg.locator(".box").nth(1).fill("212"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 7

        await at(8)                                    # practice 1
        await keys("2", "1", "3", "1", "Enter"); assert await score("p-rw") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("5", "7", "2.5", "10"); await keys("Enter"); assert await score("p-use") == 4   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("t", "f", "t", "t", "Enter"); assert await score("p-tf") == 4   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 28 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 28 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
