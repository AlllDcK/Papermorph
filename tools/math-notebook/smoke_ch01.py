"""Keyboard smoke test for ch01 quick checks: grid (q1), sorter (q2), tap (q3), then the score card."""
import asyncio, sys
from playwright.async_api import async_playwright
URL = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/math-notebook/').rstrip('/') + '/ch01/'

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page(viewport={'width': 1600, 'height': 1000})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_function('typeof TIMINGS !== "undefined" && typeof BEATS !== "undefined"')
        k = pg.keyboard
        async def at(i): await pg.evaluate(f'hideCover(); seek({i}, false)'); await pg.wait_for_timeout(300)
        async def fb(): return (await pg.locator('#ui .fb').first.inner_text()).strip()
        # q1: −4 → 3; 0 → 2,3; 9 → 1,2,3 (one wrong row first)
        await at(4)
        for keys in (['3'], ['ArrowDown', '2', '3'], ['ArrowDown', '1', '2']):
            for x in keys: await k.press(x)
        print('q1 state:', await pg.evaluate("[...document.querySelectorAll('#ui .grid .row')].map(r => [...r.querySelectorAll('.opt')].map(b => b.getAttribute('aria-pressed') === 'true' ? 1 : 0).join(''))"))
        await k.press('Enter'); print('q1 wrong:', await fb())
        await k.press('3'); await k.press('Enter'); print('q1 right:', await fb())
        # q2: sorter by keys: each number gets its ring key, in tray order
        await at(9)
        await k.press('ArrowRight')
        for ring in '123445': await k.press(ring)
        await k.press('Enter'); print('q2:', await fb())
        # q3: tap −1/2 (second of four points), then −1 (second of two)
        await at(12)
        await k.press('ArrowRight'); await k.press('ArrowRight'); await k.press('Enter'); print('q3a:', await fb())
        await k.press('Enter'); await pg.wait_for_timeout(200)
        await k.press('ArrowLeft'); await k.press('Enter'); print('q3b:', await fb())
        await at(17); print('finish:', (await pg.locator('#ui').inner_text()).replace('\n', ' | ')[:200])
        print('errors:', errs or 'none'); await b.close()
asyncio.run(main())
