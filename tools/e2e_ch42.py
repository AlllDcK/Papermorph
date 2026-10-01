"""Keyboard-only walk through chapter 42: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch42.py

Beat numbers follow BEATS in site/ch42/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch42/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1442, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(420)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(42)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(250)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1500)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(4)                                    # q1: spinner probability
        await typed("3/5"); await keys("Enter"); assert await score("c-blue") == 0
        await pg.locator(".box").nth(0).fill("3/8"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 5

        await at(8)                                    # q2: tree; an unreduced fraction is accepted
        await typed("3/12"); await keys("Enter"); await ok(); assert await score("c-tree") == 1
        await keys("Enter"); assert await ev("P.i") == 9

        await at(11)                                   # q3: counting principle
        await typed("10", "16"); await keys("Enter"); assert await score("c-count") == 1
        await pg.locator(".box").nth(0).fill("24"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 12

        await at(13)                                   # q4: complements, then show answer path
        await typed("75", "5/6"); await keys("Enter"); assert await score("c-comp") == 1
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 14

        await at(15)                                   # practice 1
        await typed("1/3", "2/3", "0", "7/12"); await keys("Enter"); assert await score("p-prob") == 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        for v in ["15", "32", "260"]:                  # practice 2
            await typed(v); await keys("Enter"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        await keys("1", "2", "3", "4", "5", "2", "Enter"); assert await score("p-likely") == 6, await ev("JSON.stringify(SCORE)")   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("0.6", "85", "7/10", "92"); await keys("Enter"); assert await score("p-comp") == 4   # practice 4
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 42 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 42 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
