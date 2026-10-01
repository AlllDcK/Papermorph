"""Keyboard-only walk through chapter 37: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch37.py

Beat numbers follow BEATS in site/ch37/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch37/index.html")


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

        await at(3)                                    # q1: solid or dashed, then which side
        await keys("2"); assert await score("c-solid") == 0
        await keys("1"); assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter", "1"); assert await score("c-side") == 0
        await keys("2"); assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 4

        await at(5)                                    # q2: any solution point
        await keys("Enter"); assert await score("c-any") == 0   # (0, 0)
        assert "other side" in await pg.inner_text(".card .fb")
        await keys("ArrowRight", "ArrowRight", "ArrowUp", "ArrowUp", "Enter")   # (2, 2) on the dashed line
        assert "dashed" in await pg.inner_text(".card .fb")
        await keys("ArrowRight", "ArrowUp", "Enter")   # (3, 3)
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 6

        await at(8)                                    # practice 1
        await keys("3", "2", "1", "3", "2", "Enter"); assert await score("p-graph") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("n", "y", "y", "n", "y", "Enter"); assert await score("p-yes") == 5   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("1", "5", "-4/3", "4", "3/2", "3", "3", "-5/2"); await keys("Enter")   # practice 3
        assert await score("p-solve") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 37 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 37 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
