from __future__ import annotations
import html, json, math
from pathlib import Path
from page_catalog import flatten, EXTRA_STATES

BASE=Path('/mnt/data/xkjy_v110_work/XKJY_V110')

CSS=r'''
:root{
  --space-950:#07111F;--space-900:#0B1830;--space-800:#102A4C;--space-700:#173B66;
  --primary:#FF7A3D;--primary-deep:#F0642F;--gold:#FFC84A;--energy:#27D5C4;--blue:#3A8CFF;
  --violet:#8B5CFF;--magenta:#ED5CBE;--surface:#FFF9F1;--surface2:#FFFFFF;--text:#172034;
  --muted:#68728A;--border:#E8DFD3;--success:#24B878;--warning:#F4A62A;--error:#E55454;
  --shadow:0 14px 34px rgba(7,17,31,.16);--shadow-soft:0 8px 24px rgba(7,17,31,.10);
}
*{box-sizing:border-box}html,body{margin:0;padding:0;width:100%;height:100%;font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;color:var(--text);background:#e7edf3}
button,input,textarea{font:inherit}.app-shell{width:390px;height:844px;overflow:hidden;background:var(--surface);position:relative;margin:0 auto}.statusbar{height:28px;padding:7px 16px 0;display:flex;justify-content:space-between;align-items:flex-start;font-size:11px;font-weight:800;position:relative;z-index:20}.statusbar.dark{color:#fff}.status-icons{display:flex;gap:6px;align-items:center}.dot-signal{width:19px;height:9px;display:inline-block;background:linear-gradient(90deg,currentColor 0 20%,transparent 20% 28%,currentColor 28% 48%,transparent 48% 56%,currentColor 56% 76%,transparent 76% 84%,currentColor 84%);clip-path:polygon(0 100%,0 75%,20% 75%,20% 55%,40% 55%,40% 35%,60% 35%,60% 15%,80% 15%,80% 0,100% 0,100% 100%)}
.topbar{height:56px;padding:0 12px;display:grid;grid-template-columns:48px 1fr 48px;align-items:center;background:rgba(255,249,241,.96);position:relative;z-index:15;border-bottom:1px solid rgba(232,223,211,.8)}.topbar.dark{background:rgba(7,17,31,.42);color:#fff;border-bottom-color:rgba(255,255,255,.08);backdrop-filter:blur(8px)}.topbar h1{font-size:19px;margin:0;text-align:center;font-weight:800;letter-spacing:.2px}.icon-btn{width:44px;height:44px;border:0;background:transparent;border-radius:14px;display:flex;align-items:center;justify-content:center}.icon-btn img{width:23px;height:23px}.topbar.dark .icon-btn img{filter:brightness(0) invert(1)}
.page-content{height:696px;overflow:hidden;padding:14px 16px 18px;position:relative}.page-content.with-bottom{height:632px}.page-content.scroll{overflow-y:auto}.page-content::-webkit-scrollbar{display:none}.bottom-nav{position:absolute;left:0;right:0;bottom:0;height:64px;background:rgba(255,255,255,.96);border-top:1px solid #ebe4dc;display:flex;align-items:center;justify-content:space-around;z-index:20;box-shadow:0 -6px 22px rgba(7,17,31,.06)}.nav-item{width:68px;height:56px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;color:#8b93a5;font-size:10px;font-weight:700}.nav-item img{width:23px;height:23px;opacity:.68}.nav-item.active{color:var(--primary-deep)}.nav-item.active img{opacity:1;filter:sepia(1) saturate(8) hue-rotate(330deg)}
.hero{border-radius:24px;padding:20px;background:linear-gradient(135deg,var(--space-800),var(--space-700));color:#fff;box-shadow:var(--shadow);position:relative;overflow:hidden}.hero:after{content:"";position:absolute;width:190px;height:190px;border:1px solid rgba(39,213,196,.28);border-radius:50%;right:-65px;top:-70px}.hero .eyebrow{font-size:11px;color:#98efe5;font-weight:800;letter-spacing:1px}.hero h2{font-size:24px;line-height:1.25;margin:8px 0}.hero p{font-size:12px;line-height:1.7;color:#cfe1ed;margin:0}.section-title{display:flex;align-items:center;justify-content:space-between;margin:18px 2px 10px}.section-title h3{margin:0;font-size:16px}.section-title span{font-size:11px;color:var(--muted)}
.card{background:#fff;border:1px solid rgba(232,223,211,.78);border-radius:18px;padding:14px;box-shadow:var(--shadow-soft)}.card.flat{box-shadow:none}.card.dark{background:linear-gradient(145deg,#173B66,#0B1830);border-color:rgba(255,255,255,.08);color:white}.card + .card{margin-top:10px}.list-row{min-height:58px;display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #eee7df}.list-row:last-child{border-bottom:0}.row-icon{width:40px;height:40px;border-radius:13px;background:#fff3e8;display:flex;align-items:center;justify-content:center;flex:0 0 auto}.row-icon.blue{background:#eaf2ff}.row-icon.green{background:#e4faf6}.row-icon.purple{background:#f1ebff}.row-icon img{width:22px;height:22px}.row-main{flex:1;min-width:0}.row-title{font-size:14px;font-weight:800}.row-sub{font-size:11px;color:var(--muted);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.row-value{font-size:13px;font-weight:800;color:var(--primary-deep)}.chevron{width:18px;height:18px;opacity:.45}
.btn{height:50px;border:0;border-radius:16px;padding:0 20px;display:inline-flex;align-items:center;justify-content:center;gap:8px;font-size:14px;font-weight:800}.btn.primary{background:linear-gradient(135deg,var(--primary),var(--primary-deep));color:#fff;box-shadow:0 9px 20px rgba(240,100,47,.28)}.btn.secondary{background:#fff3e8;color:var(--primary-deep)}.btn.dark{background:var(--space-900);color:#fff}.btn.full{width:100%}.btn.disabled{opacity:.45}.input{height:52px;background:#fff;border:1px solid var(--border);border-radius:15px;padding:0 14px;display:flex;align-items:center;gap:10px;font-size:13px;color:#9ba2b2}.input img{width:20px;height:20px;opacity:.6}.form-label{font-size:12px;font-weight:800;margin:13px 4px 7px}.form-help{font-size:10px;color:var(--muted);line-height:1.5;margin:7px 4px}.segmented{height:42px;padding:4px;background:#ece7e0;border-radius:14px;display:flex}.segmented span{flex:1;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;color:#7c8494}.segmented span.active{background:#fff;color:var(--primary-deep);box-shadow:0 3px 10px rgba(7,17,31,.08)}
.badge{display:inline-flex;height:22px;padding:0 8px;border-radius:999px;align-items:center;font-size:10px;font-weight:900}.badge.headline{background:#fff0df;color:#db4f22}.badge.pin{background:#eee8ff;color:#6e3dd6}.badge.refresh{background:#dcfaf5;color:#0b8e82}.badge.member{background:linear-gradient(135deg,#8B5CFF,#ED5CBE);color:#fff}.badge.success{background:#e5f8ef;color:#16885a}.badge.warning{background:#fff3dd;color:#b86f00}.badge.error{background:#ffe8e8;color:#c43838}.chips{display:flex;gap:7px;flex-wrap:wrap}.chip{height:30px;padding:0 12px;border-radius:15px;background:#f2eee8;display:inline-flex;align-items:center;font-size:11px;font-weight:700}.chip.active{background:var(--space-900);color:#fff}
.metric-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.metric{background:#fff;border:1px solid var(--border);border-radius:18px;padding:14px}.metric .label{font-size:10px;color:var(--muted)}.metric .value{font-size:21px;font-weight:900;margin-top:5px}.metric .delta{font-size:10px;color:var(--success);margin-top:4px}.asset-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.asset-box{border-radius:16px;padding:12px 9px;color:#fff;min-height:76px;position:relative;overflow:hidden}.asset-box.star{background:linear-gradient(135deg,#F5A72D,#F0642F)}.asset-box.energy{background:linear-gradient(135deg,#27D5C4,#2372B8)}.asset-box.cash{background:linear-gradient(135deg,#55C884,#18795B)}.asset-box img{width:25px;height:25px;position:absolute;right:9px;top:9px}.asset-box .label{font-size:9px;opacity:.86}.asset-box .value{font-size:16px;font-weight:900;margin-top:18px}
.project-card{background:#fff;border-radius:19px;padding:12px;border:1px solid var(--border);box-shadow:var(--shadow-soft);margin-bottom:11px}.project-cover{height:104px;border-radius:14px;background:linear-gradient(135deg,#102A4C,#27D5C4);position:relative;overflow:hidden}.project-cover:after{content:"";position:absolute;width:135px;height:135px;border-radius:50%;background:rgba(255,200,74,.4);right:-30px;top:-30px}.project-cover .cover-title{position:absolute;left:14px;bottom:12px;color:#fff;font-size:18px;font-weight:900}.project-title{font-size:14px;font-weight:900;margin:10px 0 4px}.project-desc{font-size:11px;color:var(--muted);line-height:1.55}.project-meta{display:flex;justify-content:space-between;align-items:center;margin-top:9px;font-size:10px;color:#8c94a3}
.product-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.product{background:#fff;border:1px solid var(--border);border-radius:18px;overflow:hidden;box-shadow:var(--shadow-soft)}.product img{width:100%;height:100px;object-fit:cover}.product-body{padding:10px}.product-name{font-size:13px;font-weight:900}.product-price{font-size:16px;color:var(--primary-deep);font-weight:900;margin-top:6px}.product-sub{font-size:10px;color:var(--muted);margin-top:2px}
.toast{position:absolute;left:30px;right:30px;bottom:82px;background:rgba(7,17,31,.92);color:#fff;border-radius:14px;padding:12px 16px;font-size:12px;text-align:center;z-index:50;box-shadow:var(--shadow)}.banner-offline{position:absolute;left:12px;right:12px;top:88px;height:38px;border-radius:14px;background:#fff3dd;color:#9f6300;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;z-index:40;box-shadow:var(--shadow-soft)}
.modal-backdrop{position:absolute;inset:0;background:rgba(5,12,22,.66);z-index:80;display:flex;align-items:center;justify-content:center;padding:24px}.modal{width:100%;background:#fff9f1;border-radius:28px;padding:24px;box-shadow:0 24px 60px rgba(0,0,0,.35);text-align:center;position:relative}.modal.dark{background:linear-gradient(150deg,#173B66,#0B1830);color:#fff}.modal-icon{width:76px;height:76px;border-radius:38px;background:#fff0df;margin:0 auto 14px;display:flex;align-items:center;justify-content:center}.modal-icon img{width:38px;height:38px}.modal h2{font-size:21px;margin:4px 0 8px}.modal p{font-size:12px;line-height:1.65;color:var(--muted);margin:0 0 18px}.modal.dark p{color:#bdd2df}.spinner{width:58px;height:58px;border:6px solid #e7e0d7;border-top-color:var(--primary);border-radius:50%;margin:0 auto 18px;animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
.skeleton{background:linear-gradient(90deg,#ece7e0,#f8f5f0,#ece7e0);background-size:200% 100%;animation:shimmer 1.2s infinite;border-radius:10px}@keyframes shimmer{to{background-position:-200% 0}}.empty-state{padding:56px 24px;text-align:center}.empty-orbit{width:100px;height:100px;border-radius:50%;border:3px dashed #cad3df;margin:0 auto 18px;position:relative}.empty-orbit:after{content:"";position:absolute;width:26px;height:26px;border-radius:50%;background:var(--energy);top:4px;left:8px}.empty-state h3{font-size:17px;margin:0 0 8px}.empty-state p{font-size:11px;color:var(--muted);line-height:1.6}
/* game */
.game-shell{background:#07111f;color:#fff}.game-bg{position:absolute;inset:0;background:url('../../07_GAME_ASSETS/backgrounds/bg_mine_home.png') center/cover no-repeat}.game-vignette{position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,17,31,.1),rgba(7,17,31,.1) 62%,rgba(7,17,31,.78))}.game-hud{height:76px;padding:7px 10px;display:grid;grid-template-columns:1.1fr 1fr 1fr;gap:6px;position:relative;z-index:12}.hud-box{height:54px;border-radius:17px;background:rgba(7,17,31,.76);border:1px solid rgba(255,255,255,.12);backdrop-filter:blur(8px);padding:7px 8px;display:flex;gap:7px;align-items:center}.hud-box img{width:27px;height:27px}.hud-label{font-size:8px;color:#b7cbd9}.hud-value{font-size:12px;font-weight:900;margin-top:2px}.mine-stage{position:relative;z-index:8;height:472px;padding:16px 20px 0}.rate-pill{height:34px;border-radius:17px;background:rgba(7,17,31,.72);border:1px solid rgba(39,213,196,.35);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;margin:0 auto 10px;width:190px}.board{display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(4,1fr);gap:8px;height:382px;padding:12px;border-radius:28px;background:linear-gradient(145deg,rgba(18,42,76,.86),rgba(7,17,31,.78));border:2px solid rgba(87,205,203,.35);box-shadow:0 18px 45px rgba(0,0,0,.35),inset 0 0 30px rgba(39,213,196,.08)}.slot{position:relative;border-radius:18px;background:linear-gradient(145deg,rgba(255,255,255,.10),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center}.slot.locked{background:rgba(7,17,31,.45)}.slot.locked:after{content:"";width:24px;height:24px;background:url('../../07_GAME_ASSETS/objects/icons/ICON-LOCK.svg') center/contain no-repeat;filter:brightness(0) invert(1);opacity:.45}.slot img.miner{width:72px;height:72px;object-fit:contain;filter:drop-shadow(0 9px 8px rgba(0,0,0,.34))}.level-tag{position:absolute;bottom:4px;right:5px;height:18px;padding:0 6px;border-radius:9px;background:rgba(7,17,31,.78);font-size:9px;font-weight:900;display:flex;align-items:center}.claim-bubble{position:absolute;right:25px;top:98px;width:72px;height:72px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff8c7,#ffc84a 42%,#f0642f);box-shadow:0 0 28px rgba(255,200,74,.75);display:flex;align-items:center;justify-content:center;color:#7a3b00;font-size:11px;font-weight:900;animation:float 1.8s ease-in-out infinite}@keyframes float{50%{transform:translateY(-8px)}}.game-tools{position:relative;z-index:12;height:72px;padding:5px 13px;display:flex;justify-content:space-around;align-items:center}.tool{width:61px;text-align:center;font-size:9px;font-weight:800;color:#d8e8f0}.tool .tool-icon{width:44px;height:44px;border-radius:17px;background:linear-gradient(145deg,#fff4db,#ffc84a);margin:0 auto 3px;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 16px rgba(0,0,0,.25)}.tool img{width:27px;height:27px}.game-bottom{background:rgba(255,255,255,.97)}.game-bottom .nav-item{color:#8490a1}.tutorial-pointer{position:absolute;z-index:90;width:52px;height:72px;border-radius:26px 26px 20px 20px;background:linear-gradient(#fff,#ffd8bd);border:3px solid #f0642f;right:118px;top:384px;transform:rotate(-25deg);box-shadow:0 8px 25px rgba(0,0,0,.25)}.tutorial-note{position:absolute;z-index:90;left:36px;right:36px;bottom:128px;background:#fff9f1;color:var(--text);border-radius:22px;padding:16px;text-align:center;box-shadow:var(--shadow)}
.chart{height:165px;background:linear-gradient(180deg,#102A4C,#173B66);border-radius:18px;position:relative;overflow:hidden;padding:16px;color:#fff}.chart svg{position:absolute;left:12px;right:12px;bottom:20px;width:calc(100% - 24px);height:100px}.chart .price{font-size:28px;font-weight:900}.chart .up{font-size:11px;color:#8af0e5}.order-card{background:#fff;border:1px solid var(--border);border-radius:17px;padding:13px;margin-top:9px}.order-card .price{font-size:19px;font-weight:900;color:var(--primary-deep)}.order-card .meta{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);margin-top:8px}
/* admin */
.admin-shell{width:1440px;height:900px;background:#f2f5f8;display:grid;grid-template-columns:232px 1fr;overflow:hidden;color:#182335}.admin-sidebar{background:linear-gradient(180deg,#07111F,#102A4C);color:#c6d7e3;padding:24px 16px}.admin-brand{display:flex;align-items:center;gap:12px;color:#fff;font-size:20px;font-weight:900;margin:0 8px 28px}.admin-brand img{width:42px;height:42px;border-radius:12px}.side-group{font-size:10px;text-transform:uppercase;color:#6f8ca3;margin:20px 12px 8px;letter-spacing:1.2px}.side-item{height:43px;border-radius:12px;display:flex;align-items:center;gap:11px;padding:0 12px;font-size:13px;font-weight:700;margin:3px 0}.side-item img{width:19px;height:19px;filter:brightness(0) invert(1);opacity:.7}.side-item.active{background:rgba(39,213,196,.16);color:#fff}.side-item.active img{opacity:1}.admin-main{display:flex;flex-direction:column;overflow:hidden}.admin-topbar{height:70px;background:#fff;border-bottom:1px solid #e3e8ee;display:flex;align-items:center;justify-content:space-between;padding:0 28px}.crumb{font-size:13px;color:#768297}.admin-user{display:flex;gap:10px;align-items:center;font-size:12px;font-weight:800}.admin-avatar{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--gold))}.admin-content{padding:24px 28px;overflow:hidden;flex:1}.admin-title{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px}.admin-title h1{font-size:24px;margin:0 0 5px}.admin-title p{font-size:12px;color:#7b879a;margin:0}.admin-btn{height:38px;padding:0 16px;border-radius:10px;border:0;background:var(--space-900);color:#fff;font-size:12px;font-weight:800}.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.kpi{background:#fff;border:1px solid #e1e7ee;border-radius:16px;padding:18px;box-shadow:0 8px 20px rgba(16,42,76,.05)}.kpi-label{font-size:11px;color:#7c8799}.kpi-value{font-size:28px;font-weight:900;margin:8px 0}.kpi-delta{font-size:10px;color:var(--success)}.admin-grid{display:grid;grid-template-columns:1.7fr 1fr;gap:16px;margin-top:16px}.panel{background:#fff;border:1px solid #e1e7ee;border-radius:16px;padding:18px;overflow:hidden}.panel-title{display:flex;justify-content:space-between;align-items:center;font-size:14px;font-weight:900;margin-bottom:14px}.filter-bar{height:62px;background:#fff;border:1px solid #e1e7ee;border-radius:14px;padding:11px;display:flex;align-items:center;gap:10px;margin-bottom:14px}.admin-input{height:38px;min-width:180px;border:1px solid #dfe5ec;border-radius:10px;padding:0 12px;color:#909aaa;font-size:11px;display:flex;align-items:center}.admin-select{height:38px;min-width:120px;border:1px solid #dfe5ec;border-radius:10px;padding:0 12px;color:#657083;font-size:11px;display:flex;align-items:center;justify-content:space-between}.data-table{width:100%;border-collapse:collapse;background:#fff;border-radius:14px;overflow:hidden;border:1px solid #e1e7ee}.data-table th{height:44px;background:#f7f9fb;text-align:left;padding:0 14px;font-size:10px;color:#758095}.data-table td{height:54px;padding:0 14px;border-top:1px solid #edf0f4;font-size:11px}.status-pill{height:24px;padding:0 9px;border-radius:12px;background:#e7f8ef;color:#16885a;display:inline-flex;align-items:center;font-weight:800;font-size:9px}.status-pill.warn{background:#fff3dd;color:#a96a00}.status-pill.error{background:#ffe8e8;color:#bd3535}.admin-form-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.admin-field label{font-size:11px;font-weight:800;display:block;margin-bottom:7px}.admin-field .control{height:42px;border:1px solid #dfe5ec;border-radius:10px;padding:0 12px;display:flex;align-items:center;color:#7c8797;font-size:11px}.switch{width:42px;height:23px;border-radius:12px;background:#dce3ea;padding:3px}.switch.on{background:var(--energy)}.switch:after{content:"";display:block;width:17px;height:17px;border-radius:50%;background:#fff}.switch.on:after{margin-left:19px}.admin-board{display:grid;grid-template-columns:repeat(4,92px);gap:10px;padding:16px;border-radius:16px;background:#102A4C;width:max-content}.admin-slot{width:92px;height:92px;border-radius:14px;background:rgba(255,255,255,.08);display:flex;align-items:center;justify-content:center}.admin-slot img{width:75px;height:75px}.health-row{display:grid;grid-template-columns:1.4fr .8fr .8fr 1fr;align-items:center;height:58px;border-bottom:1px solid #edf0f4;font-size:11px}.health-dot{width:9px;height:9px;border-radius:50%;background:var(--success);display:inline-block;margin-right:7px}.admin-overlay{position:absolute;inset:0;background:rgba(7,17,31,.55);display:flex;align-items:center;justify-content:center;z-index:100}.admin-modal{width:440px;background:#fff;border-radius:20px;padding:26px;box-shadow:0 30px 70px rgba(0,0,0,.25);text-align:center}
/* H5 */
.h5-shell{width:390px;height:844px;overflow:hidden;background:#fff9f1;margin:0 auto;position:relative}.h5-hero{height:410px;background:linear-gradient(160deg,#07111F,#173B66);color:#fff;padding:38px 24px;position:relative;overflow:hidden}.h5-hero:after{content:"";position:absolute;width:330px;height:330px;border-radius:50%;border:2px solid rgba(39,213,196,.25);right:-110px;bottom:-140px}.h5-logo{width:94px;height:94px;border-radius:25px}.h5-hero h1{font-size:30px;margin:18px 0 8px}.h5-hero p{font-size:13px;line-height:1.7;color:#c9e0ea}.h5-card{margin:-50px 16px 0;background:#fff;border-radius:24px;padding:20px;position:relative;z-index:2;box-shadow:var(--shadow)}
'''


