"""Keyboard-only walk through chapter 21: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch21.py

Beat numbers follow BEATS in site/ch21/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch21/index.html")


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

        await at(4)                                    # q1: count terms; boxes appear on a right answer
        await keys("2"); assert await score("c-count") == 0
        await keys("3", "Enter"); assert await ev("P.i") == 5

        await at(7)                                    # q2: coefficient keeps its sign; degree
        await typed("0.7"); await keys("Enter"); assert await score("c-coef") == 0
        await pg.locator(".box").nth(0).fill("-0.7"); await keys("Enter")
        await keys("Enter"); await typed("13"); await keys("Enter"); assert await score("c-deg") == 1
        await keys("Enter"); assert await ev("P.i") == 8

        await at(9)                                    # q3
        await keys("1"); assert await score("c-std") == 0
        await keys("2", "Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice 1
        await keys("2", "4", "1", "3", "1", "Enter"); assert await score("p-name") == 5
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-0.4", "1", "9", "5", "1/2"); await keys("Enter")                 # practice 2
        assert await score("p-parts") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("1", "2", "1", "2", "Enter"); assert await score("p-std") == 4   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 21 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 21 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
