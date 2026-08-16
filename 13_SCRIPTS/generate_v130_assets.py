from __future__ import annotations
from pathlib import Path
import math, json, textwrap
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / '07_GAME_ASSETS' / 'v130'
BG = ASSET / 'backgrounds'
ICON = ASSET / 'icons'
OBJ = ASSET / 'objects'
PANEL = ASSET / 'panels'
THUMB = ASSET / 'project_thumbs'
MINER_SVG = ROOT / '06_MINERS' / 'SVG_V130'
MINER_PNG = ROOT / '06_MINERS' / 'PNG_V130'
CONTACT = ROOT / '06_MINERS' / 'CONTACTS'
for d in [BG, ICON, OBJ, PANEL, THUMB, MINER_SVG, MINER_PNG, CONTACT]: d.mkdir(parents=True, exist_ok=True)

PALETTE = {
    'navy0':'#050918','navy1':'#071126','navy2':'#0B1738','navy3':'#10214B',
    'line':'#2D5E9C','line2':'#3B86D6','cyan':'#23C7E8','blue':'#3E74FF',
    'violet':'#7A4CE7','magenta':'#CE48D9','gold':'#FFC84A','orange':'#F58A2D',
    'red':'#EC5969','green':'#4AD2A6','text':'#F4F7FF','muted':'#9EACCA'
}