def write(path: Path, text: str):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8')


def icon(icon_id, cls=''):
    return f'<img class="{cls}" src="../../07_GAME_ASSETS/objects/icons/{icon_id}.svg" alt="">'


def statusbar(dark=False):
    return f'<div class="statusbar {"dark" if dark else ""}"><span>11:29</span><span class="status-icons"><i class="dot-signal"></i><span>5G</span><span>▰ 89%</span></span></div>'


def topbar(title, dark=False, back=True, right=''):
    left=f'<button class="icon-btn">{icon("ICON-ACTION-BACK")}</button>' if back else '<div></div>'
    if right=='search': right_html=f'<button class="icon-btn">{icon("ICON-ACTION-SEARCH")}</button>'
    elif right=='settings': right_html=f'<button class="icon-btn">{icon("ICON-ACTION-SETTINGS")}</button>'
    elif right=='more': right_html=f'<button class="icon-btn">{icon("ICON-ACTION-MORE")}</button>'
    else: right_html='<div></div>'
    return f'<div class="topbar {"dark" if dark else ""}">{left}<h1>{html.escape(title)}</h1>{right_html}</div>'


def bottom_nav(active):
    items=[('home','ICON-NAV-HOME','首页'),('project','ICON-NAV-PROJECT','项目'),('mall','ICON-NAV-MALL','商城'),('discover','ICON-NAV-DISCOVER','发现'),('me','ICON-NAV-ME','我的')]
    return '<div class="bottom-nav game-bottom">'+''.join(f'<div class="nav-item {"active" if key==active else ""}">{icon(ic)}<span>{name}</span></div>' for key,ic,name in items)+'</div>'


