from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, math

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/'04_UI'/'APP'; CONTACT=ROOT/'04_UI'/'CONTACTS'; CONTACT.mkdir(parents=True,exist_ok=True)
MIN=ROOT/'06_MINERS'/'PNG_V130'; ICON=ROOT/'07_GAME_ASSETS'/'v130'/'icons'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'

def font(sz,bold=False): return ImageFont.truetype(BOLD if bold else FONT,sz)

def rr(draw,box,r,fill,outline=None,width=1): draw.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)

# Miner contact
mw,mh=1500,1530
mcanvas=Image.new('RGB',(mw,mh),'#040817'); d=ImageDraw.Draw(mcanvas)
d.text((55,34),'星矿纪元 · 36级矿机 V1.3.0',font=font(44,True),fill='#F4F7FF')
d.text((56,92),'六个科技阶段 / 独立轮廓 / 透明PNG与SVG / 等比缩放',font=font(22),fill='#9EACC9')
for i in range(36):
    r=i//6;c=i%6;x=42+c*242;y=145+r*222
    rr(d,(x,y,x+220,y+198),24,'#0B1733','#28456F',3)
    im=Image.open(MIN/f'MINER_L{i+1:02d}.png').convert('RGBA');im.thumbnail((170,170),Image.Resampling.LANCZOS)
    mcanvas.paste(im,(x+(220-im.width)//2,y+5),im)
    d.text((x+110,y+169),f'Lv.{i+1:02d}',font=font(22,True),anchor='mm',fill='#F6BD48')
mcanvas.save(CONTACT/'MINER_36_CONTACT_V130.png')

# Icon contact
icons=sorted([p for p in ICON.glob('icon_*.png')])
ic=Image.new('RGB',(1500,900),'#040817');di=ImageDraw.Draw(ic)
di.text((55,34),'星矿纪元 · 游戏图标资源 V1.3.0',font=font(44,True),fill='#F4F7FF')
for i,p in enumerate(icons):
    r=i//9;c=i%9;x=45+c*160;y=115+r*185
    rr(di,(x,y,x+140,y+150),22,'#0B1733','#28456F',2)
    im=Image.open(p).convert('RGBA');im.thumbnail((82,82),Image.Resampling.LANCZOS)
    ic.paste(im,(x+(140-im.width)//2,y+12),im)
    label=p.stem.replace('icon_','')
    di.text((x+70,y+122),label,font=font(14),anchor='mm',fill='#BFCBE1')
ic.save(CONTACT/'ICON_CONTACT_V130.png')

# All UI sheets, 12 per sheet
idx=json.loads((ROOT/'10_HTML'/'RENDER_INDEX_V130_APP.json').read_text(encoding='utf-8'))
for sheet,chunk_start in enumerate(range(0,len(idx),12),1):
    chunk=idx[chunk_start:chunk_start+12]
    canvas=Image.new('RGB',(1800,2200),'#030611');dd=ImageDraw.Draw(canvas)
    dd.text((55,28),f'星矿纪元 V1.3.0 · Android 页面状态总览 {sheet:02d}',font=font(40,True),fill='#F4F7FF')
    dd.text((56,82),f'Chromium真实渲染 · 1080×2280基线 · 第 {chunk_start+1}–{chunk_start+len(chunk)} 张',font=font(20),fill='#9EACC9')
    for i,e in enumerate(chunk):
        r=i//4;c=i%4;x=35+c*440;y=125+r*680
        rr(dd,(x,y,x+410,y+640),24,'#081126','#28456F',2)
        p=UI/f"{e['page_id']}__{e['state']}.png"
        im=Image.open(p).convert('RGB'); im.thumbnail((300,633),Image.Resampling.LANCZOS)
        canvas.paste(im,(x+(410-im.width)//2,y+8))
        dd.text((x+205,y+614),f"{e['page_id']} / {e['state']}",font=font(14),anchor='mm',fill='#D9E3F4')
    canvas.save(CONTACT/f'APP_CONTACT_{sheet:02d}_V130.png')

# Core overview 3840x2160
core=[
('APP-GAME-002__DEFAULT','矿场首页'),('APP-GAME-002__CLAIMABLE','收益可领'),('APP-GAME-008__DEFAULT','合成升级'),
('APP-GAME-003__DEFAULT','矿机商店'),('APP-PROJ-001__DEFAULT','项目首页'),('APP-PROJ-006__TASK_RUNNING','项目任务'),
('APP-MALL-001__DEFAULT','商城'),('APP-MARKET-001__DEFAULT','积分集市'),('APP-ME-001__DEFAULT','个人中心'),
('APP-INVITE-001__DEFAULT','邀请好友'),('APP-MEMBER-001__DEFAULT','会员中心'),('APP-WD-001__DEFAULT','提现中心'),
('APP-ID-002__DEFAULT','实名认证'),('APP-PAY-001__DEFAULT','原生收银台')]
board=Image.new('RGB',(3840,2160),'#02050E');db=ImageDraw.Draw(board)
# subtle grid/background
for x in range(0,3840,120): db.line((x,0,x,2160),fill='#071126',width=1)
for y in range(0,2160,120): db.line((0,y,3840,y),fill='#071126',width=1)
# title panel
rr(db,(40,40,730,780),34,'#081126','#28456F',3)
db.text((90,90),'星矿纪元',font=font(82,True),fill='#F4F7FF')
db.text((94,188),'STAR MINE ERA',font=font(28,True),fill='#F6BD48')
db.text((92,255),'V1.3.0 游戏视觉重建版',font=font(34,True),fill='#31C9E7')
notes=['深海军蓝 + 金橙收益色','矿场场景与4×4合成棋盘','36级原创矿机资产','项目、商城、集市完整游戏皮肤','支付、实名、提现保持安全与可读性','Chromium基线 1080×2280']
y=345
for n in notes:
    db.ellipse((92,y+8,108,y+24),fill='#F6BD48');db.text((128,y),n,font=font(24),fill='#D9E3F4');y+=58
# phones top: 9, 250x528
for i,(key,label) in enumerate(core[:9]):
    x=770+i*335;y=45
    p=UI/f'{key}.png'; im=Image.open(p).convert('RGB'); im.thumbnail((250,528),Image.Resampling.LANCZOS)
    rr(db,(x-10,y-8,x+260,y+580),26,'#071126','#28456F',2)
    board.paste(im,(x,y))
    db.text((x+125,y+548),label,font=font(20,True),anchor='mm',fill='#F4F7FF')
# phones second row 5
for i,(key,label) in enumerate(core[9:]):
    x=55+i*335;y=850
    p=UI/f'{key}.png';im=Image.open(p).convert('RGB');im.thumbnail((250,528),Image.Resampling.LANCZOS)
    rr(db,(x-10,y-8,x+260,y+580),26,'#071126','#28456F',2);board.paste(im,(x,y));db.text((x+125,y+548),label,font=font(20,True),anchor='mm',fill='#F4F7FF')
# miners lower right
mc=Image.open(CONTACT/'MINER_36_CONTACT_V130.png').convert('RGB');mc.thumbnail((1830,930),Image.Resampling.LANCZOS)
rr(db,(1950,835,3800,1810),30,'#071126','#28456F',2);board.paste(mc,(1960,850))
# palette and validation bar
rr(db,(45,1510,1870,2070),30,'#071126','#28456F',2)
db.text((85,1550),'视觉与开发约束',font=font(38,True),fill='#F4F7FF')
constraints=['一级Tab根页无返回按钮','按钮固定42dp，禁止位图拉伸','矿机ContentScale.Fit','滚动内容避开底部导航','状态图必须真实差异','系统状态栏由Android管理']
for i,t in enumerate(constraints):
    x=85+(i%2)*850;y=1625+(i//2)*105
    rr(db,(x,y,x+760,y+74),16,'#0B1733','#28456F',2);db.text((x+28,y+21),'✓ '+t,font=font(23),fill='#D9E3F4')
# palette
colors=[('#040817','深空底色'),('#0B1733','面板'),('#F6BD48','收益金'),('#EF862D','主操作橙'),('#4267E8','功能蓝'),('#7648DE','能源紫'),('#31C9E7','科技青'),('#E95367','警示红')]
for i,(c,n) in enumerate(colors):
    x=1985+i*220;y=1880
    rr(db,(x,y,x+190,y+125),20,c,'#fff',2);db.text((x+95,y+150),n,font=font(18),anchor='mm',fill='#D9E3F4')
board.save(CONTACT/'星矿纪元_V1.3.0_核心UI总览.png')
print('contacts generated')
