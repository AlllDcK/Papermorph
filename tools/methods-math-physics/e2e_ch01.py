"""Keyboard/mouse walk-through of chapter 1's question types: domain picks, the agreement grid,
exponent boxes (supBlanks), decimal-comma answers, Show answer, first-try scores, finish card.

    python3 -m http.server 8765 -d site &
    URL=http://localhost:8765/methods-math-physics/ch01/ uv run --with playwright==1.56.0 tools/methods-math-physics/e2e_ch01.py

Beat numbers follow BEATS in site/methods-math-physics/ch01/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
URL = os.environ.get("URL", "http://localhost:8765/methods-math-physics/ch01/")
Q1, Q2, Q3, Q5, FINAL1, FINAL3 = 4, 6, 14, 21, 23, 25


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(400)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(70)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(40)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(300)

        async def fb():
            return await pg.inner_text(".card .fb")

        async def ok():
            t = await fb(); assert t.startswith("Верно"), t

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        assert await ev("JSON.stringify(rat('0,5'))") == "[5,10]", "decimal comma"
        assert await ev("JSON.stringify(rat('−2'))") == "[-2,1]"
        await keys("Space"); await pg.wait_for_timeout(1500)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        await at(Q1)                                   # domain: left side (wrong), then right side, then the inside by mouse
        await keys("ArrowRight", "Enter"); assert (await fb()).startswith("Не совсем"); assert await score("c-edge") == 0
        await keys("ArrowRight", "ArrowRight", "Enter"); await ok()
        await keys("Enter"); await pg.wait_for_timeout(150)
        await pg.locator(".qlayer .hit").nth(3).click(); await ok()
        await keys("Enter"); await pg.wait_for_timeout(150); assert await ev("P.i") == Q1 + 1

        await at(Q2)                                   # agreement grid: one row wrong, then fixed
        await keys("1", "1", "1", "2", "Enter"); assert await ev("SCORE['c-agree'].right") == 3
        await keys("ArrowUp", "ArrowUp", "2", "Enter"); await ok()

        await at(Q3)                                   # fastest mode, then an exponent box (sign accepted)
        await keys("ArrowRight", "ArrowRight", "ArrowRight", "Enter"); await ok()
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert await pg.locator("input.box.sup").count() == 1
        await typed("-4"); await keys("Enter"); await ok(); assert await score("c-exp") == 1

        await at(Q5)                                   # reduction: unicode minus
        await typed("3", "−2"); await keys("Enter"); await ok()

        await at(FINAL1)                               # exponents, then fractions with a decimal comma
        await typed("1", "9"); await keys("Enter"); await ok()
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("0,75", "1/4", "3/4", "0,25"); await keys("Enter"); await ok()
        assert await score("p-cube") == 2

        await at(FINAL3)                               # wrong first, Show answer, then the answer choice
        await typed("4", "-2"); await keys("Enter"); assert await score("p-rate") == 0
        await keys("Escape", "s"); assert (await fb()).startswith("Ответ")
        await keys("Enter"); await pg.wait_for_timeout(150)
        await keys("2"); assert await score("p-answer") == 0
        await keys("1"); await ok()
        await keys("Enter"); await pg.wait_for_timeout(300)
        assert "глава 1 пройдена" in (await pg.inner_text(".card")).lower()
        await at(FINAL3)                               # a revisit keeps the first-try score
        await typed("16", "-2"); await keys("Enter"); await ok(); assert await score("p-rate") == 0
        await at(FINAL3 + 1); await keys("r"); await pg.wait_for_timeout(200)
        assert await ev("P.i") == 0 and await ev("Object.keys(SCORE).length") == 0, "restart clears scores"

        for i in range(await ev("BEATS.length")):      # every beat must rebuild without errors
            await ev(f"seek({i}, false)")
        assert not errs, errs
        print("ch01 walk-through passed")
        await b.close()

asyncio.run(main())
