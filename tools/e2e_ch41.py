"""Keyboard-only walk through chapter 41: every quick check and chapter practice, right, wrong and shown answers.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch41.py

Beat numbers follow BEATS in site/ch41/index.html.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch41/index.html")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1441, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(410)
        ev = pg.evaluate

        async def keys(*ks):
            for k in ks:
                await pg.keyboard.press(k); await pg.wait_for_timeout(60)

        async def typed(*vals):
            for i, v in enumerate(vals):
                if i: await keys("Tab")
                await pg.keyboard.type(v); await pg.wait_for_timeout(41)

        async def at(i):
            await ev(f"seek({i}, true)"); await pg.wait_for_timeout(250)

        score = lambda k: ev(f"SCORE['{k}'] && SCORE['{k}'].right")
        await keys("Space"); await pg.wait_for_timeout(1500)
        assert await ev("P.playing && P.t > .5"), "lesson plays"

        async def ok():
            assert "Correct" in await pg.inner_text(".card .fb"), await pg.inner_text(".card .fb")

        await at(2)                                    # q1: click a table cell
        await keys("ArrowRight", "Enter"); assert await score("c-cell") == 0
        await keys("ArrowRight", "Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 3

        await at(5)                                    # q2: two histogram questions
        await typed("5"); await keys("Enter"); await ok(); assert await score("c-h30") == 1
        await keys("Enter"); await pg.wait_for_timeout(150)
        await typed("7"); await keys("Enter"); assert await score("c-h20") == 0
        await pg.locator(".box").nth(0).fill("8"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 6

        await at(8)                                    # q3: quartiles in one row
        await typed("4", "9", "12"); await keys("Enter"); assert await score("c-box") == 0
        await pg.locator(".box").nth(1).fill("8"); await keys("Enter"); await ok()
        await keys("Enter"); assert await ev("P.i") == 9

        await at(11)                                   # q4: pick the negative plot; show answer after a miss
        await keys("ArrowRight", "Enter"); assert await score("c-corr") == 0
        await keys("s"); assert "Answer" in await pg.inner_text(".card .fb")
        await keys("Enter"); assert await ev("P.i") == 12, (await ev("P.i"), await ev("document.activeElement.outerHTML.slice(0,80)"))

        await at(13)                                   # practice 1: three table questions
        for v in ["3", "24", "14"]:
            await typed(v); await keys("Enter"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        for v in ["11", "8", "20"]:                    # practice 2: histogram
            await typed(v); await keys("Enter"); await ok(); await keys("Enter"); await pg.wait_for_timeout(150)
        await keys("1", "2", "3", "2", "1", "2", "Enter"); assert await score("p-corr") == 6, await ev("JSON.stringify(SCORE)")   # practice 3
        await keys("Enter"); await pg.wait_for_timeout(200)
        await typed("4", "6.5", "10", "14", "20"); await keys("Enter"); assert await score("p-five") == 5   # practice 4
        assert await ev("S.f4n") == 5
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "chapter 41 complete" in (await pg.inner_text(".card")).lower()
        await keys("r"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0

        for i in range(await ev("BEATS.length")):
            await ev(f"seek({i}, false)")
        print("chapter 41 keyboard walk-through passed; errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
