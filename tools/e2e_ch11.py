"""Keyboard-only walk through chapter 11: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch11.py

Beat numbers follow BEATS in site/ch11/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch11/index.html")


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

        await at(3)                                    # q1: yellow to all (order matters)
        await typed("11", "4"); await keys("Enter"); assert await score("c-order") == 0
        await keys("Escape", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 4

        await at(6)                                    # q2: simplify, then a missing term
        await typed("2", "3"); await keys("Enter"); assert await score("c-simp") == 1
        await keys("Enter"); await typed("35"); await keys("Enter"); assert await score("c-equiv") == 1
        await keys("Enter"); assert await ev("P.i") == 7

        await at(9)                                    # q3: map scale
        await typed("6"); await keys("Enter"); assert await score("c-map") == 1
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice 1
        await typed("2", "3", "1", "4", "8", "3", "3", "2", "3", "8", "5", "7"); await keys("Enter")
        assert await score("p-simp") == 6, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("1", "2", "1", "2", "1", "2", "Enter"); assert await score("p-equiv") == 6   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("t", "f", "t", "t", "f", "f", "Enter"); assert await score("p-tf") == 6   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 11 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 11 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