def write_svg(path:Path, body:str, w:int=512, h:int=512, defs:str=''):
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>{defs}</defs>{body}</svg>'''
    path.write_text(svg, encoding='utf-8')
    return path

def render(svg:Path, png:Path, out_w:int|None=None, out_h:int|None=None):
    cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=out_w, output_height=out_h)

# Common defs
GLOW_DEFS='''
<filter id="shadow" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="18" stdDeviation="15" flood-color="#000" flood-opacity=".55"/></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
<filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="metalBlue" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#8BE8FF"/><stop offset=".22" stop-color="#2A88E8"/><stop offset=".58" stop-color="#164B9D"/><stop offset="1" stop-color="#0A1E55"/></linearGradient>
<linearGradient id="metalOrange" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFE27B"/><stop offset=".2" stop-color="#F7A02D"/><stop offset=".62" stop-color="#B83E20"/><stop offset="1" stop-color="#57162B"/></linearGradient>
<linearGradient id="metalPurple" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#F8A9FF"/><stop offset=".25" stop-color="#9D4AF0"/><stop offset=".65" stop-color="#44218F"/><stop offset="1" stop-color="#160B4F"/></linearGradient>
<linearGradient id="metalGold" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFF1A3"/><stop offset=".25" stop-color="#FFC64D"/><stop offset=".62" stop-color="#D3691E"/><stop offset="1" stop-color="#69220D"/></linearGradient>
<radialGradient id="coreCyan"><stop stop-color="#FFFFFF"/><stop offset=".18" stop-color="#83F4FF"/><stop offset=".55" stop-color="#23BEEB"/><stop offset="1" stop-color="#2438A2"/></radialGradient>
<radialGradient id="corePurple"><stop stop-color="#FFFFFF"/><stop offset=".18" stop-color="#F8A1FF"/><stop offset=".55" stop-color="#A64BFF"/><stop offset="1" stop-color="#381B94"/></radialGradient>
<linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#BFFFFF" stop-opacity=".94"/><stop offset=".45" stop-color="#3FC8F7" stop-opacity=".66"/><stop offset="1" stop-color="#16468F" stop-opacity=".9"/></linearGradient>
'''

# Miner generator

def miner_svg(level:int)->str:
    group=(level-1)//6
    sub=(level-1)%6
    if group==0:
        body_grad='metalBlue'; accent='#FFC84A'; core='coreCyan'
    elif group==1:
        body_grad='metalOrange'; accent='#FF5C72'; core='coreCyan'
    elif group==2:
        body_grad='metalBlue'; accent='#55F0FF'; core='coreCyan'
    elif group==3:
        body_grad='metalPurple'; accent='#6EF4FF'; core='corePurple'
    elif group==4:
        body_grad='metalGold'; accent='#67D9FF'; core='coreCyan'
    else:
        body_grad='metalPurple' if sub<3 else 'metalGold'; accent='#74FFFF'; core='coreCyan'
    rings=''.join(f'<ellipse cx="256" cy="410" rx="{110+i*18}" ry="{24+i*5}" fill="none" stroke="{accent}" stroke-width="{4-i}" opacity="{.45-i*.08}"/>' for i in range(min(3,sub//2+1)))
    base='<ellipse cx="256" cy="430" rx="160" ry="34" fill="#01030A" opacity=".68"/><ellipse cx="256" cy="424" rx="132" ry="20" fill="#16285F" opacity=".58"/>'
    sparkle=''.join(f'<circle cx="{80+(i*67+level*23)%350}" cy="{80+(i*91+level*31)%270}" r="{2+(i%3)}" fill="{accent}" opacity="{.35+.08*(i%5)}"/>' for i in range(7+sub))
    # group-specific body
    if group==0:
        wheels=''.join(f'<g transform="translate({x},0)"><circle cx="0" cy="383" r="42" fill="#070C1F" stroke="#244B86" stroke-width="8"/><circle cx="0" cy="383" r="23" fill="url(#coreCyan)" stroke="#B8FCFF" stroke-width="4"/></g>' for x in (160,352))
        accessories=''
        if sub>=1: accessories += '<rect x="238" y="124" width="36" height="56" rx="12" fill="url(#glass)" stroke="#BFFFFF" stroke-width="4"/>'
        if sub>=2: accessories += '<path d="M145 220 L105 180 L118 160 L175 205Z" fill="url(#metalGold)" stroke="#FFD979" stroke-width="5"/>'
        if sub>=3: accessories += '<path d="M365 220 L410 168 L431 188 L382 240Z" fill="url(#metalGold)" stroke="#FFD979" stroke-width="5"/>'
        if sub>=4: accessories += '<circle cx="256" cy="226" r="27" fill="url(#coreCyan)" stroke="#D5FFFF" stroke-width="5" filter="url(#glow)"/>'
        if sub>=5: accessories += '<path d="M113 255 C75 230 63 190 83 160" fill="none" stroke="#55F0FF" stroke-width="7" stroke-dasharray="10 10"/><path d="M399 255 C437 230 449 190 429 160" fill="none" stroke="#55F0FF" stroke-width="7" stroke-dasharray="10 10"/>'
        body=f'''{wheels}<path d="M125 352 Q112 285 152 222 Q182 180 256 177 Q330 180 360 222 Q400 285 387 352 Q346 374 256 374 Q166 374 125 352Z" fill="url(#{body_grad})" stroke="#8DEBFF" stroke-width="7"/>
        <path d="M174 224 Q190 160 256 154 Q322 160 338 224Z" fill="url(#glass)" stroke="#D4FFFF" stroke-width="6"/>
        <path d="M152 330 H360" stroke="{accent}" stroke-width="12" stroke-linecap="round"/>
        <path d="M176 292 H230" stroke="#D7F9FF" stroke-width="8" stroke-linecap="round" opacity=".8"/>{accessories}'''
    elif group==1:
        tracks=''.join(f'<g transform="translate({x},0)"><rect x="-90" y="345" width="180" height="72" rx="32" fill="#080A18" stroke="#6D2430" stroke-width="7"/><path d="M-62 382 H62" stroke="#FF6B73" stroke-width="14" stroke-dasharray="16 12" stroke-linecap="round"/></g>' for x in (178,334))
        accessories=''
        if sub>=1: accessories += '<circle cx="256" cy="196" r="18" fill="url(#coreCyan)" stroke="#E6FFFF" stroke-width="4"/>'
        if sub>=2: accessories += '<path d="M124 250 L82 206 L103 181 L159 232Z" fill="url(#metalGold)" stroke="#FFD979" stroke-width="5"/>'
        if sub>=3: accessories += '<path d="M382 250 L430 205 L447 232 L393 274Z" fill="url(#metalGold)" stroke="#FFD979" stroke-width="5"/>'
        if sub>=4: accessories += '<path d="M215 150 L256 104 L297 150" fill="none" stroke="#FF6978" stroke-width="9" stroke-linecap="round"/>'
        if sub>=5: accessories += '<circle cx="256" cy="270" r="38" fill="url(#corePurple)" stroke="#FFC5FF" stroke-width="6" filter="url(#glow)"/>'
        body=f'''{tracks}<path d="M110 342 Q120 236 183 183 Q217 153 287 160 Q354 167 397 232 L382 342 Q318 369 244 368 Q165 367 110 342Z" fill="url(#{body_grad})" stroke="#FFD37A" stroke-width="7"/>
        <path d="M188 221 Q205 167 256 159 Q315 164 334 226 L318 260 H180Z" fill="url(#glass)" stroke="#FFE5A4" stroke-width="5"/>
        <path d="M148 316 H351" stroke="{accent}" stroke-width="11" stroke-linecap="round"/>{accessories}'''
    elif group==2:
        legs=''.join(f'<path d="M{x} 320 L{x-35 if x<256 else x+35} 405" stroke="#9AF5FF" stroke-width="18" stroke-linecap="round"/><circle cx="{x-35 if x<256 else x+35}" cy="405" r="18" fill="#13366E" stroke="#C6FFFF" stroke-width="5"/>' for x in (170,342))
        arms=''
        if sub>=1: arms += '<path d="M151 250 L78 212 L53 241 L139 284Z" fill="url(#metalBlue)" stroke="#9EF7FF" stroke-width="6"/>'
        if sub>=2: arms += '<path d="M361 250 L434 212 L459 241 L373 284Z" fill="url(#metalBlue)" stroke="#9EF7FF" stroke-width="6"/>'
        if sub>=3: arms += '<path d="M210 160 L178 104" stroke="#77F2FF" stroke-width="10" stroke-linecap="round"/><circle cx="174" cy="96" r="14" fill="url(#coreCyan)"/>'
        if sub>=4: arms += '<path d="M302 160 L334 104" stroke="#77F2FF" stroke-width="10" stroke-linecap="round"/><circle cx="338" cy="96" r="14" fill="url(#coreCyan)"/>'
        if sub>=5: arms += '<ellipse cx="256" cy="255" rx="118" ry="96" fill="none" stroke="#55F0FF" stroke-width="8" stroke-dasharray="18 11" filter="url(#glow)"/>'
        body=f'''{legs}<path d="M132 314 Q137 209 214 159 Q256 131 299 160 Q376 210 380 314 Q327 359 256 360 Q185 359 132 314Z" fill="url(#{body_grad})" stroke="#9EF5FF" stroke-width="7"/>
        <circle cx="256" cy="248" r="72" fill="#071737" stroke="#A8F8FF" stroke-width="8"/><circle cx="256" cy="248" r="52" fill="url(#{core})" filter="url(#glow)"/>
        <path d="M188 330 H324" stroke="{accent}" stroke-width="10" stroke-linecap="round"/>{arms}'''
    elif group==3:
        fins=''.join(f'<path d="M{x} 302 L{x-85 if x<256 else x+85} 255 L{x-70 if x<256 else x+70} 330Z" fill="url(#metalPurple)" stroke="#F4A8FF" stroke-width="6"/>' for x in (178,334))
        extras=''
        if sub>=1: extras += '<ellipse cx="256" cy="350" rx="118" ry="28" fill="none" stroke="#F27CFF" stroke-width="8" filter="url(#glow)"/>'
        if sub>=2: extras += '<circle cx="256" cy="118" r="15" fill="url(#corePurple)"/><path d="M256 132 V164" stroke="#F3A6FF" stroke-width="7"/>'
        if sub>=3: extras += '<path d="M120 210 Q76 245 91 299" fill="none" stroke="#60F7FF" stroke-width="7"/><path d="M392 210 Q436 245 421 299" fill="none" stroke="#60F7FF" stroke-width="7"/>'
        if sub>=4: extras += '<ellipse cx="256" cy="250" rx="150" ry="120" fill="none" stroke="#61F5FF" stroke-width="5" stroke-dasharray="13 12" opacity=".75"/>'
        if sub>=5: extras += '<path d="M130 164 L167 125 M382 164 L345 125" stroke="#FFE1FF" stroke-width="9" stroke-linecap="round"/>'
        body=f'''{fins}<path d="M121 318 Q131 202 201 155 Q256 119 311 155 Q381 202 391 318 Q337 371 256 374 Q175 371 121 318Z" fill="url(#{body_grad})" stroke="#F0A0FF" stroke-width="7"/>
        <circle cx="256" cy="252" r="82" fill="#140A43" stroke="#FEAEFF" stroke-width="8"/><circle cx="256" cy="252" r="58" fill="url(#{core})" filter="url(#glow)"/>
        {extras}'''
    elif group==4:
        pods=''.join(f'<path d="M{x} 250 L{x-58 if x<256 else x+58} 220 L{x-69 if x<256 else x+69} 284 L{x-10 if x<256 else x+10} 312Z" fill="url(#metalGold)" stroke="#FFF0A6" stroke-width="6"/>' for x in (176,336))
        extras=''
        if sub>=1: extras += '<path d="M190 157 L174 105 M322 157 L338 105" stroke="#7BE9FF" stroke-width="8" stroke-linecap="round"/>'
        if sub>=2: extras += '<circle cx="256" cy="148" r="14" fill="url(#coreCyan)"/>'
        if sub>=3: extras += '<ellipse cx="256" cy="272" rx="125" ry="65" fill="none" stroke="#70DFFF" stroke-width="6" stroke-dasharray="12 10"/>'
        if sub>=4: extras += '<path d="M151 341 Q256 399 361 341" fill="none" stroke="#FFD86A" stroke-width="9"/>'
        if sub>=5: extras += '<ellipse cx="256" cy="257" rx="161" ry="130" fill="none" stroke="#FFE991" stroke-width="6" stroke-dasharray="18 12" filter="url(#glow)"/>'
        body=f'''{pods}<path d="M124 317 L157 184 L256 133 L355 184 L388 317 L323 368 H189Z" fill="url(#{body_grad})" stroke="#FFF1A5" stroke-width="7"/>
        <ellipse cx="256" cy="258" rx="94" ry="72" fill="#0B163F" stroke="#B7F7FF" stroke-width="8"/><ellipse cx="256" cy="258" rx="63" ry="43" fill="url(#{core})" filter="url(#glow)"/>{extras}'''
    else:
        orbit_count=2+sub//2
        orbits=''.join(f'<ellipse cx="256" cy="250" rx="{95+i*22}" ry="{45+i*14}" fill="none" stroke="{accent if i%2==0 else '#F6B5FF'}" stroke-width="{8-i}" transform="rotate({i*48+level*3} 256 250)" opacity="{.9-i*.12}"/>' for i in range(orbit_count))
        nodes=''.join(f'<circle cx="{256+math.cos(i*2*math.pi/(4+sub))* (105+sub*7):.1f}" cy="{250+math.sin(i*2*math.pi/(4+sub))* (62+sub*4):.1f}" r="{8+sub//2}" fill="url(#coreCyan)" stroke="#fff" stroke-width="2"/>' for i in range(4+sub))
        extras=''
        if sub>=3: extras += '<path d="M165 365 Q256 410 347 365" fill="none" stroke="#FFD86A" stroke-width="10"/>'
        if sub>=4: extras += '<circle cx="256" cy="250" r="128" fill="none" stroke="#FBD765" stroke-width="6" stroke-dasharray="16 12"/>'
        if sub>=5: extras += '<path d="M256 78 L274 122 L322 126 L285 156 L296 204 L256 178 L216 204 L227 156 L190 126 L238 122Z" fill="url(#metalGold)" stroke="#FFF2A4" stroke-width="5" filter="url(#glow)"/>'
        body=f'''{orbits}{nodes}<circle cx="256" cy="250" r="75" fill="url(#{core})" stroke="#E8FFFF" stroke-width="8" filter="url(#glow)"/>
        <path d="M158 356 Q256 408 354 356 L328 399 Q256 432 184 399Z" fill="url(#{body_grad})" stroke="#C6FFFF" stroke-width="7"/>{extras}'''
    lvl=f'''<g transform="translate(196 445)"><rect width="120" height="42" rx="21" fill="#071126" stroke="{accent}" stroke-width="3"/><text x="60" y="28" text-anchor="middle" font-family="Arial,sans-serif" font-size="22" font-weight="800" fill="#fff">Lv.{level}</text></g>'''
    return f'<rect width="512" height="512" fill="none"/>{sparkle}{rings}{base}<g filter="url(#shadow)">{body}</g>{lvl}'

for level in range(1,37):
    svg=write_svg(MINER_SVG/f'MINER_L{level:02d}.svg', miner_svg(level), defs=GLOW_DEFS)
    render(svg, MINER_PNG/f'MINER_L{level:02d}.png', 512,512)

# Avatar and mascot
avatar_body='''<rect width="512" height="512" rx="120" fill="url(#avbg)"/><circle cx="256" cy="256" r="210" fill="#0E1D48" stroke="#52D8FF" stroke-width="12"/><path d="M129 408 Q151 321 256 320 Q361 321 383 408" fill="#315CDA"/><circle cx="256" cy="222" r="109" fill="#FFD3B0"/><path d="M148 205 Q160 93 256 91 Q352 93 364 205 Q320 145 256 149 Q192 145 148 205Z" fill="#3D2032"/><circle cx="218" cy="229" r="12" fill="#23162C"/><circle cx="294" cy="229" r="12" fill="#23162C"/><path d="M219 277 Q256 302 293 277" fill="none" stroke="#CF6760" stroke-width="11" stroke-linecap="round"/><path d="M145 206 Q112 170 133 137" fill="none" stroke="#5FE5FF" stroke-width="18"/><path d="M367 206 Q400 170 379 137" fill="none" stroke="#5FE5FF" stroke-width="18"/><circle cx="405" cy="107" r="46" fill="#FFC849" stroke="#FFF1A2" stroke-width="8"/><path d="M405 76 L414 96 L437 99 L420 114 L425 137 L405 125 L385 137 L390 114 L373 99 L396 96Z" fill="#F0692F"/>'''
avdefs='<linearGradient id="avbg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#4B6CFF"/><stop offset="1" stop-color="#7B35E8"/></linearGradient>'
avsvg=write_svg(OBJ/'avatar_captain_v130.svg',avatar_body,defs=avdefs)
render(avsvg,OBJ/'avatar_captain_v130.png',512,512)

robot='''<rect width="512" height="512" fill="none"/><ellipse cx="256" cy="442" rx="116" ry="28" fill="#01030A" opacity=".55"/><path d="M180 390 L156 453 M332 390 L356 453" stroke="#54E2FF" stroke-width="25" stroke-linecap="round"/><path d="M140 280 L83 325 L108 365 L167 322 M372 280 L429 325 L404 365 L345 322" fill="#3BA8E8" stroke="#A5F8FF" stroke-width="8"/><rect x="135" y="120" width="242" height="292" rx="102" fill="url(#robotBody)" stroke="#D7F9FF" stroke-width="10"/><rect x="177" y="185" width="158" height="112" rx="52" fill="#071126"/><circle cx="222" cy="240" r="25" fill="url(#coreCyan)" filter="url(#glow)"/><circle cx="290" cy="240" r="25" fill="url(#coreCyan)" filter="url(#glow)"/><path d="M219 329 Q256 353 293 329" fill="none" stroke="#315BA7" stroke-width="12" stroke-linecap="round"/><path d="M256 120 V76" stroke="#6EEBFF" stroke-width="10"/><circle cx="256" cy="62" r="19" fill="#FFC849" stroke="#FFF3AF" stroke-width="5"/>'''
robotdefs=GLOW_DEFS+'<linearGradient id="robotBody" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#F3F7FF"/><stop offset=".45" stop-color="#A8C7FF"/><stop offset="1" stop-color="#6F8CF2"/></linearGradient>'
robotsvg=write_svg(OBJ/'mascot_robot_v130.svg',robot,defs=robotdefs)
render(robotsvg,OBJ/'mascot_robot_v130.png',512,512)

# Token icons and generic icons. Simple paths intentionally custom.
icons={
'nav_home':'M84 224 L256 76 L428 224 V420 H311 V300 H201 V420 H84Z',
'nav_project':'M102 76 H410 V430 H102Z M145 142 H368 M145 210 H368 M145 278 H322',
'nav_mall':'M116 170 H396 L366 430 H146Z M171 170 Q171 76 256 76 Q341 76 341 170',
'nav_discover':'M256 82 A174 174 0 1 0 256 430 A174 174 0 1 0 256 82 M310 160 L276 276 L160 310 L194 194Z',
'nav_me':'M256 92 A86 86 0 1 0 256 264 A86 86 0 1 0 256 92 M104 430 Q124 292 256 292 Q388 292 408 430Z',
'store':'M99 178 H413 L381 432 H131Z M167 178 Q167 82 256 82 Q345 82 345 178',
'warehouse':'M76 220 L256 82 L436 220 V424 H76Z M154 424 V278 H358 V424',
'atlas':'M82 92 Q170 62 248 112 V428 Q170 378 82 408Z M430 92 Q342 62 264 112 V428 Q342 378 430 408Z',
'task':'M132 90 H380 V432 H132Z M188 70 H324 V124 H188Z M180 202 L220 240 L292 164 M180 320 H330',
'box':'M94 190 H418 V426 H94Z M76 132 H436 V210 H76Z M256 132 V426 M122 106 Q160 56 238 132 M390 106 Q352 56 274 132',
'identity':'M256 80 L418 140 V264 Q418 386 256 446 Q94 386 94 264 V140Z M190 258 L235 303 L330 197',
'invite':'M170 225 A70 70 0 1 0 170 85 A70 70 0 1 0 170 225 M342 225 A70 70 0 1 0 342 85 A70 70 0 1 0 342 225 M62 424 Q74 274 170 274 Q224 274 256 318 Q288 274 342 274 Q438 274 450 424Z',
'member':'M256 70 L314 174 L430 194 L348 278 L366 398 L256 346 L146 398 L164 278 L82 194 L198 174Z',
'withdraw':'M90 100 H422 V410 H90Z M90 180 H422 M156 270 H356 M256 225 V355 M210 310 L256 356 L302 310',
'wallet':'M86 142 H392 Q430 142 430 180 V398 Q430 430 392 430 H86 Q68 430 68 412 V160 Q68 142 86 142Z M320 230 H444 V344 H320 Q284 344 284 287 Q284 230 320 230Z',
'message':'M74 106 H438 V362 H250 L150 440 V362 H74Z',
'settings':'M256 170 A86 86 0 1 0 256 342 A86 86 0 1 0 256 170 M256 62 V126 M256 386 V450 M62 256 H126 M386 256 H450 M119 119 L164 164 M348 348 L393 393 M393 119 L348 164 M164 348 L119 393',
'help':'M256 82 A174 174 0 1 0 256 430 A174 174 0 1 0 256 82 M196 190 Q207 128 266 128 Q333 128 333 188 Q333 231 286 252 Q256 267 256 306 M256 357 V371',
'order':'M112 76 H400 V436 H112Z M168 160 H344 M168 228 H344 M168 296 H304',
'commission':'M96 362 L184 274 L244 326 L382 160 M326 160 H382 V216',
'merge':'M112 112 H224 V224 H112Z M288 112 H400 V224 H288Z M200 288 H312 V400 H200Z M168 240 L232 304 M344 240 L280 304',
'ranking':'M146 224 H236 V432 H146Z M276 150 H366 V432 H276Z M36 292 H126 V432 H36Z M256 70 L276 111 L322 118 L289 150 L297 196 L256 174 L215 196 L223 150 L190 118 L236 111Z',
'sign':'M112 94 H400 V430 H112Z M112 180 H400 M176 62 V128 M336 62 V128 M178 272 L228 322 L338 212',
'back':'M330 92 L166 256 L330 420',
'close':'M120 120 L392 392 M392 120 L120 392',
'search':'M222 92 A130 130 0 1 0 222 352 A130 130 0 1 0 222 92 M318 318 L430 430',
'plus':'M256 92 V420 M92 256 H420',
'copy':'M170 120 H410 V400 H170Z M102 200 V88 H342',
'gift':'M90 190 H422 V430 H90Z M70 130 H442 V210 H70Z M256 130 V430 M126 96 Q170 42 238 130 M386 96 Q342 42 274 130',
'camera':'M90 154 H160 L190 100 H322 L352 154 H422 V410 H90Z M256 194 A88 88 0 1 0 256 370 A88 88 0 1 0 256 194',
'check':'M112 260 L220 368 L408 148',
'warning':'M256 72 L454 430 H58Z M256 180 V310 M256 354 V370',
}

def icon_svg(name,pathdata):
    defs='''<linearGradient id="ibg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#314C9A"/><stop offset="1" stop-color="#151F54"/></linearGradient><linearGradient id="istroke" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FFF0A0"/><stop offset=".45" stop-color="#FFC23C"/><stop offset="1" stop-color="#F07726"/></linearGradient><filter id="iglow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'''
    body=f'''<rect x="32" y="32" width="448" height="448" rx="126" fill="url(#ibg)" stroke="#2CC6EA" stroke-width="16"/><rect x="52" y="52" width="408" height="408" rx="108" fill="none" stroke="#7B4FE9" stroke-width="6" opacity=".7"/><path d="{pathdata}" fill="none" stroke="url(#istroke)" stroke-width="28" stroke-linecap="round" stroke-linejoin="round" filter="url(#iglow)"/>'''
    p=write_svg(ICON/f'icon_{name}.svg',body,defs=defs)
    render(p,ICON/f'icon_{name}.png',256,256)
