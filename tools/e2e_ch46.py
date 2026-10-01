"""Keyboard-only walk through chapter 46: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch46.py

Beat numbers follow BEATS in site/ch46/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch46/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1464, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(460)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(46)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(250)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1500)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(2)                                    # q1: meaning of f(3)
        await keys("1"); assert await score("c-mean") == 0
        await keys("2"); await ok(); await keys("Enter"); assert await ev("P.i") == 3

        await at(5)                                    # q2: pick the point for f(-2)
        await keys("ArrowLeft", "ArrowLeft", "Enter"); assert await score("c-pt") == 0
        assert "height" in await pg.inner_text(".card .fb")
        for _ in range(5): await keys("ArrowDown")
        await keys("Enter"); await ok(); await keys("Enter"); assert await ev("P.i") == 6

        await at(8)                                    # q3: solve for the input; show answer path
        await typed("2"); await keys("Enter"); assert await score("c-solve") == 0
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 9

        await at(10)                                   # practice
        await typed("-2", "21", "13", "6", "49"); await keys("Enter"); assert await score("p-eval") == 5
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("-5", "24", "-2", "2 1/3"); await keys("Enter"); assert await score("p-input") == 4, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("6", "7", "5", "3", "4", "2"); await keys("Enter"); assert await score("p-expr") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 46 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 46 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
