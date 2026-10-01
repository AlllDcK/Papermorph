"""Keyboard-only walk through chapter 12: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch12.py

Beat numbers follow BEATS in site/ch12/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch12/index.html")


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

        await at(2)                                    # q1: unit rate on a double number line
        await typed("30"); await keys("Enter"); assert await score("c-rate") == 1
        await keys("Enter"); assert await ev("P.i") == 3

        await at(6)                                    # q2: unit price, then the better deal
        await typed("1.25"); await keys("Enter"); assert await score("c-price") == 1
        await keys("Enter", "1"); assert await score("c-deal") == 0
        await keys("2", "Enter"); assert await ev("P.i") == 7

        await at(8)                                    # q3
        await typed("16"); await keys("Enter"); assert await score("c-predict") == 0
        await keys("Backspace", "Backspace"); await pg.keyboard.type("15"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 9

        await at(10)                                   # practice 1 (0.40 = 0.4, 1 1/3 = 4/3)
        await typed("8", "35", "0.40", "60", "1 1/3", "3.30"); await keys("Enter")
        assert await score("p-rate") == 6, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("2", "1", "2", "1", "Enter"); assert await score("p-deal") == 4   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("t", "f", "t", "f", "t", "Enter"); assert await score("p-tf") == 5   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 12 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 12 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