for n,p in icons.items(): icon_svg(n,p)

# Token assets
for name, c1,c2,symbol in [
    ('star_point','#FFE36A','#F48A24','★'),('energy_chip','#C98BFF','#6334D7','◆'),('cash','#FF7A86','#B92262','¥')]:
    defs=f'<radialGradient id="t"><stop stop-color="#fff"/><stop offset=".18" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></radialGradient><filter id="g"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    body=f'<circle cx="256" cy="256" r="196" fill="url(#t)" stroke="#FFF6C9" stroke-width="18" filter="url(#g)"/><circle cx="256" cy="256" r="151" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="8"/><text x="256" y="330" text-anchor="middle" font-family="Arial,sans-serif" font-size="210" font-weight="900" fill="#fff">{symbol}</text>'
    p=write_svg(ICON/f'token_{name}.svg',body,defs=defs);render(p,ICON/f'token_{name}.png',256,256)

# Backgrounds: restrained business and rich game scene
space_defs='''<radialGradient id="space" cx="35%" cy="10%"><stop stop-color="#132D67"/><stop offset=".35" stop-color="#07142F"/><stop offset="1" stop-color="#030711"/></radialGradient><radialGradient id="planet"><stop stop-color="#695BE8"/><stop offset=".55" stop-color="#263BB0"/><stop offset="1" stop-color="#111A58"/></radialGradient><linearGradient id="rock" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#5D6150"/><stop offset="1" stop-color="#20292B"/></linearGradient><linearGradient id="crystal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#B8FFFF"/><stop offset=".3" stop-color="#43D0F1"/><stop offset=".7" stop-color="#4467F6"/><stop offset="1" stop-color="#7F35E7"/></linearGradient><filter id="bglow"><feGaussianBlur stdDeviation="16"/></filter>'''
# 390x844 SVGs
stars=''.join(f'<circle cx="{(i*73+29)%390}" cy="{(i*131+47)%620}" r="{1+(i%3)*.45}" fill="#fff" opacity="{.25+(i%5)*.1}"/>' for i in range(45))
crystals='<g opacity=".92"><path d="M20 780 L43 690 L66 780 L46 832Z" fill="url(#crystal)" stroke="#BFFFFF" stroke-width="3"/><path d="M325 758 L350 654 L378 758 L356 824Z" fill="url(#crystal)" stroke="#BFFFFF" stroke-width="3"/></g>'
base_space=f'<rect width="390" height="844" fill="url(#space)"/>{stars}<circle cx="332" cy="105" r="94" fill="url(#planet)" opacity=".44"/><path d="M242 99 Q335 63 418 74" fill="none" stroke="#6947E9" stroke-width="9" opacity=".48"/>{crystals}'
write_svg(BG/'bg_business_space.svg',base_space,390,844,space_defs)
render(BG/'bg_business_space.svg',BG/'bg_business_space.png',780,1688)
# auth
body_auth=base_space+'<ellipse cx="195" cy="630" rx="245" ry="190" fill="#0A1839" opacity=".72"/><path d="M0 710 Q100 650 205 700 Q300 745 390 680 V844 H0Z" fill="#050917"/>'
write_svg(BG/'bg_auth_space.svg',body_auth,390,844,space_defs);render(BG/'bg_auth_space.svg',BG/'bg_auth_space.png',780,1688)
# game scene
scene=f'''<rect width="390" height="844" fill="url(#space)"/>{stars}<circle cx="333" cy="88" r="76" fill="url(#planet)" opacity=".7"/><path d="M0 300 Q58 230 120 257 Q198 200 264 256 Q329 213 390 259 V430 H0Z" fill="#152B43"/><path d="M0 350 Q69 281 145 322 Q215 276 293 329 Q344 300 390 325 V480 H0Z" fill="#263D42"/><path d="M0 420 Q90 367 187 403 Q279 361 390 405 V844 H0Z" fill="url(#rock)"/><path d="M0 458 Q91 430 171 470 Q260 424 390 458 V844 H0Z" fill="#4A4E3C"/>
<path d="M84 492 L153 445 L224 467 L301 438 L369 486 L337 727 L61 727Z" fill="#59604A" stroke="#879070" stroke-width="3"/>
<path d="M103 513 L160 479 L218 494 L288 471 L342 510 L317 690 L82 690Z" fill="#303A36" stroke="#657563" stroke-width="2"/>
<g opacity=".85"><rect x="41" y="405" width="54" height="70" rx="8" fill="#142B4A" stroke="#31BCD9" stroke-width="3"/><rect x="294" y="390" width="62" height="86" rx="8" fill="#192650" stroke="#7E50DF" stroke-width="3"/><path d="M56 405 L68 380 L80 405" fill="#F6A63B"/><circle cx="325" cy="414" r="10" fill="#9B55FF" filter="url(#bglow)"/></g>{crystals}'''
write_svg(BG/'bg_mine_scene.svg',scene,390,844,space_defs);render(BG/'bg_mine_scene.svg',BG/'bg_mine_scene.png',780,1688)
# market
market=base_space+'<path d="M0 315 Q92 278 192 318 Q300 271 390 310 V844 H0Z" fill="#061027" opacity=".78"/><g opacity=".25" stroke="#2D65AD" stroke-width="1"><path d="M25 360 H365 M25 430 H365 M25 500 H365 M25 570 H365"/></g>'
write_svg(BG/'bg_market.svg',market,390,844,space_defs);render(BG/'bg_market.svg',BG/'bg_market.png',780,1688)
# profile
profile=base_space+'<circle cx="65" cy="176" r="100" fill="#1C3888" opacity=".25"/><path d="M0 590 Q84 535 164 570 Q282 520 390 574 V844 H0Z" fill="#050918" opacity=".72"/>'
write_svg(BG/'bg_profile.svg',profile,390,844,space_defs);render(BG/'bg_profile.svg',BG/'bg_profile.png',780,1688)
# secure dark
secure=base_space+'<rect x="0" y="250" width="390" height="594" fill="#030713" opacity=".35"/>'
write_svg(BG/'bg_secure.svg',secure,390,844,space_defs);render(BG/'bg_secure.svg',BG/'bg_secure.png',780,1688)

