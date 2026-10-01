"""Keyboard-only walk through chapter 34: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch34.py

Beat numbers follow BEATS in site/ch34/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch34/index.html")


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

        await at(3)                                    # q1: read m and b
        await typed("-2", "-5"); await keys("Enter"); assert await score("c-read") == 0
        await pg.locator(".box").nth(1).fill("5"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 4

        await at(5)                                    # q2: plot the y-intercept, then one slope step
        await keys(*["ArrowLeft"] * 4, "Enter"); assert await score("c-yint") == 0   # (-4, 0)
        assert "x-axis" in await pg.inner_text(".card .fb")
        await keys("s", "Enter")
        await keys("ArrowRight", "ArrowDown", "Enter"); assert await score("c-step") == 1   # (1, -1)
        await keys("Enter"); assert await ev("P.i") == 6

        await at(8)                                    # q3: x-intercept
        await typed("3"); await keys("Enter"); assert await score("c-xint") == 1
        await keys("Enter"); assert await ev("P.i") == 9

        await at(10)                                   # practice 1
        await typed("2", "-9", "7/3", "11/8", "-1", "4", "-3", "5", "1/4", "0"); await keys("Enter")
        assert await score("p-read") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-4", "14", "-3/8", "-43/8", "-6", "-3", "1/2", "0"); await keys("Enter")   # practice 2, book's answer first
        assert await score("p-two") == 3
        await pg.locator(".box").nth(0).fill("-7/2"); await pg.locator(".box").nth(1).fill("27/2"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("3", "-3/5", "-3/2", "-3", "3/4", "-3", "4", "2"); await keys("Enter")   # practice 3
        assert await score("p-int") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 34 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 34 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
