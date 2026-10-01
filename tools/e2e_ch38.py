"""Keyboard-only walk through chapter 38: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch38.py

Beat numbers follow BEATS in site/ch38/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch38/index.html")


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

        await at(3)                                    # q1: a point in the overlap
        await keys(*["ArrowUp"] * 5, "Enter"); assert await score("c-both") == 0   # (0, 5)
        assert "only" in await pg.inner_text(".card .fb")
        await keys(*["ArrowDown"] * 5, "Enter")   # (0, 0)
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 4

        await at(5)                                    # q2: point on the solid edge
        await keys("2"); assert await score("c-edge") == 0
        await keys("1"); assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 6

        await at(7)                                    # practice 1
        await keys("y", "n", "y", "n", "y", "Enter"); assert await score("p-yes") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-2", "3", "3", "-5", "-3", "-2", "-2", "-1"); await keys("Enter")   # practice 2
        assert await score("p-corner") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("n", "y", "n", "n", "y", "Enter"); assert await score("p-incl") == 5   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 38 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 38 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