# project thumbnails original vectors
thumb_data=[
('frontier','星际边疆计划','#314CD4','#F59B35'),
('ai','AI智能工具箱','#3159A8','#38D5D2'),
('web3','Web3生态任务','#4C3197','#D349D7'),
('city','区域链应用推广','#A64A2B','#F2C14B'),
('community','联盟争夺赛','#284E78','#8E6BFF'),
('new','新用户福利活动','#AA3155','#FF8C4A'),
]
for idx,(nm,title,c1,c2) in enumerate(thumb_data):
    defs=f'<linearGradient id="tbg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient><filter id="tg"><feGaussianBlur stdDeviation="10"/></filter>'
    b=f'''<rect width="640" height="360" rx="38" fill="url(#tbg)"/><circle cx="510" cy="64" r="110" fill="#fff" opacity=".1"/><path d="M0 260 Q100 {170+idx*7} 188 244 Q290 142 384 238 Q500 160 640 242 V360 H0Z" fill="#071126" opacity=".65"/><g fill="#F6D270"><rect x="85" y="165" width="54" height="118"/><rect x="155" y="125" width="71" height="158"/><rect x="242" y="185" width="58" height="98"/><rect x="316" y="108" width="85" height="175"/><rect x="418" y="148" width="63" height="135"/></g><g fill="#57D8FF"><rect x="99" y="185" width="8" height="12"/><rect x="176" y="150" width="10" height="13"/><rect x="345" y="135" width="11" height="14"/><rect x="440" y="172" width="9" height="11"/></g><text x="42" y="70" font-family="Arial,sans-serif" font-size="34" font-weight="900" fill="#fff">{title}</text>'''
    p=write_svg(THUMB/f'{nm}.svg',b,640,360,defs);render(p,THUMB/f'{nm}.png',640,360)

