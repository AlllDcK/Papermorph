"""Keyboard-only walk through chapter 27: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch27.py

Beat numbers follow BEATS in site/ch27/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch27/index.html")


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

        await at(3)                                    # q1: pick the graph for an "and"
        await keys("1"); assert await score("c-and") == 0
        await keys("2", "Enter"); assert await ev("P.i") == 4

        await at(5)                                    # q2: "or"
        await keys("3"); assert await score("c-or") == 1
        await keys("Enter"); assert await ev("P.i") == 6

        await at(7)                                    # q3: interval notation
        await keys("1"); assert await score("c-int") == 0
        await keys("2", "Enter"); assert await ev("P.i") == 8

        await at(9)                                    # practice 1: three graphs
        await keys("1", "Enter", "3", "Enter", "1"); assert await score("p-g3") == 0
        await keys("2", "Enter"); await pg.wait_for_timeout(200)
        assert await score("p-g1") == 1 and await score("p-g2") == 1
        await keys("1", "3", "2", "2", "1", "Enter"); assert await score("p-int") == 5   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("t", "f", "t", "f", "t", "Enter"); assert await score("p-tf") == 5   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 27 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 27 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
