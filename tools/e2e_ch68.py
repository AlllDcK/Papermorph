"""Keyboard-only walk through chapter 68: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch68.py

Beat numbers follow BEATS in site/ch68/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch68/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(660)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(66)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(66)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(266)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1660)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(3)                                    # q1: click a solution (1 or 5)
        await keys("ArrowUp", "Enter"); assert await score("c-root") == 0
        await keys("ArrowDown", *["ArrowRight"] * 5, "Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 4

        await at(5)                                    # q2: other root (-4, 0); show answer after a miss
        await keys("ArrowLeft", "ArrowLeft", "Enter"); assert await score("c-other") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 6

        await at(8)                                    # q3: cannonball
        await typed("7.75"); await keys("Enter"); await ok(); assert await score("c-cannon") == 1
        await keys("Enter"); assert await ev("P.i") == 9

        await at(10)                                   # practice 1: two points
        await keys(*["ArrowLeft"] * 6, "Enter"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        await keys(*["ArrowRight"] * 4, "Enter"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        await typed("5", "1"); await keys("Enter"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)   # practice 2
        await typed("-2"); await keys("Enter"); await ok(); await keys("Escape", "Enter"); await pg.wait_for_timeout(150)
        await keys("3"); await ok(); await keys("Enter"); await pg.wait_for_timeout(200)
        assert await score("p-a") == 1 and await score("p-b") == 1 and await score("p-c") == 1, await ev("JSON.stringify(SCORE)")
        await typed("-5", "4", "12"); await keys("Enter"); assert await score("p-sym") == 3   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 68 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 68 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
