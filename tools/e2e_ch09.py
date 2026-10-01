"""Keyboard-only walk through chapter 9: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch09.py

Beat numbers follow BEATS in site/ch09/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch09/index.html")


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

        await at(4)                                    # q1: decimal sum; the answer digits appear on the stage
        await typed("5.12"); await keys("Enter"); assert await score("c-add") == 0
        await keys(*["Backspace"] * 4); await pg.keyboard.type("17.05"); await keys("Enter")
        assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 5

        await at(7)                                    # q2: sign, then value
        await keys("1"); assert await score("c-sign") == 0
        await keys("2", "Enter"); await typed("-2.3"); await keys("Enter"); assert await score("c-diff") == 1
        await keys("Enter"); assert await ev("P.i") == 8

        await at(9)                                    # q3: find the mistake
        await keys("2"); assert await score("c-error") == 1
        await keys("Enter"); assert await ev("P.i") == 10

        await at(11)                                   # practice 1 (6.0 and 6 are the same number)
        await typed("5.8", "-1.6", "-7.25", "6.0", "12.76", "4.35", "-7.55"); await keys("Enter")
        assert await score("p-calc") == 7, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("3", "2", "1", "2", "1", "2", "Enter"); assert await score("p-sign") == 6   # practice 2
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("f", "t", "f", "t", "t", "f", "Enter"); assert await score("p-tf") == 6   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 9 complete" in await pg.inner_text(".card")
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 9 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
