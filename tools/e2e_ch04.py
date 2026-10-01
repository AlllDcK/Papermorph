"""Keyboard-only walk through chapter 4: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch04.py

Beat numbers follow BEATS in site/ch04/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch04/index.html")


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

        await at(6)                                    # q1: where does −2 + 6 land?
        await keys("ArrowRight", "Enter"); assert await score("c-line") == 0          # −8 is wrong
        await keys(*["ArrowRight"] * 12, "Enter"); assert "Correct" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 7

        await at(12)                                   # q2: sign, then value
        await keys("2"); assert await score("c-sign") == 0
        await keys("1", "Enter"); await typed("7"); await keys("Enter"); assert await score("c-diff") == 1
        await keys("Enter"); assert await ev("P.i") == 13

        await at(14)                                   # q3: thermometer
        await typed("-7"); await keys("Enter"); assert await score("c-temp") == 0
        await keys("Backspace", "Backspace"); await pg.keyboard.type("7"); await keys("Enter")
        await pg.wait_for_timeout(1600)
        assert await ev("S.th.merc._st.a_height") > 250, "mercury rose"
        await keys("Enter"); assert await ev("P.i") == 15

        await at(16)                                   # practice 1: sums
        await typed("5", "-5", "−13", "7", "-21", "-9", "0"); await keys("Enter")
        assert await score("p-sums") == 7, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("2", "1", "2", "3", "1", "2", "Enter"); assert await score("p-sign") == 6   # practice 2: sign
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("t", "f", "t", "f", "t", "f", "Enter"); assert await score("p-tf") == 6      # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 4 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0   # R restarts; Enter opens the next chapter

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 4 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
