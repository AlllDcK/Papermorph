"""Keyboard-only walk through chapter 52: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch52.py

Beat numbers follow BEATS in site/ch52/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch52/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1524, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(520)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(52)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(252)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1520)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(4)                                    # q1: GCF of monomials
        await typed("2", "3", "1"); await keys("Enter"); assert await score("c-gcf") == 0
        await pg.locator(".box").nth(1).fill("2"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 5

        await at(7)                                    # q2: factor
        await typed("6", "5", "2", "3"); await keys("Enter"); await ok(); assert await score("c-fac") == 1
        await keys("Enter"); assert await ev("P.i") == 8

        await at(10)                                   # q3: fully factored? show answer after a miss
        await keys("1"); assert await score("c-full") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 11

        await at(12)                                   # practice 1: four GCF choices
        for k in ["1", "1", "2", "2"]:
            await keys(k); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        await typed("4", "4", "3", "3", "3", "2", "1", "3", "6", "5"); await keys("Enter"); assert await score("p-fac") == 4, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("y", "n", "n", "y", "y", "n", "Enter"); assert await score("p-full") == 6
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 52 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 52 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
