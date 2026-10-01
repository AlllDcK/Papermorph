"""Keyboard-only walk through chapter 6: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch06.py

Beat numbers follow BEATS in site/ch06/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch06/index.html")


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

        await at(4)                                    # q1: signs of products; the arrow flips per right row
        await keys("1"); await keys("Enter"); assert await score("c-sign") == 0
        await keys("ArrowUp", "2", "1", "2", "1", "Enter")     # single-choice rows advance by themselves
        assert "Correct" in await pg.inner_text(".card .fb")
        await pg.wait_for_timeout(700); assert await ev("S.qa.inner._st.r") == 720, "arrow flipped for each row"
        await keys("Enter"); assert await ev("P.i") == 5

        await at(8)                                    # q2: zero factor, then a quotient
        await keys("1"); assert await score("c-zero") == 0
        await keys("3", "Enter"); await typed("9"); await keys("Enter"); assert await score("c-div") == 0
        await keys("Backspace"); await pg.keyboard.type("-9"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 9

        await at(11)                                   # practice 1
        await typed("-88", "8", "18", "-9", "-4", "18", "16"); await keys("Enter")
        assert await score("p-simplify") == 7, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("2", "1", "3", "1", "2", "2", "Enter"); assert await score("p-sign") == 6   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("t", "f", "t", "f", "f", "t", "Enter"); assert await score("p-tf") == 6   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 6 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 6 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
