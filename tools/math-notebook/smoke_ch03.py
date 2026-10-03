"""Keyboard smoke test for ch03: taps with distance-tape effects (q1, q3), blanks beside the depth scale (q2),
evaluation blanks with a fraction (final1, final2), sentence blanks with a $ (final3), T/F grid (final4)."""
import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright
URL = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/math-notebook/').rstrip('/') + '/ch03/'

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page(viewport={'width': 1600, 'height': 1000})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_function('typeof TIMINGS !== "undefined" && typeof BEATS !== "undefined"')
        k = pg.keyboard
        async def at(i): await pg.evaluate(f'hideCover(); seek({i}, false)'); await pg.wait_for_timeout(300)
        async def fb(): return (await pg.locator('#ui .fb').first.inner_text()).strip()
        async def nxt(): await k.press('Enter'); await pg.wait_for_timeout(200)
        # q1: |x| = 2 among [-3,-2,0,3]: −3 first (wrong), then −2; then the farther of [-6, 4]
        await at(3)
        await k.press('ArrowRight'); await k.press('Enter'); print('q1a wrong:', await fb())
        await k.press('ArrowRight'); await k.press('Enter'); print('q1a right:', await fb())
        await nxt()
        await k.press('ArrowRight'); await k.press('Enter'); print('q1b:', await fb())
        # q2: depth 120, debt 18.25
        await at(6); await pg.wait_for_timeout(200)
        await k.type('-120'); await k.press('Enter'); print('q2a wrong:', await fb())
        await pg.locator('#ui input.box').first.fill('120'); await k.press('Enter'); print('q2a right:', await fb())
        await nxt(); await pg.wait_for_timeout(200)
        await k.type('18.25'); await k.press('Enter'); print('q2b:', await fb())
        # q3: −|−3| = −3 (2nd of 4), |6 − 2| = 4 (last of 4)
        await at(9)
        await k.press('ArrowRight'); await k.press('ArrowRight'); await k.press('Enter'); print('q3a:', await fb())
        await nxt()
        await k.press('ArrowLeft'); await k.press('Enter'); print('q3b:', await fb())
        await at(13); await pg.wait_for_timeout(200)
        for v in ['23', '61', '3.5', '3/8', '0']: await k.type(v); await k.press('Tab')
        await k.press('Escape'); await k.press('Enter'); print('final1:', await fb())
        await at(14); await pg.wait_for_timeout(200)
        for v in ['5', '12', '-38', '12', '15']: await k.type(v); await k.press('Tab')
        await k.press('Escape'); await k.press('Enter'); print('final2 wrong:', await fb())
        await k.press('s'); print('final2 shown:', await fb())
        await at(15); await pg.wait_for_timeout(200)
        for v in ['$64.20', '85', '9']: await k.type(v); await k.press('Tab')
        await k.press('Escape'); await k.press('Enter'); print('final3:', await fb())
        await at(16)
        for x in 'tftf': await k.press(x)
        await k.press('t'); await k.press('Enter'); print('final4:', await fb())
        await at(17); print('finish:', (await pg.locator('#ui').inner_text()).replace('\n', ' | ')[:200])
        Path('/tmp/animebook-mn-ch03').mkdir(parents=True, exist_ok=True)
        await pg.screenshot(path='/tmp/animebook-mn-ch03/smoke_end.png')
        print('errors:', errs or 'none'); await b.close()
asyncio.run(main())
