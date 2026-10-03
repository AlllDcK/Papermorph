"""Keyboard smoke test for ch02: sign grid (q1), taps (q2, q3), sentence blanks with + and commas (final1, final2), T/F grid (final3)."""
import asyncio, sys
from playwright.async_api import async_playwright
URL = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/math-notebook/').rstrip('/') + '/ch02/'

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page(viewport={'width': 1600, 'height': 1000})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_function('typeof TIMINGS !== "undefined" && typeof BEATS !== "undefined"')
        k = pg.keyboard
        async def at(i): await pg.evaluate(f'hideCover(); seek({i}, false)'); await pg.wait_for_timeout(300)
        async def fb(): return (await pg.locator('#ui .fb').first.inner_text()).strip()
        async def nxt(): await k.press('Enter'); await pg.wait_for_timeout(200)
        # q1: −6 N, +3 P (first try wrong: N), 0 → 0, −1.5 N
        await at(3)
        for x in ['n', 'n', '0', 'n']: await k.press(x)
        await k.press('Enter'); print('q1 wrong:', await fb())
        await k.press('ArrowUp'); await k.press('ArrowUp'); await k.press('p'); await k.press('Enter'); print('q1 right:', await fb())
        # q2: −3 is the 2nd of [-4,-3,3,4]; first try 3 (wrong), then −3; then 5 = 3rd of [-6,-5,5,6]
        await at(6)
        for x in ['ArrowRight'] * 3: await k.press(x)
        await k.press('Enter'); print('q2a wrong:', await fb())
        await k.press('ArrowLeft'); await k.press('Enter'); print('q2a right:', await fb())
        await nxt()
        for x in ['ArrowRight'] * 3: await k.press(x)
        await k.press('Enter'); print('q2b:', await fb())
        # q3: −3 (2nd), then −7 (1st of 2)
        await at(10)
        await k.press('ArrowRight'); await k.press('ArrowRight'); await k.press('Enter'); print('q3a:', await fb())
        await nxt()
        await k.press('ArrowRight'); await k.press('Enter'); print('q3b:', await fb())
        # final1: typed with a + and a comma-free plain answer
        await at(12); await pg.wait_for_timeout(200)
        for v in ['−250', '+900', '-6', '-12', '+340']: await k.type(v); await k.press('Tab')
        await k.press('Escape'); await k.press('Enter'); print('final1:', await fb())
        # final2: one wrong row first
        await at(13); await pg.wait_for_timeout(200)
        for v in ['-9', '100', '-58', '-35', '0']: await k.type(v); await k.press('Tab')
        await k.press('Escape'); await k.press('Enter'); print('final2 wrong:', await fb())
        await k.press('s'); print('final2 shown:', await fb())
        # final3: T F T T F
        await at(14)
        for x in 'tftt': await k.press(x)
        await k.press('f'); await k.press('Enter'); print('final3:', await fb())
        await at(15); print('finish:', (await pg.locator('#ui').inner_text()).replace('\n', ' | ')[:200])
        print('errors:', errs or 'none'); await b.close()
asyncio.run(main())
