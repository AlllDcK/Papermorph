"""Browser walk-through of chapter 1: playback, pauses, every quick check and the chapter practice.

    python3 -m http.server 8765 -d site &
    uv run --with playwright tools/e2e_ch01.py      # CHROME=/path/to/chromium to pick a browser

Beat numbers below follow the BEATS order in site/ch01/index.html; update them when beats move.
"""
import asyncio, os
from playwright.async_api import async_playwright
SH = os.environ.get("CHROME")
URL = os.environ.get("URL", "http://localhost:8765/ch01/index.html")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(400)
        async def at(x, y):  # stage coords -> screen point
            return await pg.evaluate(f"(() => {{ const s=$('stage'), p=s.createSVGPoint(); p.x={x}; p.y={y}; const q=p.matrixTransform(s.getScreenCTM()); return [q.x,q.y]; }})()")
        async def click_stage(x, y):
            sx, sy = await at(x, y); await pg.mouse.click(sx, sy)
        async def drag(x0, y0, x1, y1):
            a = await at(x0, y0); c = await at(x1, y1)
            await pg.mouse.move(*a); await pg.mouse.down(); await pg.mouse.move(*c, steps=8); await pg.mouse.up()
        fb = lambda: pg.locator(".card .fb").inner_text()
        await pg.click("#cover"); await pg.wait_for_timeout(1500)
        assert await pg.evaluate("P.t > .8 && !P.audio.paused")
        # captions: off by default, C toggles, text follows the narration
        assert await pg.evaluate("$('caption').hidden")
        await pg.keyboard.press("c"); await pg.wait_for_timeout(200)
        print("caption:", await pg.inner_text("#caption"))
        await pg.keyboard.press("c")
        # q1: wrong then right, effects run, continue advances
        await pg.evaluate("seek(3, true)"); await pg.wait_for_timeout(300)
        await click_stage(920, 610); print("q1 wrong:", await fb())
        await click_stage(800, 610); print("q1 right:", await fb())
        await pg.wait_for_timeout(700)
        assert await pg.evaluate("st(S.dots[0]).s === 1"), "pulse should settle"
        await pg.click(".card .btn.go:visible"); await pg.wait_for_timeout(300)
        assert await pg.evaluate("P.i") == 4
        # q2: tap -3, then families
        await pg.evaluate("seek(5, true)"); await pg.wait_for_timeout(300)
        await click_stage(440, 610); print("q2a:", await fb())
        await pg.click(".card .btn.go:visible")
        await pg.click(".card .opt:has-text('Whole')"); await pg.click(".card .btn:text-is('Check')"); print("q2b wrong:", await fb())
        await pg.click(".card .opt:has-text('Whole')"); await pg.click(".card .opt:has-text('Integer')"); await pg.click(".card .btn:text-is('Check')"); print("q2b right:", await fb())
        await pg.click(".card .btn.go:visible"); assert await pg.evaluate("P.i") == 6
        # q3 choices + show answer path
        await pg.evaluate("seek(10, true)"); await pg.wait_for_timeout(300)
        await pg.locator(".card .opt").nth(2).click(); print("q3a wrong:", await fb())
        await pg.click(".card .btn.quiet:visible"); print("q3a shown:", await fb())
        await pg.click(".card .btn.go:visible")
        await pg.locator(".card .opt").nth(1).click(); print("q3b:", await fb())
        # q4 grid
        await pg.evaluate("seek(14, true)"); await pg.wait_for_timeout(300)
        rows = pg.locator(".grid .row")
        for i, lab in enumerate(["Rational", "Irrational", "Rational", "Irrational", "Irrational"]):
            await rows.nth(i).locator(f".opt:has-text('{lab}')").first.click() if lab == "Rational" else await rows.nth(i).get_by_role("button", name="Irrational").click()
        await pg.click(".card .btn:text-is('Check')"); print("q4 one wrong:", await fb())
        await rows.nth(4).locator(".opt").nth(0).click(); await pg.click(".card .btn:text-is('Check')"); print("q4 right:", await fb())
        # q5 sorter with real mouse drags
        await pg.evaluate("seek(18, true)"); await pg.wait_for_timeout(300)
        await drag(1425, 230, 640, 330)   # -6 -> integers
        await drag(1425, 330, 175, 470)   # 3/8 -> rational
        await drag(1425, 430, 560, 620)   # 9 -> natural
        print("q5 regions:", await pg.evaluate("[...S.q.querySelectorAll('.tok')].map(c => c.region)"))
        await pg.click(".card .btn:text-is('Check')"); print("q5:", await fb())
        # worked examples play straight on: no pause, no card
        await pg.evaluate("seek(8, true)")
        await pg.wait_for_function("P.i === 9", timeout=25000)
        assert await pg.evaluate("!P.waiting") and await pg.locator(".card").count() == 0
        # the guide reacts: wrong answer wobbles, right answer hops
        await pg.evaluate("seek(3, true)"); await pg.wait_for_timeout(300)
        await click_stage(1040, 610); assert await pg.evaluate("document.querySelector('.card .mascot').classList.contains('oops')")
        await click_stage(800, 610); assert await pg.evaluate("document.querySelector('.card .mascot').classList.contains('happy')")
        # chapter practice: sort via keyboard path (select + Enter on ring label)
        await pg.evaluate("seek(22, true)"); await pg.wait_for_timeout(300)
        await pg.click(".card .btn:text-is('Check')"); print("final1 empty:", (await fb())[:60])
        await pg.click(".card .btn.quiet:visible"); await pg.wait_for_timeout(1800)
        print("final1 revealed regions ok:", await pg.evaluate("[...S.q.querySelectorAll('.tok')].every(c => regionAt(st(c).x, st(c).y) === c.answer)"))
        await pg.click(".card .btn.go:visible")
        # final2 all right
        ans = [[0,1,2,3,5],[2,3,5],[1,2,3,5],[3,5],[2,3,5],[4,5]]
        rows = pg.locator(".grid .row")
        for i, a in enumerate(ans):
            for k in a: await rows.nth(i).locator(".opt").nth(k).click()
        await pg.click(".card .btn:text-is('Check')"); print("final2:", await fb())
        await pg.click(".card .btn.go:visible")
        rows = pg.locator(".grid .row")
        for i, v in enumerate([0, 1, 1, 0, 0]):  # True, False, False, True, True
            await rows.nth(i).locator(".opt").nth(v).click()
        await pg.click(".card .btn:text-is('Check')"); print("final3 one wrong:", await fb())
        await pg.click(".card .btn.quiet:visible"); await pg.click(".card .btn.go:visible")
        await pg.wait_for_timeout(300)
        print("finish:", (await pg.locator(".card").inner_text()).replace("\n", " | "))
        print("score:", await pg.evaluate("JSON.stringify(SCORE)"))
        # stray layers after leaving quizzes
        await pg.evaluate("seek(19, false)")
        print("leftover qlayer:", await pg.evaluate("!!document.querySelector('.qlayer')"), "cards:", await pg.locator(".card").count())
        print("errors:", errs)
        await b.close()


