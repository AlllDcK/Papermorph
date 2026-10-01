"""Keyboard-only walk through chapter 8: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch08.py

Beat numbers follow BEATS in site/ch08/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch08/index.html")


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

        await at(4)                                    # q1: tap 1/6 on a line in sixths (−1…1, index 7)
        await keys("ArrowRight", "Enter"); assert await score("c-line") == 0
        await keys(*["ArrowRight"] * 7, "Enter"); assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 5

        await at(8)                                    # q2: LCM, then a sum that must be simplest
        await typed("24"); await keys("Enter"); assert await score("c-lcm") == 0
        await keys("Backspace", "Backspace"); await pg.keyboard.type("12"); await keys("Enter")
        await keys("Enter"); await typed("11/12"); await keys("Enter"); assert await score("c-add") == 1
        await keys("Enter"); assert await ev("P.i") == 9

        await at(11)                                   # q3: −13/6 is accepted; −26/12 is not simplest
        await typed("-26/12"); await keys("Enter"); assert await score("c-sub") == 0
        await keys(*["Backspace"] * 6); await pg.keyboard.type("−13/6"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 12

        await at(13)                                   # practice 1
        await typed("1 1/4", "-1/3", "-3/5", "1/12", "-1/6", "1 3/5", "-4 1/6"); await keys("Enter")
        assert await score("p-calc") == 7, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("6", "20", "18", "35", "24"); await keys("Enter")                  # practice 2
        assert await score("p-lcm") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("f", "t", "f", "t", "f", "t", "Enter"); assert await score("p-tf") == 6   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 8 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 8 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
