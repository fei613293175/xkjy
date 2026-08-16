from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'05_BRAND'; OUT.mkdir(parents=True,exist_ok=True)
MIN=ROOT/'06_MINERS'/'PNG_V130'
BG=ROOT/'07_GAME_ASSETS'/'v130'/'backgrounds'
QR=ROOT/'07_GAME_ASSETS'/'v120'/'objects'/'invite_qr_2026.png'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
SERIF='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'

def f(sz,serif=False): return ImageFont.truetype(SERIF if serif else FONT,sz)

def text_gradient(size,text,font,top,bottom,stroke=0,stroke_fill='#2A1742'):
    mask=Image.new('L',size,0); d=ImageDraw.Draw(mask); box=d.textbbox((0,0),text,font=font,stroke_width=stroke)
    x=(size[0]-(box[2]-box[0]))//2; y=(size[1]-(box[3]-box[1]))//2-box[1]
    d.text((x,y),text,font=font,fill=255,stroke_width=stroke,stroke_fill=255)
    arr=np.zeros((size[1],size[0],4),dtype=np.uint8)
    c1=tuple(int(top[i:i+2],16) for i in (1,3,5)); c2=tuple(int(bottom[i:i+2],16) for i in (1,3,5))
    for yy in range(size[1]):
        t=yy/max(1,size[1]-1); c=tuple(int(c1[j]*(1-t)+c2[j]*t) for j in range(3)); arr[yy,:,0:3]=c; arr[yy,:,3]=255
    grad=Image.fromarray(arr,'RGBA'); grad.putalpha(mask)
    # separate darker stroke layer
    if stroke:
        sm=Image.new('L',size,0);sd=ImageDraw.Draw(sm);sd.text((x,y),text,font=font,fill=0,stroke_width=stroke,stroke_fill=255)
        st=Image.new('RGBA',size,stroke_fill); st.putalpha(sm); st.alpha_composite(grad)
        return st
    return grad

def contain(im,size):
    im=im.copy();im.thumbnail(size,Image.Resampling.LANCZOS);return im

def cosmic_canvas(size):
    # crop business background and enrich
    bg=Image.open(BG/'bg_business_space.png').convert('RGB').resize(size,Image.Resampling.LANCZOS)
    return bg

# logo transparent
logo=Image.new('RGBA',(1600,520),(0,0,0,0))
d=ImageDraw.Draw(logo)
# deep shadow and warm gold face, deliberately compact and legible
d.text((800,188),'星矿纪元',font=f(210,True),anchor='mm',fill='#24162A',stroke_width=22,stroke_fill='#080B18')
d.text((800,174),'星矿纪元',font=f(210,True),anchor='mm',fill='#FFD66A',stroke_width=11,stroke_fill='#7A3416')
d.text((800,365),'STAR MINE ERA',font=f(44),anchor='mm',fill='#F4F7FF',stroke_width=2,stroke_fill='#071126')
d.line((500,420,1100,420),fill='#31C9E7',width=5)
logo.save(OUT/'logo_wordmark_v130.png')

# App icon
icon=cosmic_canvas((1024,1024)).convert('RGBA')
# dark overlay
ov=Image.new('RGBA',icon.size,(3,7,20,70));icon.alpha_composite(ov)
miner=contain(Image.open(MIN/'MINER_L30.png').convert('RGBA'),(780,780))
# glow
alpha=miner.getchannel('A'); glow=alpha.filter(ImageFilter.GaussianBlur(28));g=Image.new('RGBA',miner.size,(86,85,255,0));g.putalpha(glow.point(lambda p:int(p*.65)))
x=(1024-miner.width)//2;y=160
icon.alpha_composite(g,(x,y));icon.alpha_composite(miner,(x,y))
# bottom crystals
D=ImageDraw.Draw(icon)
for x,c in [(90,'#43D4EF'),(850,'#7C4CE5')]:
    D.polygon([(x,930),(x+58,740),(x+116,930),(x+62,1000)],fill=c,outline='#C9FFFF')
