"""Keyboard-only walk through chapter 67: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch67.py

Beat numbers follow BEATS in site/ch67/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch67/index.html")


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

        await at(3)                                    # q1: click the vertex (2, -3)
        await keys("ArrowRight", "Enter"); assert await score("c-vtx") == 0
        await keys("ArrowRight", "ArrowDown", "ArrowDown", "ArrowDown", "Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 4

        await at(6)                                    # q2: vertex form
        await typed("3", "4"); await keys("Enter"); assert await score("c-vf") == 0
        await pg.locator(".box").nth(1).fill("-4"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 7

        await at(10)                                   # q3: vertex (1, 4); show answer after a miss
        await keys("Enter"); assert await score("c-vtx2") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 11

        await at(12)                                   # practice 1
        await keys("2"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        await typed("3", "-1", "3", "4", "8", "4", "2"); await keys("Enter"); assert await score("p-desc") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("1", "4", "-2", "-18", "-1.5", "-16", "1", "4"); await keys("Enter"); assert await score("p-vtx") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("ArrowRight", *["ArrowDown"] * 9, "Enter"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)   # practice 3: vertex (1, -9)
        await keys(*["ArrowDown"] * 8, "Enter"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)                  # y-intercept (0, -8)
        await keys("ArrowLeft", "ArrowLeft", "Enter"); await ok()                                                                # x-intercept (-2, 0)
        assert await score("p-pv") == 1 and await score("p-py") == 1 and await score("p-px") == 1
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 67 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 67 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
