"""Keyboard-only walk through chapter 7: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch07.py

Beat numbers follow BEATS in site/ch07/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch07/index.html")


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

        await at(4)                                    # q1: fraction answer; an equal but unsimplified value also counts here
        await typed("1/6"); await keys("Enter"); assert await score("c-mult") == 0     # sign missing
        await keys("Backspace", "Backspace", "Backspace"); await pg.keyboard.type("-2/12"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await pg.wait_for_timeout(1800); assert await pg.locator("#scene path[stroke-dasharray='1 1']").count() >= 4, "cancel slashes drawn"
        await keys("Enter"); assert await ev("P.i") == 5

        await at(9)                                    # q2: choose the method, then simplest form is required
        await keys("2"); assert await score("c-method") == 0
        await keys("3", "Enter"); await typed("14/20"); await keys("Enter"); assert await score("c-divide") == 0
        await keys(*["Backspace"] * 5); await pg.keyboard.type("7/10"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # q3
        await typed("15"); await keys("Enter"); assert await score("c-recip") == 1
        await keys("Enter"); assert await ev("P.i") == 12

        await at(13)                                   # practice 1: simplest form
        await typed("1/6", "-1/2", "1/4", "5/6", "-1/6", "-10", "1 1/2"); await keys("Enter")
        assert await score("p-calc") == 7, await ev("JSON.stringify(SCORE)")          # 1 1/2 is accepted for 3/2: same value, simplest form
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("7/2", "−5/3", "1/9", "-1", "4/5"); await keys("Enter")   # practice 2
        assert await score("p-recip") == 5, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("t", "f", "t", "f", "t", "f", "Enter"); assert await score("p-tf") == 6   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 7 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 7 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
