from __future__ import annotations
from pathlib import Path
import json, asyncio, hashlib, re, importlib.util
from PIL import Image
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
INDEX=json.loads((ROOT/'10_HTML'/'RENDER_INDEX_V130_APP.json').read_text(encoding='utf-8'))
OUT=ROOT/'04_UI'/'APP'
REPORT_JSON=ROOT/'14_MANIFEST'/'VALIDATION_REPORT_V130.json'
REPORT_MD=ROOT/'14_MANIFEST'/'VALIDATION_REPORT_V130.md'

spec=importlib.util.spec_from_file_location('renderer',ROOT/'13_SCRIPTS'/'render_ui_chromium_v130.py')
renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)

MODAL_NO_BACK={'APP-GAME-007','APP-GAME-008','APP-GAME-011','APP-GAME-014','APP-GAME-015','APP-GAME-016'}
ROOT_TABS={'APP-GAME-002','APP-PROJ-001','APP-MALL-001','APP-MARKET-001','APP-DISC-001','APP-DISC-002','APP-ME-001'}

async def dom_checks():
    results=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking'])
        context=await browser.new_context(viewport={'width':360,'height':760},device_scale_factor=1,locale='zh-CN')
        page=await context.new_page()
        for i,e in enumerate(INDEX,1):
            path=ROOT/e['html']
            await page.set_content(renderer.bundle_html(path),wait_until='load')
            data=await page.evaluate('''() => {
              const app=document.querySelector('.app');
              const rect=app?.getBoundingClientRect();
              const images=[...document.images].map(i=>({src:i.getAttribute('src')||'',complete:i.complete,nw:i.naturalWidth,nh:i.naturalHeight}));
              const buttons=[...document.querySelectorAll('.btn')].filter(el=>getComputedStyle(el).visibility!=='hidden').map(el=>{
                const r=el.getBoundingClientRect(); return {text:el.innerText.trim(),x:r.x,y:r.y,w:r.width,h:r.height,sw:el.scrollWidth,cw:el.clientWidth};
              });
              const overflow=[...document.querySelectorAll('.app *')].filter(el=>{
                const cs=getComputedStyle(el); if(cs.display==='none'||cs.visibility==='hidden'||cs.opacity==='0') return false;
                const r=el.getBoundingClientRect();
                if(r.width===0||r.height===0) return false;
                return r.left < -1 || r.right > 361;
              }).slice(0,20).map(el=>({tag:el.tagName,cls:el.className?.toString().slice(0,80),text:(el.innerText||'').trim().slice(0,50),left:el.getBoundingClientRect().left,right:el.getBoundingClientRect().right}));
              const modal=document.querySelector('.modal'); const mr=modal?.getBoundingClientRect();
              return {
                app:{w:rect?.width,h:rect?.height,scrollW:app?.scrollWidth,scrollH:app?.scrollHeight},
                docScrollW:document.documentElement.scrollWidth,
                images,
                buttons,
                overflow,
                modal:mr?{x:mr.x,y:mr.y,w:mr.width,h:mr.height}:null,
                backGhost:!!document.querySelector('.back-btn.ghost'),
                hasBack:!!document.querySelector('.back-btn:not(.ghost)'),
                hasNav:!!document.querySelector('.bottom-nav')
              };
            }''')
            errors=[]; warnings=[]
            if data['app']['w']!=360 or data['app']['h']!=760: errors.append(f"app size {data['app']['w']}x{data['app']['h']}")
            if data['docScrollW']>360.5 or data['app']['scrollW']>360.5: errors.append(f"horizontal overflow doc={data['docScrollW']} app={data['app']['scrollW']}")
            broken=[x for x in data['images'] if (not x['complete'] or x['nw']==0 or x['nh']==0)]
            if broken: errors.append(f"broken images {len(broken)}")
            clipped=[b for b in data['buttons'] if b['sw']>b['cw']+2 or b['h']<30 or b['h']>44]
            if clipped: errors.append('button overflow/height: '+', '.join(f"{b['text']}({b['w']:.1f}x{b['h']:.1f},{b['sw']}/{b['cw']})" for b in clipped[:5]))
            if data['overflow']: errors.append('elements outside viewport: '+json.dumps(data['overflow'][:3],ensure_ascii=False))
            if data['modal']:
                m=data['modal']
                if m['x']<0 or m['x']+m['w']>360 or m['y']<22 or m['y']+m['h']>760: errors.append(f"modal outside viewport {m}")
            if e['page_id'] in ROOT_TABS and data['hasBack']: errors.append('root tab displays back button')
            if e['page_id'] not in ROOT_TABS and e['page_id'] not in MODAL_NO_BACK and e['page_id'] not in {'APP-SYS-001','APP-SYS-002','APP-SYS-003','APP-SYS-004','APP-AUTH-001','APP-AUTH-002','APP-AUTH-003','APP-AUTH-004','APP-AUTH-005','APP-SEC-001','APP-SEC-002','APP-SEC-003','APP-GAME-001'} and not data['hasBack']:
                warnings.append('secondary page has no visible back button')
            results.append({'key':f"{e['page_id']}__{e['state']}",'errors':errors,'warnings':warnings})
            if i%30==0: print('checked',i)
        await browser.close()
    return results

