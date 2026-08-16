from pathlib import Path
import json, asyncio, re, base64, mimetypes
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
INDEX=json.loads((ROOT/'10_HTML'/'RENDER_INDEX_V130_APP.json').read_text(encoding='utf-8'))
OUT=ROOT/'04_UI'/'APP';OUT.mkdir(parents=True,exist_ok=True)
CSS_PATH=ROOT/'10_HTML'/'shared'/'styles_v130.css'


def data_uri(path:Path)->str:
    data=path.read_bytes()
    mime=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return f'data:{mime};base64,'+base64.b64encode(data).decode('ascii')

def inline_css(css:str, base:Path)->str:
    pat=re.compile(r'url\(([^)]+)\)')
    def repl(m):
        raw=m.group(1).strip().strip('"\'')
        if raw.startswith(('data:','http:','https:','#')): return m.group(0)
        p=(base/raw).resolve()
        if p.exists(): return f'url("{data_uri(p)}")'
        return m.group(0)
    return pat.sub(repl,css)

def bundle_html(path:Path)->str:
    text=path.read_text(encoding='utf-8')
    css=inline_css(CSS_PATH.read_text(encoding='utf-8'),CSS_PATH.parent)
    text=re.sub(r'<link\s+rel="stylesheet"\s+href="\.\./shared/styles_v130\.css">',f'<style>{css}</style>',text)
    pat=re.compile(r'src="([^"]+)"')
    def repl(m):
        raw=m.group(1)
        if raw.startswith(('data:','http:','https:')): return m.group(0)
        p=(path.parent/raw).resolve()
        if p.exists(): return f'src="{data_uri(p)}"'
        return m.group(0)
    return pat.sub(repl,text)

async def main(selected=None):
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage','--font-render-hinting=none','--disable-background-networking'])
        context=await browser.new_context(viewport={'width':360,'height':760},device_scale_factor=3,locale='zh-CN')
        page=await context.new_page()
        entries=INDEX if not selected else [x for x in INDEX if f"{x['page_id']}__{x['state']}" in selected]
        for i,e in enumerate(entries,1):
            path=ROOT/e['html']
            await page.set_content(bundle_html(path),wait_until='load')
            await page.wait_for_function("Array.from(document.images).every(i => i.complete)")
            await page.wait_for_timeout(100)
            out=OUT/f"{e['page_id']}__{e['state']}.png"
            await page.screenshot(path=str(out),full_page=False,animations='disabled')
            if i%20==0 or i==len(entries): print(i,'/',len(entries))
        await browser.close()

if __name__=='__main__':
    import sys
    sel=set(sys.argv[1:]) if len(sys.argv)>1 else None
    asyncio.run(main(sel))
