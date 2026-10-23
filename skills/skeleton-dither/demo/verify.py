import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':1200,'height':820})
        errs=[]
        pg.on('console', lambda m: errs.append(m.text) if m.type in ('error','warning') else None)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8811/demo/index.html')
        await pg.wait_for_timeout(500); await pg.screenshot(path='../shots/demo-1-skeleton.png')
        await pg.wait_for_function("window.__sd.last==='profile'")
        await pg.wait_for_timeout(260); await pg.screenshot(path='../shots/demo-2-decoding.png')
        await pg.wait_for_function("window.__sd.phase==='done'", timeout=10000)
        await pg.wait_for_timeout(200); await pg.screenshot(path='../shots/demo-3-done.png')
        # dither preset mid-reveal
        await pg.click('#preset button[data-v=dither]')
        await pg.wait_for_function("window.__sd.phase==='reveal'")
        await pg.wait_for_timeout(250); await pg.screenshot(path='../shots/demo-4-dither-preset.png')
        await pg.wait_for_function("window.__sd.phase==='done'", timeout=10000)
        left = await pg.evaluate("document.querySelectorAll('[data-sd-t],[data-sd-m],[data-sd-f],.sd-overlay').length")
        # reduced motion
        ctx = await b.new_context(reduced_motion='reduce'); rp = await ctx.new_page()
        rp.on('pageerror', lambda e: errs.append('RM '+str(e)))
        await rp.goto('http://localhost:8811/demo/index.html')
        await rp.wait_for_function("window.__sd.phase==='done'", timeout=10000)
        print('errors:', errs, 'leftover:', left)
        await b.close()
asyncio.run(main())