# small logo label
D.rounded_rectangle((190,820,834,963),radius=48,fill=(4,10,30,210),outline='#2E628F',width=5)
D.text((512,890),'星矿纪元',font=f(92,True),anchor='mm',fill='#FFD66A',stroke_width=7,stroke_fill='#5B2815')
icon.save(OUT/'app_icon_1024_v130.png')
# adaptive foreground with transparent outside subject
fg=Image.new('RGBA',(1024,1024),(0,0,0,0));m=contain(Image.open(MIN/'MINER_L30.png').convert('RGBA'),(720,720));fg.alpha_composite(m,((1024-m.width)//2,(1024-m.height)//2));fg.save(OUT/'app_icon_foreground_1024_v130.png')

# Splash 1080x2400
sp=cosmic_canvas((1080,2400)).convert('RGBA')
# add dark gradient bottom
arr=np.zeros((2400,1080,4),dtype=np.uint8)
for y in range(2400):
    a=int(20+130*(y/2399));arr[y,:,0:3]=(2,5,15);arr[y,:,3]=a
sp.alpha_composite(Image.fromarray(arr,'RGBA'))
lg=contain(logo,(900,340));sp.alpha_composite(lg,((1080-lg.width)//2,240))
miner=contain(Image.open(MIN/'MINER_L36.png').convert('RGBA'),(760,760));x=(1080-miner.width)//2;y=680
alpha=miner.getchannel('A').filter(ImageFilter.GaussianBlur(38));gl=Image.new('RGBA',miner.size,(112,78,238,0));gl.putalpha(alpha.point(lambda p:int(p*.65)));sp.alpha_composite(gl,(x,y));sp.alpha_composite(miner,(x,y))
D=ImageDraw.Draw(sp)
D.text((540,1510),'合成矿机 · 放置产出 · 星际推广',font=f(44),anchor='mm',fill='#DCE6F7')
D.rounded_rectangle((175,1770,905,1874),radius=52,fill=(7,17,38,210),outline='#28456F',width=4)
D.rounded_rectangle((195,1790,810,1854),radius=32,fill='#17234A')
D.rounded_rectangle((195,1790,730,1854),radius=32,fill='#F6BD48')
D.text((540,1940),'正在启动星际矿场  82%',font=f(32),anchor='mm',fill='#9EACC9')
D.text((540,2240),'STAR MINE ERA  ·  V1.3.0',font=f(26),anchor='mm',fill='#7183A7')
sp.save(OUT/'android_splash_1080x2400_v130.png')

# Brand banner
bn=cosmic_canvas((1600,900)).convert('RGBA');bn.alpha_composite(Image.new('RGBA',bn.size,(2,5,15,70)))
lg=contain(logo,(770,260));bn.alpha_composite(lg,(70,90))
miner=contain(Image.open(MIN/'MINER_L36.png').convert('RGBA'),(700,700));bn.alpha_composite(miner,(850,80))
D=ImageDraw.Draw(bn)
D.text((105,405),'科幻矿业 · 放置合成 · 策略经营',font=f(38),fill='#31C9E7')
features=['36级原创矿机','双积分与虚拟商城','项目推广与浏览任务','会员、邀请与账户体系']
y=500
for t in features:
    D.ellipse((110,y+8,128,y+26),fill='#F6BD48');D.text((150,y),t,font=f(30),fill='#F4F7FF');y+=72
bn.save(OUT/'brand_banner_1600x900_v130.png')

# Invite poster
poster=cosmic_canvas((1080,1920)).convert('RGBA');poster.alpha_composite(Image.new('RGBA',poster.size,(2,5,15,60)))
lg=contain(logo,(800,270));poster.alpha_composite(lg,((1080-lg.width)//2,100))
D=ImageDraw.Draw(poster)
D.text((540,400),'邀请好友，一起开矿',font=f(54),anchor='mm',fill='#F4F7FF')
miner=contain(Image.open(MIN/'MINER_L10.png').convert('RGBA'),(460,460));poster.alpha_composite(miner,((1080-miner.width)//2,470))
D.rounded_rectangle((150,910,930,1590),radius=48,fill=(10,23,51,235),outline='#315A8F',width=5)
D.text((540,985),'我的邀请码 / UID',font=f(34),anchor='mm',fill='#9EACC9')
D.text((540,1080),'2026',font=f(110),anchor='mm',fill='#F6BD48')
qr=contain(Image.open(QR).convert('RGBA'),(330,330));poster.alpha_composite(qr,((1080-qr.width)//2,1160))
D.text((540,1540),'扫码注册 · 邀请码自动填写',font=f(28),anchor='mm',fill='#DCE6F7')
D.rounded_rectangle((220,1660,860,1765),radius=52,fill='#F6BD48',outline='#FFF1A5',width=4)
D.text((540,1712),'保存海报并分享',font=f(36),anchor='mm',fill='#452300')
poster.save(OUT/'invite_poster_1080x1920_v130.png')

manifest='''version: 1.3.0\nassets:\n  logo: logo_wordmark_v130.png\n  app_icon: app_icon_1024_v130.png\n  adaptive_foreground: app_icon_foreground_1024_v130.png\n  splash: android_splash_1080x2400_v130.png\n  brand_banner: brand_banner_1600x900_v130.png\n  invite_poster: invite_poster_1080x1920_v130.png\n'''
(OUT/'BRAND_ASSET_MANIFEST_V130.yaml').write_text(manifest,encoding='utf-8')
print('brand assets generated')