async def keyboard_only():
    """Answer every question with keys alone."""
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=SH, args=["--autoplay-policy=no-user-gesture-required"])
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(400)
        kb = pg.keyboard
        async def keys(*ks):
            for k in ks:
                await kb.press(k); await pg.wait_for_timeout(60)
        ev = pg.evaluate
        await keys("Space"); await pg.wait_for_timeout(600)
        assert await ev("P.started && P.playing")
        await keys("?"); assert await ev("!$('help').hidden && !P.playing")
        await keys("Escape"); assert await ev("$('help').hidden && P.playing")
        await keys("c"); assert await ev("captions"); await keys("c")
        await keys("ArrowRight", "ArrowRight", "ArrowRight"); assert await ev("P.i") == 3
        await keys("ArrowRight"); assert await ev("P.i") == 3, "arrows belong to the question"
        await keys("Enter", "Enter"); assert await ev("P.i") == 4                    # tap 0, continue
        await keys("ArrowRight"); assert await ev("P.i") == 5
        await keys("ArrowRight", "ArrowRight", "ArrowRight", "Enter", "Enter")       # tap -3, next
        await keys("3", "Enter", "Enter"); assert await ev("P.i") == 6               # -4 is an integer
        await keys("Shift+ArrowLeft"); assert await ev("P.i") in (5, 6)
        await ev("seek(10, true)"); await pg.wait_for_timeout(200)
        await keys("3"); assert await ev("SCORE['c-frac'].right") == 0
        await keys("s", "Enter", "2", "Enter"); assert await ev("P.i") == 11
        await ev("seek(14, true)"); await pg.wait_for_timeout(200)
        await keys("1", "2", "1", "2", "1", "Enter"); assert await ev("SCORE['c-ratirr'].right") == 5
        await keys("Enter")
        await ev("seek(18, true)"); await pg.wait_for_timeout(200)
        await keys("ArrowRight", "3", "4", "1", "Enter"); assert await ev("SCORE['c-map'].right") == 3
        await ev("seek(22, true)"); await pg.wait_for_timeout(200)
        await keys("ArrowRight", "1", "2", "3", "4", "4", "1", "5", "1", "Enter")
        assert await ev("SCORE['p-sort'].right") == 8, await ev("JSON.stringify(SCORE)")
        await keys("Enter"); await pg.wait_for_timeout(200)
        for row in ["12346", "346", "2346", "46", "346", "56"]:
            await keys(*row, "ArrowDown")
        await keys("Enter"); assert await ev("SCORE['p-fam'].right") == 6
        await keys("Enter"); await pg.wait_for_timeout(200)
        await keys("t", "f", "f", "t", "f", "Enter"); assert await ev("SCORE['p-tf'].right") == 5
        await keys("Enter"); await pg.wait_for_timeout(200)
        assert "Chapter 1 complete" in await pg.inner_text(".card")
        await keys("Enter"); await pg.wait_for_timeout(200); assert await ev("P.i") == 0
        print("keyboard only: all questions answered, errors:", errs)
        assert not errs
        await b.close()

asyncio.run(main())
asyncio.run(keyboard_only())