def asset_strip():
    return f'''<div class="asset-strip">
      <div class="asset-box star">{icon('ICON-STAR-POINT')}<div class="label">星矿值</div><div class="value">12,860.45</div></div>
      <div class="asset-box energy">{icon('ICON-ENERGY-CHIP')}<div class="label">能源芯片</div><div class="value">6,430.20</div></div>
      <div class="asset-box cash">{icon('ICON-CASH')}<div class="label">账户余额</div><div class="value">¥ 28.60</div></div>
    </div>'''


def list_rows(items):
    out='<div class="card">'
    for title,sub,ic,val in items:
        out+=f'<div class="list-row"><div class="row-icon">{icon(ic)}</div><div class="row-main"><div class="row-title">{title}</div><div class="row-sub">{sub}</div></div><div class="row-value">{val}</div>{icon("ICON-CHEVRON-RIGHT","chevron")}</div>'
    return out+'</div>'


def form_page(title, fields, button='确认提交', note='信息仅用于当前业务处理'):
    body=''
    for label,placeholder,ic in fields:
        body+=f'<div class="form-label">{label}</div><div class="input">{icon(ic)}<span>{placeholder}</span></div>'
    body+=f'<p class="form-help">{note}</p><button class="btn primary full">{button}</button>'
    return body


def game_home(state='DEFAULT', tutorial=False):
    slots=[]
    miners=[1,1,2,3,4,4,5,6,7,8,9,10]
    if state=='NEW_USER': miners=[1,None,None,None,None,None,None,None,None,None,None,None]
    for i in range(16):
        if i>=12:
            slots.append('<div class="slot locked"></div>')
        else:
            lv=miners[i] if i<len(miners) else None
            if lv:
                slots.append(f'<div class="slot"><img class="miner" src="../../06_MINERS/PNG/MINER_L{lv:02d}.png"><span class="level-tag">Lv.{lv}</span></div>')
            else: slots.append('<div class="slot"></div>')
    bubble='<div class="claim-bubble">+ 36.80</div>' if state in ('CLAIMABLE','DEFAULT') else ''
    tut='''<div class="modal-backdrop"></div><div class="tutorial-pointer"></div><div class="tutorial-note"><b>拖动两台相同等级矿机</b><br><span style="font-size:11px;color:#68728A">重合后会自动合成更高等级矿机</span></div>''' if tutorial or state=='NEW_USER' else ''
    return f'''<div class="app-shell game-shell"><div class="game-bg"></div><div class="game-vignette"></div>{statusbar(True)}
      <div class="game-hud">
        <div class="hud-box">{icon('ICON-STAR-POINT')}<div><div class="hud-label">星矿值</div><div class="hud-value">12,860.45</div></div></div>
        <div class="hud-box">{icon('ICON-ENERGY-CHIP')}<div><div class="hud-label">能源芯片</div><div class="hud-value">6,430.20</div></div></div>
        <div class="hud-box">{icon('ICON-LEVEL')}<div><div class="hud-label">最高矿机</div><div class="hud-value">Lv.10</div></div></div>
      </div>
      <div class="mine-stage"><div class="rate-pill">每小时产出 5,482.36</div><div class="board">{''.join(slots)}</div>{bubble}</div>
      <div class="game-tools"><div class="tool"><div class="tool-icon">{icon('ICON-MINER-STORE')}</div>矿机商店</div><div class="tool"><div class="tool-icon">{icon('ICON-WAREHOUSE')}</div>仓库</div><div class="tool"><div class="tool-icon">{icon('ICON-ATLAS')}</div>图鉴</div><div class="tool"><div class="tool-icon">{icon('ICON-TASK')}</div>任务</div><div class="tool"><div class="tool-icon">{icon('ICON-BOX')}</div>补给箱</div></div>
      {bottom_nav('home')}{tut}</div>'''


def miner_grid(mode='store'):
    items=[]
    levels=[1,2,3,4,5,6,7,8]
    for lv in levels:
        if mode=='warehouse' and lv>5: locked=True
        else: locked=False
        price=f'{2.2**(lv-1):,.0f}'
        items.append(f'''<div class="product"><div style="height:100px;background:linear-gradient(145deg,#102A4C,#173B66);display:flex;align-items:center;justify-content:center"><img style="width:90px;height:90px;object-fit:contain" src="../../06_MINERS/PNG/MINER_L{lv:02d}.png"></div><div class="product-body"><div class="product-name">{['初级钻探机','双钻采矿机','履带采矿车','蒸汽钻井机','磁力采集机','重型碎岩机','自动矿车','齿轮钻塔'][lv-1]}</div><div class="product-sub">Lv.{lv} · 每小时 {0.05*(2.05**(lv-1)):.2f}</div><div class="product-price">{price} 星矿值</div></div></div>''')
    return '<div class="product-grid">'+''.join(items)+'</div>'


def project_cards(count=3):
    badges=[('<span class="badge headline">头条</span><span class="badge pin">置顶</span>','AI工具推广计划'),('<span class="badge headline">头条</span>','本地商家联合推广'),('<span class="badge refresh">刚刚刷新</span>','创业项目资源对接')]
    out=''
    for i in range(count):
        b,t=badges[i%len(badges)]
        out+=f'''<div class="project-card"><div class="project-cover"><div class="cover-title">{t}</div></div><div class="chips" style="margin-top:9px">{b}<span class="badge member">星耀会员</span></div><div class="project-title">{t} · 真实项目展示</div><div class="project-desc">包含项目介绍、图文素材、联系方式和安全提示，浏览任务在详情页内轻量显示。</div><div class="project-meta"><span>UID 2026 · 12分钟前</span><span>任务奖励 2.00</span></div></div>'''
    return out


def state_layer(state, platform='app'):
    if state in ('DEFAULT','NEW_USER','CLAIMABLE','TASK_RUNNING'): return ''
    if platform=='admin':
        if state=='EMPTY': return '<div class="admin-overlay"><div class="admin-modal"><div class="empty-orbit"></div><h2>暂无待处理数据</h2><p style="color:#7c8797">筛选条件下没有符合记录</p></div></div>'
        return '<div class="admin-overlay"><div class="admin-modal"><div class="modal-icon" style="background:#ffe8e8;margin:auto">'+icon('ICON-REPORT')+'</div><h2>服务数据加载失败</h2><p style="color:#7c8797">保留当前筛选和页面内容，可手动重试。</p><button class="admin-btn">重新加载</button></div></div>'
    data={
      'ERROR':('ICON-REPORT','加载失败','已保留当前页面内容，请检查网络后重试。','重新加载','error'),
      'SUBMITTING':('ICON-CLOCK','正在提交','请勿重复操作，服务端正在校验并处理。','','processing'),
      'BOARD_FULL':('ICON-WAREHOUSE','棋盘已满','请先合成、整理或将矿机移入仓库。','打开仓库','warning'),
      'OFFLINE_BY_ADMIN':('ICON-REPORT','项目已下架','该项目暂时无法查看联系方式和任务奖励。','返回列表','error'),
      'PROCESSING':('ICON-CLOCK','处理中','正在通过服务端确认最终状态，请保持页面。','','processing'),
      'SUCCESS':('ICON-CHECK','操作成功','服务端状态和资产已经完成更新。','完成','success'),
      'FAILURE':('ICON-REPORT','操作失败','本次业务未生效，未重复扣减资产。','重新尝试','error'),
      'EXPIRED':('ICON-CLOCK','订单已过期','当前订单已关闭，请返回商品页重新创建。','返回商城','warning'),
      'UPLOADING':('ICON-UPLOAD','正在上传付款截图','上传完成前不得提交人工审核。','','processing'),
      'REVIEW_PENDING':('ICON-CLOCK','已提交人工审核','财务管理员核对后会通过站内消息通知。','查看订单','success'),
      'REJECTED':('ICON-REPORT','付款审核未通过','请根据拒绝原因重新上传清晰的付款凭证。','重新上传','error'),
      'PERMISSION_DENIED':('ICON-CAMERA','未获得相机权限','需要前置摄像头完成实名动作采集，可前往系统设置授权。','前往设置','warning'),
      'VERIFYING':('ICON-IDENTITY','正在核验身份','已完成静默上传，正在等待人证比对结果。','','processing'),
      'RECAPTURE':('ICON-CAMERA','需要重新采集','当前媒体质量不足，请在光线充足环境重新完成动作。','重新采集','warning'),
      'DISABLED':('ICON-LOCK','暂不可提现','请先完成实名认证并绑定支付宝收款账号。','去完善','warning'),
      'TASK_SUCCESS':('ICON-CHECK','浏览任务完成','奖励已自动发放至星矿值账户，无需再次点击领取。','继续浏览','success'),
    }
    if state not in data:return ''
    ic,title,desc,btn,kind=data[state]
    if kind=='processing':
        return f'<div class="modal-backdrop"><div class="modal"><div class="spinner"></div><h2>{title}</h2><p>{desc}</p></div></div>'
    color={'error':'#ffe8e8','warning':'#fff3dd','success':'#e5f8ef'}.get(kind,'#fff0df')
    return f'<div class="modal-backdrop"><div class="modal"><div class="modal-icon" style="background:{color}">{icon(ic)}</div><h2>{title}</h2><p>{desc}</p>{f"<button class=\"btn primary full\">{btn}</button>" if btn else ""}</div></div>'


