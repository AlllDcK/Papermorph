"""Keyboard/mouse walk-through of § 1.1's question types (side picks on Π, decimal-comma and negative
answers, grid, choice, Show answer, first-try scores, finish card with the section label), plus a
rebuild of every beat in lessons 1–4.

    python3 -m http.server 8765 -d site &
    uv run --with playwright==1.56.0 tools/optimal-control-hyperbolic/e2e.py

Beat numbers follow BEATS in site/optimal-control-hyperbolic/ch01/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
BASE = os.environ.get("URL", "http://localhost:8765/optimal-control-hyperbolic/")
Q1, Q2, FINAL1, FINAL3 = 6, 10, 18, 20


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(BASE + "ch01/"); await pg.wait_for_timeout(400)
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
        assert await ev("JSON.stringify(rat('0,3'))") == "[3,10]", "decimal comma"
        await keys("Space"); await pg.wait_for_timeout(1500)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        await at(Q1)                                   # sides of Π: left (wrong) by keyboard, then right by mouse
        await keys("ArrowRight", "ArrowRight", "Enter"); assert (await fb()).startswith("Не совсем"); assert await score("c-side") == 0
        await pg.locator(".qlayer .hit").nth(2).click(); await ok()
        await keys("Enter"); await pg.wait_for_timeout(150); assert await ev("P.i") == Q1 + 1

        await at(Q2)                                   # decimal commas and an integer
        await typed("0,3", "0,3", "1"); await keys("Enter"); await ok(); assert await score("c-kink") == 3

        await at(FINAL1)                               # unicode minus with a decimal comma
        await typed("0,3", "−0,4"); await keys("Enter"); await ok()

        await at(FINAL3)                               # grid: one row wrong, fixed; then the choice wrong first, Show answer
        await keys("1", "2", "3", "2", "Enter"); assert await ev("SCORE['p-sides'].right") == 3
        await keys("1", "Enter"); await ok()
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("2"); assert await score("p-weak") == 0
        await keys("s"); assert (await fb()).startswith("Ответ")
        await keys("Enter"); await pg.wait_for_timeout(250)
        card = await pg.inner_text(".card")
        assert "§ 1.1 пройден" in card.lower() and "Следующий параграф" in card, card
        await at(Q1); assert await score("c-side") == 0, "first try kept after revisiting"
        await keys("Home"); await pg.wait_for_timeout(200)

        for ch in ["ch01", "ch02", "ch03", "ch04"]:   # every beat must rebuild without errors
            await pg.goto(BASE + ch + "/"); await pg.wait_for_timeout(400)
            for i in range(await ev("BEATS.length")):
                await ev(f"seek({i}, false)")
        assert not errs, errs
        print("optimal-control-hyperbolic: § 1.1 walk-through and rebuild of lessons 1–4 passed")
        await b.close()

asyncio.run(main())