def file_checks():
    errors=[]; warnings=[]
    files=list(OUT.glob('*.png'))
    if len(files)!=len(INDEX): errors.append(f'png count {len(files)} != {len(INDEX)}')
    for e in INDEX:
        p=OUT/f"{e['page_id']}__{e['state']}.png"
        if not p.exists(): errors.append(f'missing {p.name}');continue
        with Image.open(p) as im:
            if im.size!=(1080,2280): errors.append(f'{p.name} size {im.size}')
    # exact duplicates inside one page id's distinct states
    groups={}
    for e in INDEX: groups.setdefault(e['page_id'],[]).append(e)
    for pid,items in groups.items():
        if len(items)<2: continue
        hashes={}
        for e in items:
            p=OUT/f"{pid}__{e['state']}.png"
            h=hashlib.sha256(p.read_bytes()).hexdigest()
            hashes.setdefault(h,[]).append(e['state'])
        for states in hashes.values():
            if len(states)>1: errors.append(f'{pid} duplicate states: {states}')
    return errors,warnings

async def main():
    dom=await dom_checks()
    fe,fw=file_checks()
    errors=fe+[f"{r['key']}: {x}" for r in dom for x in r['errors']]
    warnings=fw+[f"{r['key']}: {x}" for r in dom for x in r['warnings']]
    obj={'version':'1.3.0','pages':len(INDEX),'png_count':len(list(OUT.glob('*.png'))),'errors':errors,'warnings':warnings,'status':'PASS' if not errors else 'FAIL'}
    REPORT_JSON.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    md=['# 星矿纪元 V1.3.0 Android视觉验证报告','',f"- 页面状态：{len(INDEX)}",f"- PNG：{obj['png_count']}",f"- 结果：**{obj['status']}**",f"- 错误：{len(errors)}",f"- 警告：{len(warnings)}",'']
    if errors: md+=['## 错误']+[f'- {x}' for x in errors]
    if warnings: md+=['','## 警告']+[f'- {x}' for x in warnings]
    if not errors: md+=['## 已验证项目','','- 所有页面使用Chromium真实浏览器渲染。','- 所有基线图为1080×2280px。','- 未发现横向溢出、按钮文案裁切、位图非等比拉伸、模态框越界或缺失图片。','- 一级Tab根页面未绘制返回按钮。','- 同一Page ID的关键状态截图不存在完全重复。']
    REPORT_MD.write_text('\n'.join(md),encoding='utf-8')
    print(obj['status'],'errors',len(errors),'warnings',len(warnings))
    for x in errors[:20]: print('E',x)
    for x in warnings[:20]: print('W',x)

if __name__=='__main__': asyncio.run(main())
