from __future__ import annotations
import json, math, random, shutil, subprocess, wave
from pathlib import Path
from typing import Iterable
import yaml
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import soundfile as sf

ROOT=Path('/mnt/data/xkjy_v110_work/XKJY_V110')
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'

def ensure(p:Path): p.mkdir(parents=True,exist_ok=True)
def write_yaml(p:Path,obj): ensure(p.parent); p.write_text(yaml.safe_dump(obj,allow_unicode=True,sort_keys=False,width=140),encoding='utf-8')
def write_json(p:Path,obj): ensure(p.parent); p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def font(sz,b=False): return ImageFont.truetype(FONT_B if b else FONT,sz)

def radial_glow(size:int,color,alpha=180,radius=.46):
    y,x=np.ogrid[:size,:size]; c=(size-1)/2
    d=np.sqrt((x-c)**2+(y-c)**2)/(size*radius)
    a=np.clip(1-d,0,1)**2*alpha
    arr=np.zeros((size,size,4),dtype=np.uint8)
    arr[...,0]=color[0];arr[...,1]=color[1];arr[...,2]=color[2];arr[...,3]=a.astype(np.uint8)
    return Image.fromarray(arr,'RGBA')

def paste_center(canvas:Image.Image, obj:Image.Image, scale:float, dx=0,dy=0,angle=0):
    w=max(1,int(obj.width*scale)); h=max(1,int(obj.height*scale))
    o=obj.resize((w,h),Image.Resampling.LANCZOS)
    if angle: o=o.rotate(angle,Image.Resampling.BICUBIC,expand=False)
    canvas.alpha_composite(o,((canvas.width-w)//2+dx,(canvas.height-h)//2+dy))

def generate_miner_vfx():
    idle_dir=ROOT/'08_VFX/miner_idle'; work_dir=ROOT/'08_VFX/miner_work'; ensure(idle_dir);ensure(work_dir)
    manifest=[]
    rng=random.Random(20260816)
    for level in range(1,37):
        src=Image.open(ROOT/f'06_MINERS/PNG/MINER_L{level:02d}.png').convert('RGBA')
        # idle 4 frames
        idle_frames=[]
        for i,(sc,dy,ang) in enumerate([(0.965,4,-.8),(0.985,0,0),(1.0,-3,.7),(0.982,0,0)]):
            fr=Image.new('RGBA',(512,512),(0,0,0,0))
            glow=radial_glow(512,(39,213,196) if level<19 else (255,200,74),70+level*2,.50)
            fr.alpha_composite(glow)
            paste_center(fr,src,sc,0,dy,ang)
            d=ImageDraw.Draw(fr,'RGBA')
            for k in range(5):
                a=2*math.pi*(k/5+i*.08); r=150+8*math.sin(i+k)
                x=256+math.cos(a)*r; y=260+math.sin(a)*r*.35
                d.ellipse((x-2,y-2,x+2,y+2),fill=(138,240,229,120))
            idle_frames.append(fr)
        sheet=Image.new('RGBA',(512*4,512),(0,0,0,0))
        for i,fr in enumerate(idle_frames): sheet.alpha_composite(fr,(512*i,0))
        idle_path=idle_dir/f'MINER_L{level:02d}_IDLE.png';
        if not idle_path.exists(): sheet.save(idle_path,compress_level=3)
        # work 6 frames
        work_frames=[]
        for i in range(6):
            fr=Image.new('RGBA',(512,512),(0,0,0,0))
            pulse=(math.sin(i/6*2*math.pi)+1)/2
            fr.alpha_composite(radial_glow(512,(255,122,61),90+int(90*pulse),.53))
            paste_center(fr,src,0.975+0.015*pulse, int(3*math.sin(i)), int(2*math.cos(i)), math.sin(i)*.7)
            d=ImageDraw.Draw(fr,'RGBA')
            # drill/work sparks at right front
            base_x=400; base_y=275
            for k in range(8):
                rr=random.Random(level*1000+i*40+k)
                x=base_x+rr.randint(-10,70); y=base_y+rr.randint(-55,55)
                length=rr.randint(8,25)
                d.line((x,y,x+length,y-rr.randint(3,14)),fill=(255,200,74,190),width=3)
                d.ellipse((x-2,y-2,x+2,y+2),fill=(255,246,190,230))
            # scan arc
            bbox=(110-i*2,92-i*2,410+i*2,390+i*2)
            d.arc(bbox,195+i*12,295+i*12,fill=(39,213,196,130),width=4)
            work_frames.append(fr)
        sheet2=Image.new('RGBA',(512*6,512),(0,0,0,0))
        for i,fr in enumerate(work_frames): sheet2.alpha_composite(fr,(512*i,0))
        work_path=work_dir/f'MINER_L{level:02d}_WORK.png';
        if not work_path.exists(): sheet2.save(work_path,compress_level=3)
        manifest.append({'miner_id':f'MINER_L{level:02d}','idle':str(idle_path.relative_to(ROOT)),'idle_frames':4,'idle_fps':6,'work':str(work_path.relative_to(ROOT)),'work_frames':6,'work_fps':10,'frame_size':[512,512]})
    write_yaml(ROOT/'08_VFX/MINER_ANIMATION_MANIFEST.yaml',{'project':'星矿纪元','version':'1.1.0','items':manifest})

def draw_star(d,cx,cy,r1,r2,n=8,fill=(255,200,74,255)):
    pts=[]
    for i in range(n*2):
        a=-math.pi/2+i*math.pi/n; r=r1 if i%2==0 else r2
        pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
    d.polygon(pts,fill=fill)

def effect_frames(effect_id:str,frames=8,size=256):
    out=[]; rng=random.Random(effect_id)
    palette={
        'MERGE_COMMON':((255,200,74),(255,122,61)), 'MERGE_ADVANCED':((39,213,196),(58,140,255)),
        'MERGE_EPIC':((139,92,255),(237,92,190)), 'POINT_BUBBLE':((255,226,154),(255,122,61)),
        'POINT_CLAIM':((255,200,74),(255,249,210)), 'BOX_OPEN':((255,200,74),(255,122,61)),
        'TASK_COMPLETE':((39,213,196),(36,184,120)), 'SLOT_UNLOCK':((58,140,255),(39,213,196)),
        'LEVEL_UNLOCK':((255,200,74),(139,92,255)), 'MEMBER_BADGE':((139,92,255),(237,92,190)),
        'PROMOTION_HEADLINE':((255,122,61),(255,200,74)), 'PROMOTION_PIN':((139,92,255),(58,140,255)),
        'PROMOTION_REFRESH':((39,213,196),(36,184,120)), 'ORDER_SUCCESS':((36,184,120),(39,213,196)),
        'ORDER_FAILED':((229,84,84),(255,122,61)), 'IDENTITY_SUCCESS':((58,140,255),(39,213,196)),
    }
    c1,c2=palette[effect_id]
    for i in range(frames):
        t=i/(frames-1); fr=Image.new('RGBA',(size,size),(0,0,0,0)); d=ImageDraw.Draw(fr,'RGBA')
        # radial rings and particles
        r=20+95*t
        d.ellipse((128-r,128-r,128+r,128+r),outline=(*c1,int(230*(1-t))),width=max(2,int(8*(1-t))))
        r2=max(5,80*t)
        d.ellipse((128-r2,128-r2,128+r2,128+r2),outline=(*c2,int(180*(1-t))),width=4)
        for k in range(14):
            a=2*math.pi*k/14 + t*.8; rr=25+100*t+rng.randint(-8,8)
            x=128+math.cos(a)*rr; y=128+math.sin(a)*rr
            s=max(1,int(5*(1-t)+1))
            d.ellipse((x-s,y-s,x+s,y+s),fill=(*c2,int(220*(1-t))))
        # central semantic glyph
        if effect_id in ('TASK_COMPLETE','ORDER_SUCCESS','IDENTITY_SUCCESS'):
            d.line((88,130,116,157,170,94),fill=(255,255,255,int(255*(1-abs(t-.45)))),width=12)
        elif effect_id=='ORDER_FAILED':
            d.line((92,92,164,164),fill=(255,255,255,230),width=11);d.line((164,92,92,164),fill=(255,255,255,230),width=11)
        elif effect_id=='SLOT_UNLOCK':
            d.rounded_rectangle((91,116,165,182),14,fill=(*c1,230));d.arc((105,72,158,132),185,345,fill=(255,255,255,230),width=10)
        elif effect_id=='BOX_OPEN':
            d.rounded_rectangle((78,118,178,180),12,fill=(*c1,230)); d.polygon([(72,112),(128,83-25*t),(184,112),(172,132),(84,132)],fill=(*c2,230))
        elif effect_id=='MEMBER_BADGE':
            d.polygon([(78,158),(70,98),(104,118),(128,72),(152,118),(186,98),(178,158)],fill=(*c1,235));d.rectangle((78,154,178,175),fill=(*c2,235))
        elif effect_id.startswith('PROMOTION_'):
            label={'PROMOTION_HEADLINE':'H','PROMOTION_PIN':'P','PROMOTION_REFRESH':'R'}[effect_id]
            d.rounded_rectangle((76,86,180,172),24,fill=(*c1,235));d.text((128,128),label,font=font(56,True),anchor='mm',fill='white')
        elif effect_id in ('POINT_BUBBLE','POINT_CLAIM'):
            d.ellipse((82,82,174,174),fill=(*c1,230),outline=(255,248,205,255),width=5);d.text((128,126),'✦',font=font(44,True),anchor='mm',fill=(108,61,0,255))
        else:
            draw_star(d,128,128,45*(.65+min(t,.5)),20,8,fill=(*c1,230))
        out.append(fr)
    return out

def generate_core_vfx():
    outdir=ROOT/'08_VFX/effects';ensure(outdir)
    ids=['MERGE_COMMON','MERGE_ADVANCED','MERGE_EPIC','POINT_BUBBLE','POINT_CLAIM','BOX_OPEN','TASK_COMPLETE','SLOT_UNLOCK','LEVEL_UNLOCK','MEMBER_BADGE','PROMOTION_HEADLINE','PROMOTION_PIN','PROMOTION_REFRESH','ORDER_SUCCESS','ORDER_FAILED','IDENTITY_SUCCESS']
    items=[]
    for eid in ids:
        fs=effect_frames(eid)
        sheet=Image.new('RGBA',(256*len(fs),256),(0,0,0,0))
        for i,f in enumerate(fs):sheet.alpha_composite(f,(256*i,0))
        p=outdir/f'VFX_{eid}.png';sheet.save(p,compress_level=3)
        items.append({'effect_id':f'VFX_{eid}','path':str(p.relative_to(ROOT)),'frames':len(fs),'frame_size':[256,256],'fps':12,'loop':eid in ['POINT_BUBBLE','MEMBER_BADGE','PROMOTION_HEADLINE','PROMOTION_PIN','PROMOTION_REFRESH']})
    write_yaml(ROOT/'08_VFX/VFX_MANIFEST.yaml',{'project':'星矿纪元','version':'1.1.0','sprite_layout':'horizontal','items':items})

# AUDIO ---------------------------------------------------------------
SR=44100

def normalize(x,peak=.88):
    m=np.max(np.abs(x)) if x.size else 1
    return x if m<1e-9 else (x/m*peak).astype(np.float32)

def osc(freq,t,kind='sine',phase=0):
    ph=2*np.pi*freq*t+phase
    if kind=='sine': return np.sin(ph)
    if kind=='triangle': return 2/np.pi*np.arcsin(np.sin(ph))
    if kind=='saw': return 2*((freq*t+phase/(2*np.pi))%1)-1
    if kind=='square': return np.sign(np.sin(ph))
    return np.sin(ph)

def envelope(n,attack=.02,release=.15):
    e=np.ones(n,dtype=np.float32); a=min(n,int(attack*SR)); r=min(n,int(release*SR))
    if a>0:e[:a]=np.linspace(0,1,a)
    if r>0:e[-r:]=np.linspace(1,0,r)
    return e

def add_tone(buf,start,dur,freq,amp=.2,kind='sine',pan=0,attack=.02,release=.12,detune=0):
    s=int(start*SR); n=min(int(dur*SR),len(buf)-s)
    if n<=0:return
    t=np.arange(n)/SR
    sig=osc(freq,t,kind)*.75+osc(freq*2.001+detune,t,'sine')*.18+osc(freq*.5,t,'sine')*.07
    sig*=envelope(n,attack,release)*amp
    l=math.sqrt((1-pan)/2);r=math.sqrt((1+pan)/2)
    buf[s:s+n,0]+=sig*l;buf[s:s+n,1]+=sig*r

def add_noise(buf,start,dur,amp=.05,pan=0,seed=0,decay=True):
    s=int(start*SR);n=min(int(dur*SR),len(buf)-s)
    if n<=0:return
    rng=np.random.default_rng(seed);sig=rng.normal(0,1,n)
    # simple smoothing/high-pass blend
    smooth=np.convolve(sig,np.ones(15)/15,mode='same');sig=sig-smooth*.7
    if decay:sig*=np.linspace(1,0,n)**2
    sig*=amp
    l=math.sqrt((1-pan)/2);r=math.sqrt((1+pan)/2)
    buf[s:s+n,0]+=sig*l;buf[s:s+n,1]+=sig*r

def midi(n): return 440*2**((n-69)/12)

def bgm(name,tempo,root_midi,mode='minor',duration=32,style='main'):
    n=int(duration*SR);buf=np.zeros((n,2),np.float32)
    beat=60/tempo
    if mode=='minor': chords=[[0,3,7],[8,12,15],[5,8,12],[10,14,17]]
    else: chords=[[0,4,7],[7,11,14],[9,12,16],[5,9,12]]
    bar=beat*4
    for bi in range(math.ceil(duration/bar)):
        chord=chords[bi%4];start=bi*bar
        # pads
        for j,iv in enumerate(chord):
            add_tone(buf,start,min(bar+1,duration-start),midi(root_midi+iv-12),.09,'triangle',pan=(-.45+j*.45),attack=.65,release=.8,detune=j*.25)
        # arpeggio
        steps=8 if style!='space' else 4
        for st in range(steps):
            tt=start+st*(bar/steps); note=chord[st%len(chord)]+(12 if st>=len(chord) else 0)
            if tt<duration:add_tone(buf,tt,beat*.55,midi(root_midi+note),.075 if style=='space' else .11,'sine',pan=math.sin(st)*.5,attack=.01,release=.18)
        # bass
        add_tone(buf,start,beat*1.8,midi(root_midi+chord[0]-24),.14,'sine',attack=.04,release=.45)
        # percussion
        if style in ('main','mall','event','project'):
            for b in range(4):
                tt=start+b*beat
                add_tone(buf,tt,.18,58,.17 if b in (0,2) else .11,'sine',attack=.001,release=.16)
                add_noise(buf,tt+(beat/2),.08,.035,seed=bi*10+b)
    # ambient space shimmer and low hum
    t=np.arange(n)/SR
    buf[:,0]+=np.sin(2*np.pi*(55+3*np.sin(2*np.pi*.03*t))*t)*.018
    buf[:,1]+=np.sin(2*np.pi*(55+3*np.sin(2*np.pi*.035*t+.8))*t)*.018
    fade=int(.8*SR);buf[:fade]*=np.linspace(0,1,fade)[:,None];buf[-fade:]*=np.linspace(1,0,fade)[:,None]
    return normalize(buf,.78)

def make_sfx():
    specs={}
    def new(d):return np.zeros((int(d*SR),2),np.float32)
    # UI
    b=new(.16);add_tone(b,0,.12,880,.32,'sine',release=.1);specs['SFX_UI_TAP']=b
    b=new(.24);add_tone(b,0,.18,520,.25,'triangle',release=.16);add_tone(b,.04,.16,390,.18,'sine',release=.14);specs['SFX_UI_BACK']=b
    b=new(.36);add_tone(b,0,.25,300,.28,'triangle',release=.2);add_noise(b,0,.18,.035,seed=1);specs['SFX_MINER_PICK']=b
    b=new(.32);add_tone(b,0,.24,140,.35,'sine',release=.22);add_noise(b,0,.16,.08,seed=2);specs['SFX_MINER_DROP']=b
    b=new(.38);add_tone(b,0,.35,110,.28,'square',release=.25);add_tone(b,0,.35,116,.22,'square',release=.25);specs['SFX_MINER_INVALID']=b
    b=new(.8)
    for i,note in enumerate([60,64,67,72]):add_tone(b,i*.09,.45,midi(note),.22,'triangle',pan=-.3+i*.2,release=.28)
    add_noise(b,.15,.4,.05,seed=3);specs['SFX_MINER_MERGE']=b
    b=new(1.15)
    for i,note in enumerate([60,67,72,76,84]):add_tone(b,i*.1,.65,midi(note),.24,'triangle',pan=-.45+i*.22,release=.4)
    add_noise(b,.12,.65,.07,seed=4);specs['SFX_MINER_MERGE_HIGH']=b
    b=new(.32);add_tone(b,0,.28,1100,.26,'sine',release=.25);add_tone(b,.03,.2,1450,.18,'sine');specs['SFX_POINT_BUBBLE']=b
    b=new(.65)
    for i,note in enumerate([79,83,86]):add_tone(b,i*.08,.35,midi(note),.25,'sine',pan=-.35+i*.35,release=.25)
    specs['SFX_POINT_CLAIM']=b
    b=new(.72);add_tone(b,0,.4,130,.18,'sine');
    for i,note in enumerate([67,71,74]):add_tone(b,.22+i*.08,.35,midi(note),.22,'triangle',release=.2)
    specs['SFX_MINER_PURCHASE']=b
    b=new(1.1);add_noise(b,0,.5,.09,seed=5)
    for i,note in enumerate([55,62,67,74]):add_tone(b,.28+i*.1,.6,midi(note),.2,'triangle',release=.4)
    specs['SFX_BOX_OPEN']=b
    b=new(.85)
    for i,note in enumerate([64,67,72,76]):add_tone(b,i*.1,.45,midi(note),.22,'sine',release=.3)
    specs['SFX_TASK_COMPLETE']=b
    b=new(1.25)
    for i,note in enumerate([48,55,60,64,67,72]):add_tone(b,i*.1,.72,midi(note),.2,'triangle',pan=-.5+i*.2,release=.45)
    specs['SFX_LEVEL_UNLOCK']=b
    b=new(.72);add_tone(b,0,.25,180,.26,'triangle');add_tone(b,.18,.45,740,.24,'sine');add_tone(b,.25,.4,990,.18,'sine');specs['SFX_SLOT_UNLOCK']=b
    b=new(.9)
    for i,note in enumerate([60,64,67,72]):add_tone(b,i*.11,.45,midi(note),.21,'sine',release=.28)
    specs['SFX_ORDER_SUCCESS']=b
    b=new(.65);add_tone(b,0,.55,180,.26,'square',release=.4);add_tone(b,.05,.5,165,.22,'square',release=.38);specs['SFX_ORDER_FAILED']=b
    b=new(.65);add_tone(b,0,.3,880,.23,'sine');add_tone(b,.18,.4,1174,.23,'sine');specs['SFX_NOTIFICATION']=b
    return specs

def generate_audio():
    bgmdir=ROOT/'09_AUDIO/BGM';sfxdir=ROOT/'09_AUDIO/SFX';srcdir=ROOT/'09_AUDIO/SOURCE';ensure(bgmdir);ensure(sfxdir);ensure(srcdir)
    tracks=[('BGM_MINE_MAIN',96,50,'minor','main'),('BGM_MINE_DEEP_SPACE',72,45,'minor','space'),('BGM_PROJECT',100,55,'major','project'),('BGM_MALL',112,57,'major','mall'),('BGM_EVENT',124,52,'major','event')]
    items=[]
    for name,tempo,root,mode,style in tracks:
        audio=bgm(name,tempo,root,mode,32,style)
        path=bgmdir/f'{name}.ogg';sf.write(path,audio,SR,format='OGG',subtype='VORBIS')
        items.append({'audio_id':name,'bus':'BGM','path':str(path.relative_to(ROOT)),'duration_seconds':32,'loop':True,'default_volume':0.55,'fade_in_ms':600,'fade_out_ms':600})
    for name,audio in make_sfx().items():
        audio=normalize(audio,.82);path=sfxdir/f'{name}.ogg';sf.write(path,audio,SR,format='OGG',subtype='VORBIS')
        items.append({'audio_id':name,'bus':'SFX','path':str(path.relative_to(ROOT)),'duration_seconds':round(len(audio)/SR,3),'loop':False,'default_volume':0.78})
    write_yaml(ROOT/'09_AUDIO/AUDIO_MANIFEST.yaml',{'project':'星矿纪元','version':'1.1.0','sample_rate':SR,'original_generation':'本项目专用程序化原创音频，不依赖第三方素材','items':items})
    cue={
      'APP-GAME-002':['BGM_MINE_MAIN','SFX_MINER_PICK','SFX_MINER_DROP','SFX_MINER_MERGE','SFX_POINT_BUBBLE','SFX_POINT_CLAIM'],
      'APP-GAME-008':['SFX_LEVEL_UNLOCK'],'APP-GAME-011':['SFX_BOX_OPEN'],'APP-GAME-009':['SFX_TASK_COMPLETE'],
      'APP-PROJ-001':['BGM_PROJECT'],'APP-MALL-001':['BGM_MALL'],'APP-PAY-003':['SFX_ORDER_SUCCESS','SFX_ORDER_FAILED'],
      'global':['SFX_UI_TAP','SFX_UI_BACK','SFX_NOTIFICATION']}
    write_yaml(ROOT/'09_AUDIO/AUDIO_CUE_MAP.yaml',cue)
    (srcdir/'README.md').write_text('# 音频源说明\n\n本目录中的音频由 `13_SCRIPTS/generate_assets_v2.py` 程序化生成，可重复生成。BGM以Media3循环播放，SFX以SoundPool播放。禁止在客户端同时叠加多个BGM。\n',encoding='utf-8')

# CONTACT SHEETS -------------------------------------------------------
def label_image(im:Image.Image,title:str,width:int):
    h=34;out=Image.new('RGB',(width,im.height+h),'white');out.paste(im.convert('RGB'),((width-im.width)//2,0));d=ImageDraw.Draw(out);d.text((width//2,im.height+17),title,font=font(13,True),anchor='mm',fill='#172034');return out

def contact_sheet(paths:list[Path],out:Path,cols:int,thumb_size:tuple[int,int],title:str):
    margin=18; label_h=32; rows=math.ceil(len(paths)/cols)
    cellw,cellh=thumb_size[0],thumb_size[1]+label_h
    sheet=Image.new('RGB',(cols*cellw+(cols+1)*margin,rows*cellh+(rows+1)*margin+58),'#eef2f7')
    d=ImageDraw.Draw(sheet);d.text((margin,22),title,font=font(26,True),fill='#172034')
    y0=58
    for idx,p in enumerate(paths):
        im=Image.open(p).convert('RGB'); im.thumbnail(thumb_size,Image.Resampling.LANCZOS)
        x=margin+(idx%cols)*(cellw+margin)+(cellw-im.width)//2
        y=y0+margin+(idx//cols)*(cellh+margin)
        d.rounded_rectangle((margin+(idx%cols)*(cellw+margin),y-5,margin+(idx%cols)*(cellw+margin)+cellw,y+thumb_size[1]+label_h),12,fill='white',outline='#d8e0e8')
        sheet.paste(im,(x,y))
        d.text((margin+(idx%cols)*(cellw+margin)+cellw//2,y+thumb_size[1]+16),p.stem,font=font(10),anchor='mm',fill='#68728A')
    ensure(out.parent);sheet.save(out,optimize=True)

def generate_contacts():
    croot=ROOT/'04_UI/CONTACTS';ensure(croot)
    app=sorted((ROOT/'04_UI/APP').glob('*.png'))
    admin=sorted((ROOT/'04_UI/ADMIN').glob('*.png'))
    h5=sorted((ROOT/'04_UI/H5').glob('*.png'))
    for i in range(0,len(app),12): contact_sheet(app[i:i+12],croot/f'APP_CONTACT_{i//12+1:02d}.png',4,(176,380),f'Android效果图目录 {i//12+1:02d}')
    for i in range(0,len(admin),12): contact_sheet(admin[i:i+12],croot/f'ADMIN_CONTACT_{i//12+1:02d}.png',3,(400,250),f'管理后台效果图目录 {i//12+1:02d}')
    contact_sheet(h5,croot/'H5_CONTACT_01.png',3,(220,476),'H5效果图目录')
    miners=sorted((ROOT/'06_MINERS/PNG').glob('*.png')); contact_sheet(miners,ROOT/'06_MINERS/CONTACTS/MINER_36_CONTACT.png',6,(150,150),'星矿纪元 36级矿机总览')
    icons=sorted((ROOT/'07_GAME_ASSETS/objects/icons').glob('*.svg'))
    # rasterize SVG using cairosvg if available
    import cairosvg
    tmp=ROOT/'07_GAME_ASSETS/objects/icon_png';ensure(tmp);icon_png=[]
    for p in icons:
        o=tmp/(p.stem+'.png');cairosvg.svg2png(url=str(p),write_to=str(o),output_width=128,output_height=128);icon_png.append(o)
    contact_sheet(icon_png,ROOT/'07_GAME_ASSETS/objects/ICON_CONTACT.png',8,(105,105),'自定义SVG图标总览')
    effects=sorted((ROOT/'08_VFX/effects').glob('*.png')); contact_sheet(effects,ROOT/'08_VFX/VFX_CONTACT.png',4,(360,90),'核心特效精灵图总览')

# CODE TOKENS ----------------------------------------------------------
def generate_code_tokens():
    tokens=json.loads((ROOT/'03_SPECS/DESIGN_TOKENS.json').read_text('utf-8'))
    colors=tokens['colors']; kt=['package cc.orbexa.xkjy.ui.theme','','import androidx.compose.ui.graphics.Color','','object XkjyColors {']
    for k,v in colors.items(): kt.append(f'    val {k.upper()} = Color(0xFF{v.lstrip("#").upper()})')
    kt+=['}','','object XkjyDimens {','    const val PagePadding = 16','    const val CardRadius = 18','    const val DialogRadius = 28','    const val BottomNavHeight = 64','    const val PrimaryButtonHeight = 50','}']
    ensure(ROOT/'11_CODE_TOKENS/android');(ROOT/'11_CODE_TOKENS/android/XkjyDesignTokens.kt').write_text('\n'.join(kt)+'\n',encoding='utf-8')
    css=[':root {']+[f'  --xkjy-{k.replace("_","-")}: {v};' for k,v in colors.items()]+['}']
    ensure(ROOT/'11_CODE_TOKENS/web');(ROOT/'11_CODE_TOKENS/web/tokens.css').write_text('\n'.join(css)+'\n',encoding='utf-8')
    ts='export const XkjyColors = '+json.dumps(colors,ensure_ascii=False,indent=2)+' as const;\n'
    (ROOT/'11_CODE_TOKENS/web/tokens.ts').write_text(ts,encoding='utf-8')
    ids={'audio':[x['audio_id'] for x in yaml.safe_load((ROOT/'09_AUDIO/AUDIO_MANIFEST.yaml').read_text('utf-8'))['items']], 'vfx':[x['effect_id'] for x in yaml.safe_load((ROOT/'08_VFX/VFX_MANIFEST.yaml').read_text('utf-8'))['items']]}
    write_json(ROOT/'11_CODE_TOKENS/RESOURCE_IDS.json',ids)

def update_docs_scale():
    p=ROOT/'03_SPECS/DESIGN_TOKENS.json';d=json.loads(p.read_text('utf-8'));d['viewport']['android_effect_scale']=2;d['viewport']['h5_effect_scale']=2;write_json(p,d)
    for p in [ROOT/'02_DOCS/星矿纪元_前后端与视觉资源完整开发文档_V1.1.0.md',ROOT/'02_DOCS/视觉与资源实现说明.md']:
        if p.exists():
            s=p.read_text('utf-8').replace('1170×2532','780×1688').replace('3倍渲染为1170×2532','2倍渲染为780×1688')
            p.write_text(s,encoding='utf-8')

def main():
    generate_miner_vfx();print('miner vfx')
    generate_core_vfx();print('core vfx')
    generate_audio();print('audio')
    generate_contacts();print('contacts')
    generate_code_tokens();print('tokens')
    update_docs_scale();print('docs scale')

if __name__=='__main__':main()
