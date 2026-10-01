"""Keyboard-only walk through chapter 2: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch02.py

Beat numbers follow BEATS in site/ch02/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch02/index.html")


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

        async def typed(*vals):  # type into consecutive boxes
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(40)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(250)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1500)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        await at(4)                                            # q1: order, true/false
        await keys("t", "t", "f", "f", "Enter"); assert await score("c-order") == 4
        await keys("Enter"); assert await ev("P.i") == 5

        await at(9)                                            # q2: property name, then fill-in
        await keys("1"); assert await score("c-name") == 0
        assert "Not quite" in await pg.inner_text(".card .fb")
        await keys("2", "Enter")
        await typed("100", "117"); await keys("Enter"); assert await score("c-group") == 1
        await keys("Enter"); assert await ev("P.i") == 10

        await at(13)                                           # q3: fill-in, wrong then fixed
        await typed("4", "20", "24"); await keys("Enter")
        assert await score("c-expand") == 0 and await pg.locator(".box.bad").count() == 1
        await keys("Backspace", "Backspace"); await pg.keyboard.type("25"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 14

        await at(16)                                           # q4: wrong, then show answer
        await keys("1", "s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 17

        await at(18)                                           # chapter practice 1: name the property
        await keys("1", "2", "3", "1", "2", "4", "3", "Enter"); assert await score("p-name") == 7
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("22", "52", "21", "6", "24", "30"); await keys("Enter")   # practice 2: expand
        assert await score("p-expand") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("f", "f", "f", "t", "t", "f", "Enter"); assert await score("p-tf") == 6
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 2 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter would open the next chapter

        # every beat fast-forwards cleanly (replay from any step)
        n = await ev("BEATS.length")
        for i in range(n):
            await ev(f"seek({i}, false)")
        print("chapter 2 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
