"""Keyboard-only walk through chapter 62: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch62.py

Beat numbers follow BEATS in site/ch62/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch62/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1624, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(620)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(62)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(62)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(262)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1620)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(4)                                    # q1: two solutions, either order
        await typed("2", "5"); await keys("Enter"); assert await score("c-solve") == 0
        await pg.locator(".box").nth(0).fill("-5"); await pg.locator(".box").nth(1).fill("-2"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 5

        await at(6)                                    # q2: find the mistake
        await keys("3"); assert await score("c-err") == 0
        await keys("1"); await ok(); await keys("Enter"); assert await ev("P.i") == 7

        await at(9)                                    # q3: GCF first; show answer after a miss
        await typed("1", "5/2"); await keys("Enter"); assert await score("c-gcf") == 0
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice
        await typed("-3", "7", "-4", "-1/2", "2/3", "-4", "3 1/2", "-4/3"); await keys("Enter"); assert await score("p-fac") == 4, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("8", "-4", "-5", "4", "5/6", "-2"); await keys("Enter"); assert await score("p-rhs") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("1.5", "-7", "7", "4", "0"); await keys("Enter"); assert await score("p-more") == 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 62 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 62 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