def generic_app(page,state):
    pid=page['page_id']; title=page['name_cn']; t=page['template']; m=page['module']
    if t=='splash':
        return f'''<div class="app-shell" style="background:#07111F url('../../05_BRAND/android_splash_1080x2400.png') center/cover no-repeat"></div>'''
    if t=='game_home': return game_home(state)
    if t=='game_tutorial': return game_home('NEW_USER',True)
    if t in ('auth_login','auth_register'):
        fields=[('邮箱','输入邮箱地址','ICON-MAIL')]
        if t=='auth_login': fields+=[('登录密码','输入登录密码','ICON-LOCK')]
        else: fields+=[('邮箱验证码','6位验证码','ICON-CHECK'),('登录密码','8~32位字母与数字','ICON-LOCK'),('邀请码（选填）','默认等于邀请人UID','ICON-INVITE')]
        content=f'''<div class="hero"><div class="eyebrow">XKJY ACCOUNT</div><h2>{'欢迎回到星矿纪元' if t=='auth_login' else '创建你的星际矿场'}</h2><p>使用邮箱完成安全认证，注册后自动初始化钱包、UID和第一台矿机。</p></div><div style="margin-top:14px">{form_page(title,fields,'登录' if t=='auth_login' else '注册并进入矿场','提交前将弹出自研图形安全验证码')}</div>'''
        shell=f'<div class="app-shell">{statusbar()}{topbar(title,back=False)}<div class="page-content scroll">{content}</div>{state_layer(state)}</div>'
        return shell
    if t in ('captcha','email_verify','pin'):
        base=generic_app({'page_id':'APP-AUTH-001','name_cn':'登录页','module':'account','template':'auth_login'},'DEFAULT')
        if t=='captcha':
            modal='''<div class="modal-backdrop"><div class="modal"><h2>安全验证</h2><p>请输入图中字符后继续原业务，表单内容不会丢失。</p><div style="height:74px;border-radius:16px;background:repeating-linear-gradient(120deg,#102A4C,#102A4C 18px,#173B66 18px,#173B66 36px);display:flex;align-items:center;justify-content:center;color:#fff;font-size:30px;font-weight:900;letter-spacing:8px">7K9PX</div><div class="input" style="margin:14px 0">输入验证码</div><button class="btn primary full">验证并继续</button></div></div>'''
        elif t=='email_verify': modal='''<div class="modal-backdrop"><div class="modal"><div class="modal-icon">'''+icon('ICON-MAIL')+'''</div><h2>邮箱安全验证</h2><p>验证码已发送至 c***@example.com，有效期5分钟。</p><div class="input">输入6位验证码</div><button class="btn primary full" style="margin-top:14px">确认验证</button></div></div>'''
        else: modal='''<div class="modal-backdrop"><div class="modal"><div class="modal-icon">'''+icon('ICON-LOCK')+'''</div><h2>输入赠送密码</h2><p>6位独立安全密码，不与登录密码共用。</p><div style="display:flex;justify-content:center;gap:10px;margin:18px 0">'''+''.join('<span style="width:38px;height:46px;border:1px solid #E8DFD3;border-radius:12px;display:flex;align-items:center;justify-content:center">•</span>' for _ in range(6))+'''</div><button class="btn primary full">确认赠送</button></div></div>'''
        return base.replace('</div></div>', '</div></div>',1)+modal
    if t in ('status','update','download','result','payment_result','withdraw_result','identity_result'):
        ic='ICON-CHECK'; heading=title; desc='系统已完成状态确认，页面仅展示服务端最终结果。'
        if t=='status': ic='ICON-SETTINGS' if False else 'ICON-SETTINGS'; heading='系统维护中'; desc='当前正在进行短时维护，已有数据不会受到影响。'
        body=f'<div class="empty-state"><div class="modal-icon">{icon(ic)}</div><h3>{heading}</h3><p>{desc}</p><button class="btn primary full">返回首页</button></div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div>{state_layer(state)}</div>'
    if t=='update':
        body=f'<div class="hero"><div class="eyebrow">VERSION 1.1.0</div><h2>发现新版本</h2><p>包含矿机动画优化、支付稳定性和页面状态恢复修复。</p></div>'+list_rows([('版本大小','42.8 MB','ICON-DOWNLOAD',''),('更新方式','应用内安全下载','ICON-SECURITY',''),('发布时间','2026-08-16','ICON-CALENDAR','')])+'<button class="btn primary full" style="margin-top:14px">立即更新</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t=='article' or t=='legal':
        body='<div class="card"><h3 style="margin-top:0">星矿纪元用户协议</h3>'+''.join(f'<p style="font-size:12px;line-height:1.8;color:#5f687b"><b>{i}. 条款标题</b><br>本页面展示完整协议正文、版本号和生效时间，支持长列表滚动并保持阅读位置。</p>' for i in range(1,8))+'</div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='miner_store':
        body=asset_strip()+'<div class="section-title"><h3>可直接购买等级</h3><span>最高等级 - 4</span></div>'+miner_grid('store')
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div>{state_layer(state)}</div>'
    if t=='warehouse':
        body='<div class="hero"><div class="eyebrow">WAREHOUSE 8 / 24</div><h2>矿机仓库</h2><p>仓库内矿机不参与生产，可移动回棋盘继续运行。</p></div><div class="section-title"><h3>已存矿机</h3><span>自动整理</span></div>'+miner_grid('warehouse')
        return f'<div class="app-shell">{statusbar()}{topbar(title,right="more")}<div class="page-content scroll">{body}</div></div>'
    if t=='atlas':
        rows=''.join(f'<div class="list-row"><div class="row-icon blue" style="width:56px;height:56px"><img style="width:50px;height:50px" src="../../06_MINERS/PNG/MINER_L{i:02d}.png"></div><div class="row-main"><div class="row-title">Lv.{i} {['初级钻探机','双钻采矿机','履带采矿车','蒸汽钻井机','磁力采集机','重型碎岩机'][i-1]}</div><div class="row-sub">每小时产出 {0.05*(2.05**(i-1)):.4f} 星矿值</div></div><span class="badge success">已解锁</span></div>' for i in range(1,7))
        body='<div class="segmented"><span class="active">原始采矿</span><span>机械工业</span><span>智能矿业</span></div><div class="card" style="margin-top:12px">'+rows+'</div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='miner_detail':
        body=f'<div class="hero" style="text-align:center"><img src="../../06_MINERS/PNG/MINER_L18.png" style="width:180px;height:180px;object-fit:contain"><div class="eyebrow">SMART MINING ERA</div><h2>Lv.18 智能矿业中枢</h2><p>首次获得于 2026-08-16 11:29</p></div><div class="metric-grid" style="margin-top:12px"><div class="metric"><div class="label">每小时产出</div><div class="value">9,624.80</div></div><div class="metric"><div class="label">当前拥有</div><div class="value">1 台</div></div></div><button class="btn secondary full" style="margin-top:12px">锁定矿机</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t in ('offline_reward','unlock','unlock_slot','supply_box','confirm'):
        base=game_home('DEFAULT')
        if t=='offline_reward': modal=f'<div class="modal-backdrop"><div class="modal dark"><div class="modal-icon">{icon("ICON-STAR-POINT")}</div><h2>离线收益</h2><p>离线 7小时 42分钟，累计产生 3,860.45 星矿值。</p><button class="btn primary full">领取全部收益</button></div></div>'
        elif t=='unlock': modal=f'<div class="modal-backdrop"><div class="modal dark"><img src="../../06_MINERS/PNG/MINER_L24.png" style="width:180px;height:180px"><h2>解锁 Lv.24 等离子矿业站</h2><p>图鉴已点亮，并获得首次解锁奖励。</p><button class="btn primary full">收入矿场</button></div></div>'
        elif t=='unlock_slot': modal=f'<div class="modal-backdrop"><div class="modal"><div class="modal-icon">{icon("ICON-LOCK")}</div><h2>解锁第13格</h2><p>最高矿机达到 Lv.8 后永久开放该棋盘格。</p><button class="btn primary full">立即解锁</button></div></div>'
        elif t=='supply_box': modal=f'<div class="modal-backdrop"><div class="modal dark"><div style="font-size:100px">◇</div><h2>星际补给箱</h2><p>服务端已经确定掉落结果，点击播放开箱动画。</p><button class="btn primary full">开启补给</button></div></div>'
        else: modal=f'<div class="modal-backdrop"><div class="modal"><div class="modal-icon">{icon("ICON-RECYCLE")}</div><h2>{title}</h2><p>本操作不可撤回，服务端确认后再更新棋盘与资产。</p><button class="btn primary full">确认操作</button></div></div>'
        return base+modal
    if t=='task_list':
        body='<div class="hero"><div class="eyebrow">DAILY MISSION</div><h2>今日矿场任务</h2><p>完成行为后由服务端更新进度，奖励需主动领取。</p></div>'+list_rows([('领取矿机收益','2 / 3 次','ICON-STAR-POINT','+1.00'),('完成矿机合成','3 / 3 次','ICON-MINER','领取'),('购买矿机','1 / 2 台','ICON-MINER-STORE','+1.00'),('完成项目浏览任务','0 / 2 个','ICON-TASK','+2.00')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='signin':
        days=''.join(f'<div style="height:92px;border-radius:16px;background:{"#fff0df" if i==3 else "#fff"};border:1px solid #E8DFD3;display:flex;flex-direction:column;align-items:center;justify-content:center"><b>第{i}天</b><span style="font-size:10px;color:#68728A;margin-top:7px">{i*2} 芯片</span></div>' for i in range(1,8))
        body='<div class="hero"><div class="eyebrow">7-DAY SIGN IN</div><h2>连续签到赢补给</h2><p>漏签不自动补签，完成七日后开启新一轮。</p></div><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-top:14px">'+days+'</div><button class="btn primary full" style="margin-top:14px">领取第3天奖励</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t=='ranking':
        body='<div class="segmented"><span class="active">最高等级</span><span>累计产出</span><span>今日产出</span></div>'+list_rows([(f'{i}. 星矿玩家{2025+i}',f'UID {2025+i} · 最高 Lv.{37-i}','ICON-RANK',f'{982-i*21}M') for i in range(1,8)])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='ledger':
        body=asset_strip()+list_rows([('矿机产出领取','今天 11:28','ICON-STAR-POINT','+36.8000'),('浏览任务奖励','今天 10:16','ICON-TASK','+2.0000'),('购买 Lv.4 矿机','昨天 22:45','ICON-MINER-STORE','-10.6480'),('一级积分提成','昨天 19:22','ICON-USERS','+1.2400'),('兑换能源芯片','08-14 09:10','ICON-EXCHANGE','-100.0000')])
        return f'<div class="app-shell">{statusbar()}{topbar(title,right="search")}<div class="page-content scroll">{body}</div></div>'
    if t in ('project_feed','project_list'):
        body='<div class="input">'+icon('ICON-ACTION-SEARCH')+'<span>搜索项目标题或简介</span></div><div class="chips" style="margin:12px 0"><span class="chip active">推荐</span><span class="chip">AI工具</span><span class="chip">本地服务</span><span class="chip">创业项目</span></div>'+project_cards(4)
        return f'<div class="app-shell">{statusbar()}{topbar(title,back=False if t=="project_feed" else True,right="search")}<div class="page-content with-bottom scroll">{body}</div>{bottom_nav("project") if t=="project_feed" else ""}{state_layer(state)}</div>'
    if t=='search':
        body='<div class="input">'+icon('ICON-ACTION-SEARCH')+'<span>AI 工具</span></div><div class="section-title"><h3>搜索结果</h3><span>28个项目</span></div>'+project_cards(4)
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t in ('project_form','report_form','market_form','feedback','profile_form','alipay_bind','pin_setup'):
        configs={
        'project_form':[('项目标题','5~40字','ICON-PROJECT' if False else 'ICON-EDIT'),('项目简介','10~120字','ICON-EDIT'),('项目链接（选填）','https://','ICON-LINK'),('联系方式','微信/QQ/电话/邮箱','ICON-CONTACT')],
        'report_form':[('举报类型','选择举报原因','ICON-REPORT'),('问题说明','请描述具体问题','ICON-EDIT'),('证据图片','最多3张','ICON-IMAGE')],
        'market_form':[('求购数量','输入星矿值数量','ICON-STAR-POINT'),('求购单价','输入单价','ICON-CASH'),('联系方式','微信/QQ/电话','ICON-CONTACT'),('备注','0~200字','ICON-EDIT')],
        'feedback':[('问题类型','选择类型','ICON-HELP'),('反馈内容','请详细描述','ICON-EDIT'),('问题截图','最多3张','ICON-IMAGE')],
        'profile_form':[('昵称','星矿玩家2026','ICON-USER'),('头像','上传新头像','ICON-IMAGE')],
        'alipay_bind':[('实名姓名','陈*（自动读取）','ICON-IDENTITY'),('支付宝账号','输入支付宝账号','ICON-PAY-ALIPAY'),('邮箱验证码','6位验证码','ICON-MAIL')],
        'pin_setup':[('邮箱验证码','6位验证码','ICON-MAIL'),('新赠送密码','6位数字','ICON-LOCK'),('确认赠送密码','再次输入','ICON-LOCK')],}
        body=form_page(title,configs[t],'保存并提交' if t!='alipay_bind' else '确认绑定','所有关键字段由后端再次校验')
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='image_manager':
        tiles=''.join(f'<div style="height:105px;border-radius:16px;background:linear-gradient(135deg,#173B66,#27D5C4);position:relative"><span style="position:absolute;right:7px;top:7px;width:24px;height:24px;border-radius:12px;background:#fff;display:flex;align-items:center;justify-content:center">×</span></div>' for _ in range(5))
        body='<div class="hero"><h2>项目图片</h2><p>最多8张，支持拖动排序。文件对象先上传R2，再绑定项目草稿。</p></div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:14px">'+tiles+'<div style="height:105px;border-radius:16px;border:2px dashed #cbd3dc;display:flex;align-items:center;justify-content:center">'+icon('ICON-UPLOAD')+'</div></div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t=='project_detail':
        progress='<div style="position:absolute;top:86px;left:16px;right:16px;height:34px;border-radius:17px;background:rgba(7,17,31,.9);color:#fff;z-index:10;display:flex;align-items:center;padding:0 12px;font-size:10px"><span style="flex:1">浏览任务进行中</span><b>12 / 20 秒</b></div>' if state=='TASK_RUNNING' else ''
        body=f'''<div class="project-cover" style="height:180px"><div class="cover-title">AI 创作工具推广计划</div></div><div class="chips" style="margin:12px 0"><span class="badge headline">头条</span><span class="badge pin">置顶</span><span class="badge member">星耀会员</span></div><h2 style="font-size:20px;margin:0 0 8px">AI 创作工具推广计划</h2><p style="font-size:12px;line-height:1.75;color:#5f687b">这是统一项目详情页，完整展示项目介绍、图片、链接、联系方式、安全提示和浏览任务。任务进度不会遮挡正文。</p><div class="section-title"><h3>项目图片</h3><span>1 / 4</span></div><div style="height:150px;border-radius:18px;background:linear-gradient(135deg,#102A4C,#27D5C4)"></div><div class="card" style="margin-top:12px"><b>安全提示</b><p style="font-size:11px;color:#68728A;line-height:1.6">请自行判断外部项目风险，平台不要求向陌生人转账。</p></div><div style="display:flex;gap:10px;margin-top:12px"><button class="btn secondary" style="flex:1">收藏</button><button class="btn primary" style="flex:2">获取联系方式</button></div>'''
        return f'<div class="app-shell">{statusbar()}{topbar(title,right="more")}<div class="page-content scroll">{body}</div>{progress}{state_layer(state)}</div>'
    if t=='contact_sheet':
        base=generic_app({'page_id':'APP-PROJ-006','name_cn':'项目详情','module':'project','template':'project_detail'},'DEFAULT')
        modal=f'<div class="modal-backdrop" style="align-items:flex-end;padding:0"><div class="modal" style="border-radius:28px 28px 0 0;text-align:left"><h2>联系方式与链接</h2>{list_rows([("微信","xingkuang2026","ICON-CONTACT","复制"),("项目链接","xkjy.example/project","ICON-LINK","打开")])}<p style="font-size:10px;color:#68728A">打开外部链接前将再次显示目标域名和安全提示。</p></div></div>'
        return base+modal
    if t=='project_manage':
        body='<div class="hero"><div class="eyebrow">PROJECT STATUS</div><h2>AI创作工具推广计划</h2><p>已发布 · 头条剩余 18小时32分 · 置顶剩余 18小时32分</p></div><div class="metric-grid" style="margin-top:12px"><div class="metric"><div class="label">浏览量</div><div class="value">1,268</div></div><div class="metric"><div class="label">联系方式获取</div><div class="value">86</div></div></div>'+list_rows([('使用推广卡','头条、置顶或刷新','ICON-HEADLINE',''),('创建浏览任务','按人数和单人奖励购买预算','ICON-TASK',''),('编辑项目','修改后重新提交审核','ICON-EDIT',''),('下架项目','暂停展示和任务','ICON-REPORT','')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t in ('promotion_apply','task_budget'):
        body='<div class="hero"><div class="eyebrow">PROMOTION</div><h2>'+title+'</h2><p>权益只能绑定本人已发布项目，服务端完成库存和状态校验后生效。</p></div>'+list_rows([('头条卡','24小时头条展示','ICON-HEADLINE','2张'),('置顶卡','24小时置顶展示','ICON-PIN','3张'),('刷新卡','单次刷新并获得优先期','ICON-REFRESH','5张')])+'<button class="btn primary full" style="margin-top:14px">确认使用</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='gallery':
        return f'<div class="app-shell" style="background:#07111F">{statusbar(True)}{topbar(title,True)}<div style="height:720px;display:flex;align-items:center;justify-content:center"><div style="width:350px;height:480px;border-radius:24px;background:linear-gradient(135deg,#173B66,#27D5C4)"></div></div></div>'
    if t=='category_picker':
        body=list_rows([('综合','系统默认分类','ICON-PROJECT' if False else 'ICON-ORGANIZE','已选'),('AI工具','后台配置','ICON-CHART',''),('本地服务','后台配置','ICON-PROJECT' if False else 'ICON-STORE',''),('创业项目','后台配置','ICON-INVITE','')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t=='mall_home':
        products=''.join(f'<div class="product"><img src="../../07_GAME_ASSETS/cards/{code}.png"><div class="product-body"><div class="product-name">{name}</div><div class="product-sub">虚拟权益 · 服务端自动发放</div><div class="product-price">{price}</div></div></div>' for code,name,price in [('member_card','星耀会员','¥ 99.00'),('headline_card','头条卡','20 星矿值'),('pin_card','置顶卡','16 星矿值'),('refresh_card','刷新卡','8 星矿值'),('red_packet_card','福利红包卡','活动限定'),('headline_card','浏览任务预算','¥ 10 起')])
        body=asset_strip()+'<div class="chips" style="margin:12px 0"><span class="chip active">推荐</span><span class="chip">会员</span><span class="chip">推广服务</span><span class="chip">游戏权益</span></div><div class="product-grid">'+products+'</div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title,back=False,right="search")}<div class="page-content with-bottom scroll">{body}</div>{bottom_nav("mall")}</div>'
    if t=='product_detail':
        body='<img src="../../07_GAME_ASSETS/cards/headline_card.png" style="width:100%;border-radius:22px"><h2 style="font-size:21px">头条卡</h2><p style="font-size:12px;color:#68728A;line-height:1.7">使用后项目在推荐信息流获得24小时头条权益，可与置顶同时生效。</p><div class="card"><div class="list-row"><b>普通价格</b><span style="margin-left:auto">40 星矿值 + 80 芯片</span></div><div class="list-row"><b>会员价格</b><span style="margin-left:auto;color:#F0642F">20 星矿值 + 40 芯片</span></div></div><button class="btn primary full" style="margin-top:14px">立即购买</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t in ('order_confirm','checkout'):
        payment_methods=''.join(f'<div class="list-row"><div class="row-icon {cls}">{icon(ic)}</div><div class="row-main"><div class="row-title">{name}</div><div class="row-sub">{sub}</div></div><span style="width:20px;height:20px;border-radius:50%;border:2px solid #d4dbe3"></span></div>' for name,sub,ic,cls in [('支付宝','XApay在线支付','ICON-PAY-ALIPAY','blue'),('微信支付','XApay在线支付','ICON-PAY-WECHAT','green'),('账户余额','可用 ¥28.60','ICON-CASH','green'),('星矿值 + 能源芯片','仅限允许的虚拟商品','ICON-EXCHANGE','purple')])
        body=f'<div class="card"><div class="list-row"><div class="row-icon">{icon("ICON-HEADLINE")}</div><div class="row-main"><div class="row-title">头条卡 × 1</div><div class="row-sub">订单号 XK202608160001</div></div><b>¥ 10.00</b></div><div class="list-row"><span>会员优惠</span><span style="margin-left:auto;color:#24B878">- ¥10.00</span></div><div class="list-row"><b>应付金额</b><b style="margin-left:auto;font-size:22px;color:#F0642F">¥ 10.00</b></div></div><div class="section-title"><h3>选择支付方式</h3><span>剩余14:52</span></div><div class="card">{payment_methods}</div><button class="btn primary full" style="margin-top:14px">确认支付 ¥10.00</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div>{state_layer(state)}</div>'
    if t=='manual_qr':
        body=f'<div class="hero" style="text-align:center"><div class="eyebrow">MANUAL QR PAYMENT</div><h2>请使用微信扫码付款</h2><p>订单金额 ¥10.00 · 订单号 XK202608160001</p></div><div style="width:230px;height:230px;margin:18px auto;border:14px solid #fff;background:repeating-conic-gradient(#07111F 0 25%,#fff 0 50%) 0/22px 22px;box-shadow:var(--shadow)"></div><div class="card"><div class="list-row"><span>付款截图</span><span style="margin-left:auto;color:#F0642F">上传凭证</span></div><p style="font-size:10px;color:#68728A">付款后必须上传完整截图，审核通过后才发放权益。</p></div><button class="btn primary full" style="margin-top:12px">提交人工审核</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div>{state_layer(state)}</div>'
    if t=='order_list':
        body='<div class="segmented"><span class="active">全部</span><span>待支付</span><span>已完成</span><span>已关闭</span></div>'+list_rows([('头条卡 × 1','订单 XK202608160001 · 已完成','ICON-ORDER','¥10.00'),('星耀会员 1年','订单 XK202608150021 · 已完成','ICON-MEMBER','¥99.00'),('浏览任务预算','订单 XK202608140118 · 待支付','ICON-TASK','¥20.00')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='order_detail':
        body='<div class="hero"><div class="eyebrow">ORDER SETTLED</div><h2>订单已完成</h2><p>XK202608160001 · 支付和权益结算均已确认</p></div>'+list_rows([('商品','头条卡 × 1','ICON-HEADLINE',''),('支付方式','支付宝 · XApay','ICON-PAY-ALIPAY',''),('实付金额','会员五折','ICON-CASH','¥10.00'),('权益发放','虚拟背包 +1','ICON-BOX','已完成')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='inventory':
        body=list_rows([('头条卡','24小时头条权益','ICON-HEADLINE','2张'),('置顶卡','24小时置顶权益','ICON-PIN','3张'),('刷新卡','单次刷新','ICON-REFRESH','5张'),('星际补给箱','开箱获得积分或矿机','ICON-BOX','4个')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t=='membership':
        body='<div class="hero" style="background:linear-gradient(135deg,#8B5CFF,#ED5CBE)"><div class="eyebrow">STARLIGHT MEMBER</div><h2>星耀会员</h2><p>有效期至 2027-08-16 · 推广服务五折 · 专属标识</p></div>'+list_rows([('推广服务五折','头条、置顶和刷新卡','ICON-HEADLINE','已生效'),('项目会员标识','列表、详情和个人中心','ICON-MEMBER','已生效'),('会员主题装饰','后续可配置','ICON-LEVEL','已生效')])+'<button class="btn primary full" style="margin-top:14px">续费一年 ¥99</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t in ('discover','market'):
        body='<div class="segmented"><span class="active">集市</span><span>游戏</span></div><div class="chart" style="margin-top:12px"><div class="price">¥ 0.5368</div><div class="up">今日 +1.00%</div><svg viewBox="0 0 340 100"><polyline points="0,84 55,74 110,78 165,52 220,45 275,28 340,16" fill="none" stroke="#27D5C4" stroke-width="5"/><circle cx="340" cy="16" r="7" fill="#FFC84A"/></svg></div><div class="section-title"><h3>用户求购</h3><span>按单价从高到低</span></div>'+''.join(f'<div class="order-card"><div style="display:flex;justify-content:space-between"><b>求购 {5000-i*500:,} 星矿值</b><span class="badge success">有效</span></div><div class="price">¥ {0.59-i*.01:.2f} / 个</div><div class="meta"><span>UID {2025+i}</span><span>微信联系</span></div></div>' for i in range(1,5))
        return f'<div class="app-shell">{statusbar()}{topbar("发现",back=False)}<div class="page-content with-bottom scroll">{body}</div>{bottom_nav("discover")}</div>'
    if t in ('market_detail','market_list'):
        body='<div class="hero"><div class="eyebrow">POINT MARKET</div><h2>求购 4,500 星矿值</h2><p>求购单价 ¥0.58 · 预计总额 ¥2,610.00</p></div>'+list_rows([('发布者','星矿玩家2028 · UID 2028','ICON-USER',''),('联系方式','微信 · 确认后展示','ICON-CONTACT','查看'),('有效期','剩余6天18小时','ICON-CLOCK',''),('订单状态','正常展示','ICON-CHECK','有效')])+'<button class="btn primary full" style="margin-top:14px">查看联系方式</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='game_portal':
        body='<div class="hero"><div class="eyebrow">DISCOVER GAMES</div><h2>更多积分消耗玩法</h2><p>本期只保留入口，不开发未确认的额外小游戏。</p></div><div class="empty-state"><div class="empty-orbit"></div><h3>新玩法筹备中</h3><p>后续版本按独立功能文档和效果图增量加入。</p></div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t=='wallet_home':
        body=asset_strip()+'<div class="section-title"><h3>常用资产功能</h3></div>'+list_rows([('赠送星矿值','输入收款UID并确认','ICON-TRANSFER',''),('兑换能源芯片','消耗100获得50','ICON-EXCHANGE',''),('提现','固定档位支付宝提现','ICON-CASH',''),('资产流水','查看全部账本记录','ICON-WALLET','')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='transfer_form':
        body=asset_strip()+form_page(title,[('收款UID','输入纯数字UID','ICON-USER'),('赠送数量','输入星矿值','ICON-STAR-POINT')],'下一步','赠送1星矿值额外消耗2能源芯片')
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='recipient_confirm':
        body='<div class="hero" style="text-align:center"><div style="width:82px;height:82px;border-radius:50%;background:linear-gradient(135deg,#FF7A3D,#FFC84A);margin:auto"></div><h2>星矿玩家2038</h2><p>UID 2038 · 请确认收款人信息</p></div>'+list_rows([('赠送星矿值','100.0000','ICON-STAR-POINT',''),('能源芯片手续费','200.0000','ICON-ENERGY-CHIP',''),('到账数量','100.0000 星矿值','ICON-TRANSFER','')])+'<button class="btn primary full" style="margin-top:14px">输入赠送密码</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='exchange':
        body=asset_strip()+'<div class="hero" style="margin-top:14px"><div class="eyebrow">2 : 1 EXCHANGE</div><h2>星矿值兑换能源芯片</h2><p>消耗100星矿值，获得50能源芯片；只支持单向兑换。</p></div>'+form_page(title,[('消耗星矿值','100.0000','ICON-STAR-POINT')],'确认兑换','本次预计获得 50.0000 能源芯片')
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='invite_home':
        body='<div class="hero"><div class="eyebrow">INVITE CODE 2026</div><h2>邀请好友共建矿场</h2><p>一级和二级好友的可计提积分行为与现金推广消费分别计算提成。</p></div><div class="metric-grid" style="margin-top:12px"><div class="metric"><div class="label">一级好友</div><div class="value">18</div><div class="delta">积分提成10%</div></div><div class="metric"><div class="label">二级好友</div><div class="value">56</div><div class="delta">积分提成5%</div></div></div>'+list_rows([('邀请海报','二维码与邀请码2026','ICON-QR','生成'),('一级好友','查看注册时间和累计提成','ICON-USERS','18'),('二级好友','查看间接邀请用户','ICON-USERS','56'),('我的上级','查看绑定关系','ICON-INVITE','UID 2025')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='invite_poster':
        return f'<div class="app-shell" style="background:#07111F">{statusbar(True)}{topbar(title,True)}<div style="height:680px;display:flex;align-items:center;justify-content:center"><img src="../../05_BRAND/invite_poster_1080x1920.png" style="height:630px;border-radius:18px;box-shadow:var(--shadow)"></div><div style="padding:0 16px"><button class="btn primary full">保存海报到相册</button></div></div>'
    if t=='friend_list':
        body=list_rows([(f'星矿玩家{2026+i}',f'UID {2026+i} · 注册 2026-08-{16-i:02d}','ICON-USERS',f'+{i*2.4:.2f}') for i in range(1,8)])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='superior':
        body='<div class="hero" style="text-align:center"><div style="width:90px;height:90px;border-radius:50%;background:linear-gradient(135deg,#8B5CFF,#ED5CBE);margin:auto"></div><h2>星矿玩家2025</h2><p>UID 2025 · 绑定于 2026-08-16</p></div><div class="card" style="margin-top:14px"><p style="font-size:12px;line-height:1.7;color:#68728A">邀请关系绑定后普通用户不可修改；异常关系由后台审核并保留审计。</p></div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t=='identity_status':
        body='<div class="hero"><div class="eyebrow">IDENTITY VERIFICATION</div><h2>完成实名认证</h2><p>用于提高账户安全并满足提现前置条件。实名媒体静默上传且本地零留存。</p></div>'+list_rows([('认证姓名','未认证','ICON-IDENTITY',''),('身份证号','未提交','ICON-SECURITY',''),('活体动作','随机2个动作','ICON-CAMERA','')])+'<button class="btn primary full" style="margin-top:14px">开始认证</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='identity_form':
        body=form_page(title,[('真实姓名','输入姓名','ICON-USER'),('身份证号','输入身份证号码','ICON-IDENTITY')],'下一步：动作采集','信息加密保存，普通日志不记录完整字段')
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t=='permission':
        body='<div class="empty-state"><div class="modal-icon">'+icon('ICON-CAMERA')+'</div><h3>需要前置摄像头权限</h3><p>仅在动作采集页面启用；退出页面立即释放；照片和短视频不会保存到相册。</p><button class="btn primary full">允许并继续</button></div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t=='capture':
        body=f'<div style="height:610px;background:#07111F;border-radius:24px;position:relative;overflow:hidden"><div style="position:absolute;inset:65px 70px 150px;border:4px solid #27D5C4;border-radius:50% 50% 44% 44%;box-shadow:0 0 28px rgba(39,213,196,.45)"></div><div style="position:absolute;left:0;right:0;bottom:55px;text-align:center;color:#fff"><div style="font-size:26px;font-weight:900">请向右转头</div><div style="font-size:12px;color:#b9d4e2;margin-top:9px">保持面部在识别框内 · 3 秒</div></div></div>'
        return f'<div class="app-shell" style="background:#07111F">{statusbar(True)}{topbar(title,True)}<div class="page-content">{body}</div>{state_layer(state)}</div>'
    if t=='verifying':
        body='<div class="empty-state"><div class="spinner"></div><h3>正在核验身份</h3><p>媒体已静默上传至私有对象路径，正在调用人证比对服务。</p></div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div>{state_layer(state)}</div>'
    if t=='withdraw_home':
        tiers=''.join(f'<div style="height:74px;border-radius:17px;border:2px solid {"#FF7A3D" if i==0 else "#E8DFD3"};display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:900">¥ {v}</div>' for i,v in enumerate(['0.30','5.00','10.00','20.00','50.00','100.00']))
        body='<div class="hero"><div class="eyebrow">AVAILABLE BALANCE</div><h2>¥ 28.60</h2><p>支付宝：chen***@example.com · 已实名</p></div><div class="section-title"><h3>选择提现档位</h3><span>固定档位</span></div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:9px">'+tiers+'</div><div class="card" style="margin-top:14px"><p style="font-size:11px;color:#68728A;line-height:1.7">0.30元档位今日可提现1次；最终状态以支付宝出款查询为准。</p></div><button class="btn primary full" style="margin-top:12px">确认提现 ¥0.30</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div>{state_layer(state)}</div>'
    if t=='withdraw_confirm':
        body='<div class="hero"><h2>确认提现 ¥0.30</h2><p>账户余额将先转入冻结，出款成功后记为已支出。</p></div>'+list_rows([('收款方式','支付宝','ICON-PAY-ALIPAY',''),('实名姓名','陈*','ICON-IDENTITY',''),('支付宝账号','chen***@example.com','ICON-PAY-ALIPAY',''),('预计到账','¥0.30','ICON-CASH','')])+'<button class="btn primary full" style="margin-top:14px">提交提现</button>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='withdraw_list':
        body=list_rows([('提现 ¥0.30','今天 11:28 · 成功','ICON-CASH','已到账'),('提现 ¥5.00','08-15 16:08 · 出款中','ICON-CLOCK','处理中'),('提现 ¥10.00','08-14 09:22 · 失败退回','ICON-REPORT','已退回')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='withdraw_detail':
        body='<div class="hero"><div class="eyebrow">PAYOUT SUCCESS</div><h2>提现成功 ¥0.30</h2><p>提现单 WD202608160001</p></div>'+list_rows([('创建订单','11:28:03','ICON-ORDER','完成'),('余额冻结','11:28:03','ICON-LOCK','完成'),('支付宝受理','11:28:05','ICON-PAY-ALIPAY','完成'),('出款成功','11:28:08','ICON-CHECK','完成')])
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    if t=='me_home':
        body='<div class="hero"><div style="display:flex;gap:14px;align-items:center"><div style="width:72px;height:72px;border-radius:24px;background:linear-gradient(135deg,#FFC84A,#FF7A3D)"></div><div><span class="badge member">星耀会员</span><h2 style="margin:7px 0 2px">星矿玩家2026</h2><p>UID 2026 · 已实名认证</p></div></div></div><div style="margin-top:12px">'+asset_strip()+'</div>'+list_rows([('我的项目','发布、审核和推广服务','ICON-NAV-PROJECT','3'),('虚拟背包','推广卡和补给箱','ICON-BOX','14'),('邀请好友','一级18人 · 二级56人','ICON-INVITE',''),('积分提成','累计 486.20 星矿值','ICON-STAR-POINT',''),('消费佣金','累计 ¥128.60','ICON-CASH',''),('设置','账号、安全、声音和更新','ICON-ACTION-SETTINGS','')])
        return f'<div class="app-shell">{statusbar()}{topbar(title,back=False,right="settings")}<div class="page-content with-bottom scroll">{body}</div>{bottom_nav("me")}</div>'
    if t=='message_list':
        body=list_rows([('提现成功','¥0.30 已转入绑定支付宝','ICON-CASH','刚刚'),('项目审核通过','AI创作工具推广计划已发布','ICON-CHECK','10分钟前'),('矿机图鉴解锁','首次获得Lv.18智能矿业中枢','ICON-MINER','1小时前'),('系统公告','星矿纪元V1.1.0更新说明','ICON-NOTIFICATION','昨天')])
        return f'<div class="app-shell">{statusbar()}{topbar(title,right="more")}<div class="page-content scroll">{body}</div></div>'
    if t=='message_detail':
        body='<div class="card"><span class="badge success">提现</span><h2 style="font-size:20px">提现成功</h2><p style="font-size:12px;color:#68728A">2026-08-16 11:28</p><p style="font-size:13px;line-height:1.8">您的提现申请已通过支付宝证书出款完成，金额 ¥0.30。可在提现记录中查看完整状态时间线。</p><button class="btn primary full">查看提现详情</button></div>'
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content">{body}</div></div>'
    if t in ('settings','toggle_settings','device_list','about','help','danger'):
        if t=='toggle_settings': items=[('背景音乐','独立开关','ICON-VOLUME','开启'),('游戏音效','短音效和机械环境声','ICON-VOLUME','开启'),('震动反馈','合成和关键操作','ICON-VIBRATE','开启'),('消息通知','站内消息与系统通知','ICON-NOTIFICATION','开启')]
        elif t=='device_list': items=[('Windows Chrome','新加坡 · 当前设备','ICON-SECURITY','当前'),('Android Pixel 8','新加坡 · 2小时前','ICON-USER','退出')]
        elif t=='about': items=[('当前版本','V1.1.0','ICON-DOWNLOAD','最新'),('检查更新','应用内安全下载','ICON-REFRESH',''),('用户协议','版本 2026-08-16','ICON-ATLAS',''),('隐私政策','版本 2026-08-16','ICON-SECURITY','')]
        elif t=='help': items=[('账号与登录','邮箱验证码、密码与设备','ICON-USER',''),('矿机合成','购买、拖动和生产','ICON-MINER',''),('支付与订单','在线支付和人工扫码','ICON-PAY-CARD',''),('实名与提现','认证与出款状态','ICON-IDENTITY','')]
        elif t=='danger': items=[('注销账号','进入冷静期并停止关键业务','ICON-DELETE','申请注销')]
        else: items=[('账号与安全','密码、设备和赠送密码','ICON-SECURITY',''),('声音、震动和通知','三个独立音频/反馈开关','ICON-VOLUME',''),('帮助中心','常见问题','ICON-HELP',''),('协议与隐私','用户协议和隐私政策','ICON-ATLAS',''),('关于和更新','版本与安装包','ICON-DOWNLOAD',''),('退出登录','退出当前会话','ICON-LOGOUT','')]
        body=list_rows(items)
        return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div></div>'
    # Generic fallback
    body='<div class="hero"><div class="eyebrow">XKJY MODULE</div><h2>'+title+'</h2><p>本页面已绑定独立Page ID、状态、接口、数据库和返回状态合同。</p></div>'+list_rows([('核心信息','展示当前业务真实状态','ICON-CHECK',''),('操作记录','可追踪、可审计','ICON-ORDER',''),('安全控制','服务端校验与频控','ICON-SECURITY','')])+'<button class="btn primary full" style="margin-top:14px">确认操作</button>'
    return f'<div class="app-shell">{statusbar()}{topbar(title)}<div class="page-content scroll">{body}</div>{state_layer(state)}</div>'


def admin_sidebar(active_module):
    items=[('dashboard','ICON-CHART','运营总览'),('user','ICON-USERS','用户中心'),('game','ICON-MINER','游戏管理'),('project','ICON-NAV-PROJECT','项目推广'),('asset','ICON-WALLET','资产账本'),('payment','ICON-PAY-CARD','支付订单'),('identity','ICON-IDENTITY','实名与提现'),('system','ICON-ACTION-SETTINGS','系统管理')]
    return f'''<aside class="admin-sidebar"><div class="admin-brand"><img src="../../05_BRAND/app_icon/app_icon_512.png"><span>星矿纪元</span></div><div class="side-group">Platform</div>{''.join(f'<div class="side-item {"active" if k==active_module or (active_module in ("market","commission","referral") and k=="asset") or (active_module in ("withdrawal",) and k=="identity") else ""}">{icon(ic)}<span>{n}</span></div>' for k,ic,n in items)}<div class="side-group">Access</div><div class="side-item">{icon('ICON-SECURITY')}<span>权限与审计</span></div></aside>'''


def admin_table_rows(module, count=8):
    status=['正常','待审核','处理中','已完成','已限制']
    rows=''
    for i in range(count):
        st=status[i%len(status)]; cls='warn' if st in ('待审核','处理中') else 'error' if st=='已限制' else ''
        rows+=f'<tr><td><b>{2026+i}</b></td><td>{module.upper()}-{20260816000+i}</td><td>星矿玩家{2026+i}</td><td>{["12,860.45","¥ 10.00","Lv.18","100.0000"][i%4]}</td><td><span class="status-pill {cls}">{st}</span></td><td>2026-08-16 11:{20+i:02d}</td><td style="color:#3A8CFF;font-weight:800">查看</td></tr>'
    return rows


def generic_admin(page,state):
    t=page['template']; title=page['name_cn']; module=page['module']
    sidebar=admin_sidebar(module)
    header=f'''<div class="admin-main"><div class="admin-topbar"><div class="crumb">星矿纪元 / {module} / {title}</div><div class="admin-user"><div class="admin-avatar"></div><span>超级管理员</span></div></div><main class="admin-content"><div class="admin-title"><div><h1>{title}</h1><p>真实业务数据、配置、状态和审计统一管理</p></div><button class="admin-btn">新增或执行操作</button></div>'''
    if t in ('dashboard','admin_dashboard'):
        kpis=[('今日新增用户','268','+12.4%'),('今日星矿值产出','86.2M','+8.2%'),('今日支付金额','¥ 12,680','+6.8%'),('待处理审核','28','需要关注')]
        content='<div class="kpi-grid">'+''.join(f'<div class="kpi"><div class="kpi-label">{a}</div><div class="kpi-value">{b}</div><div class="kpi-delta">{c}</div></div>' for a,b,c in kpis)+'</div><div class="admin-grid"><div class="panel"><div class="panel-title"><span>近7日核心趋势</span><span style="color:#3A8CFF">查看详情</span></div><svg viewBox="0 0 700 260" style="width:100%;height:250px"><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#27D5C4" stop-opacity=".45"/><stop offset="1" stop-color="#27D5C4" stop-opacity="0"/></linearGradient></defs><path d="M0 220 C90 205 120 170 190 180 S300 80 380 120 S500 40 700 65 L700 260 L0 260Z" fill="url(#area)"/><path d="M0 220 C90 205 120 170 190 180 S300 80 380 120 S500 40 700 65" fill="none" stroke="#27D5C4" stroke-width="5"/></svg></div><div class="panel"><div class="panel-title">待办事项</div>'+''.join(f'<div class="health-row" style="grid-template-columns:1.5fr .6fr"><span>{n}</span><b style="color:#F0642F">{v}</b></div>' for n,v in [('人工扫码审核','12'),('项目审核','8'),('实名复核','3'),('提现审核','5')])+'</div></div>'
    elif t=='admin_login':
        return f'''<div style="width:1440px;height:900px;background:linear-gradient(135deg,#07111F,#173B66);display:grid;grid-template-columns:1.2fr .8fr"><div style="padding:160px 90px;color:#fff"><img src="../../05_BRAND/app_icon/app_icon_512.png" style="width:96px;border-radius:24px"><h1 style="font-size:50px;margin:30px 0 12px">星矿纪元管理后台</h1><p style="font-size:18px;color:#b8d0df">游戏、项目、资产、支付、实名和提现的企业级控制中心</p></div><div style="background:#fff;margin:90px;border-radius:30px;padding:70px 52px;box-shadow:0 30px 80px rgba(0,0,0,.25)"><h2 style="font-size:30px">管理员登录</h2><p style="color:#7b879a">登录必须通过自研图形验证码和后端票据校验</p><div class="admin-field"><label>管理员账号</label><div class="control">输入账号</div></div><div class="admin-field" style="margin-top:18px"><label>登录密码</label><div class="control">输入密码</div></div><button class="admin-btn" style="width:100%;height:48px;margin-top:24px">安全登录</button></div></div>'''
    elif t in ('admin_config','admin_form'):
        fields=['启用状态','默认比例或数值','每日限额','单用户限制','开始时间','结束时间','紧急关闭开关','变更原因']
        content='<div class="panel"><div class="admin-form-grid">'+''.join(f'<div class="admin-field"><label>{x}</label><div class="control">{("开启" if i==0 else "请输入或选择")}</div></div>' for i,x in enumerate(fields))+'</div><div style="display:flex;justify-content:flex-end;gap:10px;margin-top:24px"><button class="admin-btn" style="background:#e7ecf1;color:#475269">取消</button><button class="admin-btn">保存配置</button></div></div>'
    elif t=='admin_board':
        slots=''.join(f'<div class="admin-slot">{f"<img src=\"../../06_MINERS/PNG/MINER_L{(i%10)+1:02d}.png\">" if i<12 else icon("ICON-LOCK")}</div>' for i in range(16))
        content=f'<div class="admin-grid"><div class="panel"><div class="panel-title">用户棋盘 · UID 2026</div><div class="admin-board">{slots}</div></div><div class="panel"><div class="panel-title">游戏账户快照</div>'+''.join(f'<div class="health-row" style="grid-template-columns:1.2fr 1fr"><span>{a}</span><b>{b}</b></div>' for a,b in [('棋盘版本','128'),('最高等级','Lv.18'),('仓库容量','12 / 24'),('待领取产出','36.8000'),('最后结算','11:28:42')])+'</div></div>'
    elif t=='admin_cards':
        cards=''.join(f'<div class="kpi" style="min-height:150px"><img src="../../06_MINERS/PNG/MINER_L{(i%36)+1:02d}.png" style="width:80px;height:80px;float:right"><div class="kpi-label">Lv.{i+1}</div><div style="font-size:15px;font-weight:900;margin-top:8px">矿机配置</div><div class="kpi-delta" style="margin-top:18px">产出与价格已配置</div></div>' for i in range(8))
        content='<div class="kpi-grid">'+cards+'</div>'
    elif t=='admin_detail' or t=='admin_review':
        content='<div class="admin-grid"><div class="panel"><div class="panel-title">业务详情</div>'+''.join(f'<div class="health-row"><b>{a}</b><span>{b}</span><span></span><span></span></div>' for a,b in [('业务编号','XK202608160001'),('用户','UID 2026 · 星矿玩家2026'),('当前状态','待审核'),('金额或数量','¥10.00 / 100.0000'),('创建时间','2026-08-16 11:28:03')])+'<div style="height:230px;border-radius:14px;background:linear-gradient(135deg,#102A4C,#27D5C4);margin-top:16px"></div></div><div class="panel"><div class="panel-title">审核与操作</div><div class="admin-field"><label>审核结论</label><div class="control">选择通过或拒绝</div></div><div class="admin-field" style="margin-top:14px"><label>审核说明</label><div class="control" style="height:100px">填写原因并进入审计日志</div></div><button class="admin-btn" style="width:100%;margin-top:18px">提交审核</button></div></div>'
    elif t=='admin_health':
        services=['PostgreSQL','Redis','Cloudflare R2','SMTP邮箱','XApay支付宝','XApay微信','阿里云人证比对','支付宝证书出款','Outbox Worker']
        content='<div class="panel"><div class="health-row" style="font-weight:900;color:#7b8797"><span>服务</span><span>状态</span><span>延迟</span><span>最后检查</span></div>'+''.join(f'<div class="health-row"><b>{s}</b><span><i class="health-dot"></i>正常</span><span>{18+i*7} ms</span><span>11:29:{10+i:02d}</span></div>' for i,s in enumerate(services))+'</div>'
    elif t=='admin_chart':
        content='<div class="kpi-grid">'+''.join(f'<div class="kpi"><div class="kpi-label">{a}</div><div class="kpi-value">{b}</div><div class="kpi-delta">{c}</div></div>' for a,b,c in [('当日参考价','¥0.5368','+1.00%'),('星矿值总存量','826.4M','+4.2%'),('今日兑换','1.28M','稳定'),('求购订单','286','+18')])+'</div><div class="panel" style="margin-top:16px"><svg viewBox="0 0 1050 430" style="width:100%;height:430px"><path d="M30 380 C160 350 230 360 330 280 S520 240 620 170 S830 130 1020 70" fill="none" stroke="#27D5C4" stroke-width="8"/><path d="M30 380 C160 350 230 360 330 280 S520 240 620 170 S830 130 1020 70 L1020 430 L30 430Z" fill="#27D5C4" opacity=".12"/></svg></div>'
    elif t=='admin_tree':
        content='<div class="admin-grid"><div class="panel"><div class="panel-title">权限树</div>'+''.join(f'<div style="padding:11px {20+i*18}px;border-bottom:1px solid #edf0f4;font-size:12px"><span style="display:inline-block;width:16px;height:16px;border-radius:4px;background:#27D5C4;margin-right:10px"></span>{name}</div>' for i,name in enumerate(['全部权限','用户中心','游戏管理','项目推广','资产账本','支付订单','实名与提现','系统管理']))+'</div><div class="panel"><div class="panel-title">角色权限摘要</div><p style="font-size:12px;color:#7b8797;line-height:1.8">字段权限、数据范围权限、敏感媒体权限和资金操作权限分别控制。</p></div></div>'
    elif t=='admin_timeline':
        content='<div class="panel">'+''.join(f'<div style="display:grid;grid-template-columns:120px 20px 1fr;min-height:80px"><span style="font-size:11px;color:#7b8797">11:{20+i:02d}:03</span><span style="width:12px;height:12px;border-radius:50%;background:#27D5C4;margin-top:4px"></span><div><b>{name}</b><p style="font-size:11px;color:#7b8797">记录请求ID、业务ID、状态变化和操作人</p></div></div>' for i,name in enumerate(['创建业务记录','完成风控校验','调用第三方通道','接收结果并验签','统一结算完成']))+'</div>'
    else:
        content=f'''<div class="filter-bar"><div class="admin-input">搜索UID、业务编号或关键词</div><div class="admin-select">全部状态 <span>⌄</span></div><div class="admin-select">今日 <span>⌄</span></div><button class="admin-btn">查询</button></div><table class="data-table"><thead><tr><th>UID</th><th>业务编号</th><th>用户</th><th>数值</th><th>状态</th><th>时间</th><th>操作</th></tr></thead><tbody>{admin_table_rows(module)}</tbody></table>'''
    return f'<div class="admin-shell" style="position:relative">{sidebar}{header}{content}</main></div>{state_layer(state,"admin")}</div>'


def generic_h5(page,state):
    t=page['template']; title=page['name_cn']
    if t=='invite_landing':
        body=f'''<div class="h5-shell"><div class="h5-hero"><img class="h5-logo" src="../../05_BRAND/app_icon/app_icon_512.png"><h1>加入星矿纪元</h1><p>邀请码 2026 · 注册后获得第一台一级矿机，完成新手流程解锁合成。</p></div><div class="h5-card">{form_page(title,[('邮箱','输入邮箱地址','ICON-MAIL'),('邮箱验证码','6位验证码','ICON-CHECK'),('登录密码','8~32位','ICON-LOCK')],'注册并下载App','邀请关系将在注册时一次性绑定')}</div></div>'''
        return body
    if t=='download_landing':
        return f'''<div class="h5-shell"><div class="h5-hero"><img class="h5-logo" src="../../05_BRAND/app_icon/app_icon_512.png"><h1>星矿纪元 Android</h1><p>原生矿机合成游戏平台 · 当前版本 V1.1.0</p></div><div class="h5-card"><div class="modal-icon">{icon('ICON-DOWNLOAD')}</div><h2 style="text-align:center">下载正式签名APK</h2><p style="font-size:12px;color:#68728A;line-height:1.7;text-align:center">安装包由Cloudflare R2分发，页面展示版本号、大小和SHA-256。</p><button class="btn primary full">下载 Android APK</button></div></div>'''
    if t=='pay_return':
        return f'''<div class="h5-shell"><div class="h5-hero" style="height:300px"><img class="h5-logo" src="../../05_BRAND/app_icon/app_icon_512.png"><h1>正在确认支付结果</h1><p>返回页不会直接发货，将通过服务端主动查单确认。</p></div><div class="h5-card"><div class="spinner"></div><h2 style="text-align:center">订单查询中</h2><p style="font-size:12px;color:#68728A;text-align:center">XK202608160001</p></div></div>'''
    if t=='project_share':
        return f'''<div class="h5-shell"><div class="h5-hero" style="height:320px"><img class="h5-logo" src="../../05_BRAND/app_icon/app_icon_512.png"><h1>AI创作工具推广计划</h1><p>来自星矿纪元项目板块的外部分享预览。</p></div><div class="h5-card"><div class="chips"><span class="badge headline">头条</span><span class="badge member">星耀会员</span></div><p style="font-size:13px;line-height:1.8">安装App后查看完整图片、联系方式、安全提示和浏览任务。</p><button class="btn primary full">打开或下载星矿纪元</button></div></div>'''
    body='<div class="h5-shell">'+statusbar()+topbar(title)+'<div class="page-content scroll"><div class="card">'+''.join(f'<h3>{i}. 条款标题</h3><p style="font-size:12px;line-height:1.8;color:#68728A">协议正文、版本号、生效日期和数据处理说明。</p>' for i in range(1,8))+'</div></div></div>'
    return body


def wrap_html(body, platform, title):
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><link rel="stylesheet" href="../shared/styles.css"></head><body>{body}</body></html>'''


def main():
    write(BASE/'10_HTML/shared/styles.css',CSS)
    app,h5,admin=flatten()
    entries=[]
    for page in app+h5+admin:
        states=['DEFAULT']+EXTRA_STATES.get(page['page_id'],[])
        folder='APP' if page['platform']=='android' else 'ADMIN' if page['platform']=='admin' else 'H5'
        for state in states:
            if page['platform']=='android': body=generic_app(page,state)
            elif page['platform']=='admin': body=generic_admin(page,state)
            else: body=generic_h5(page,state)
            html_text=wrap_html(body,page['platform'],f'{page["page_id"]} {state}')
            out=BASE/f'10_HTML/{folder}/{page["page_id"]}__{state}.html'
            write(out,html_text)
            entries.append({'platform':folder,'page_id':page['page_id'],'name':page['name_cn'],'state':state,'html':str(out.relative_to(BASE))})
    # browser index
    cards=''.join(f'''<article data-p="{e['platform']}" data-q="{e['page_id']} {e['name']} {e['state']}"><h3>{e['page_id']} · {e['state']}</h3><p>{e['name']}</p><a href="{e['platform']}/{e['page_id']}__{e['state']}.html">打开源文件</a><img src="../04_UI/{e['platform']}/{e['page_id']}__{e['state']}.png"></article>''' for e in entries)
    index=f'''<!doctype html><html><head><meta charset="utf-8"><title>星矿纪元UI索引</title><style>body{{font-family:sans-serif;background:#eef2f6;margin:0;padding:28px}}header{{position:sticky;top:0;background:#eef2f6;padding:10px 0;z-index:2}}input{{width:420px;height:42px;border:1px solid #ccd4de;border-radius:12px;padding:0 14px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}}article{{background:#fff;border-radius:16px;padding:14px;box-shadow:0 8px 22px #0b183012}}article h3{{font-size:13px;margin:0}}article p,article a{{font-size:11px}}article img{{width:100%;height:330px;object-fit:contain;background:#dfe5ec;border-radius:10px;margin-top:10px}}</style></head><body><header><h1>星矿纪元 V1.1.0 UI索引 · {len(entries)}张</h1><input id=q placeholder="搜索Page ID、名称或状态"></header><div class=grid>{cards}</div><script>q.oninput=()=>document.querySelectorAll('article').forEach(x=>x.style.display=x.dataset.q.toLowerCase().includes(q.value.toLowerCase())?'block':'none')</script></body></html>'''
    write(BASE/'10_HTML/UI_PREVIEW_INDEX.html',index)
    write(BASE/'10_HTML/RENDER_INDEX.json',json.dumps(entries,ensure_ascii=False,indent=2))
    print('html generated',len(entries))

if __name__=='__main__':main()
