"""Keyboard-only walk through chapter 57: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch57.py

Beat numbers follow BEATS in site/ch57/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch57/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1574, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(570)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(57)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(257)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1570)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(4)                                    # q1: square roots
        await typed("8", "12", "0"); await keys("Enter"); assert await score("c-sq") == 2
        await pg.locator(".box").nth(1).fill("13"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 5

        await at(6)                                    # q2: rational or irrational
        await keys("r", "r", "i", "Enter"); await ok(); assert await score("c-rat") == 3
        await keys("Enter"); assert await ev("P.i") == 7

        await at(9)                                    # q3: who is correct; show answer after a miss
        await keys("1"); assert await score("c-who") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice
        await typed("1", "9", "-6", "3 2/3", "-10/3"); await keys("Enter"); assert await score("p-simp") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("n", "i", "r", "r", "i", "r", "Enter"); assert await score("p-kind") == 6
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("f", "t", "f", "t", "f", "Enter"); assert await score("p-tf") == 5
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 57 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 57 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