# Panel nine-slice SVGs, fixed size examples
panel_defs='''<linearGradient id="pbg" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#132A5A"/><stop offset="1" stop-color="#071127"/></linearGradient><linearGradient id="pline" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#2A6DAE"/><stop offset=".5" stop-color="#41C7E7"/><stop offset="1" stop-color="#2A6DAE"/></linearGradient>'''
for name,rad in [('panel_regular',24),('panel_compact',18),('panel_modal',30)]:
    b=f'<rect x="4" y="4" width="504" height="248" rx="{rad}" fill="url(#pbg)" stroke="url(#pline)" stroke-width="4"/><path d="M34 16 H478" stroke="#fff" stroke-opacity=".1" stroke-width="2"/>'
    p=write_svg(PANEL/f'{name}.svg',b,512,256,panel_defs);render(p,PANEL/f'{name}.png',512,256)

# Manifest
manifest={
 'version':'1.3.0','miner_count':36,'miner_svg_dir':'06_MINERS/SVG_V130','miner_png_dir':'06_MINERS/PNG_V130',
 'icons':sorted([p.name for p in ICON.glob('*.svg')]),'backgrounds':sorted([p.name for p in BG.glob('*.svg')]),
 'project_thumbnails':sorted([p.name for p in THUMB.glob('*.png')])
}
(ASSET/'ASSET_MANIFEST_V130.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('generated',len(list(MINER_PNG.glob('*.png'))),'miners',len(list(ICON.glob('*.svg'))),'icons')
