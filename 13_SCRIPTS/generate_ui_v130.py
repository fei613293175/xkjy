from __future__ import annotations
from pathlib import Path
import json, html, re, hashlib

ROOT=Path(__file__).resolve().parents[1]
HTML_DIR=ROOT/'10_HTML'/'APP'
HTML_DIR.mkdir(parents=True,exist_ok=True)
OLD_INDEX=Path('/mnt/data/xkjy_v120_inspect/XKJY_V120/10_HTML/RENDER_INDEX.json')
ENTRIES=[x for x in json.loads(OLD_INDEX.read_text(encoding='utf-8')) if x['platform']=='APP']

A='../../07_GAME_ASSETS/v130'
MIN='../../06_MINERS/PNG_V130'
V120='../../07_GAME_ASSETS/v120'

ICON={k:f"{A}/icons/icon_{k}.png" for k in [
'nav_home','nav_project','nav_mall','nav_discover','nav_me','store','warehouse','atlas','task','box','identity','invite','member','withdraw','wallet','message','settings','help','order','commission','merge','ranking','sign','back','close','search','plus','copy','gift','camera','check','warning']}
TOK={'star':f'{A}/icons/token_star_point.png','energy':f'{A}/icons/token_energy_chip.png','cash':f'{A}/icons/token_cash.png'}
AVATAR=f'{A}/objects/avatar_captain_v130.png'
ROBOT=f'{A}/objects/mascot_robot_v130.png'
QR=f'{V120}/objects/invite_qr_2026.png'
TH={n:f'{A}/project_thumbs/{n}.png' for n in ['frontier','ai','web3','city','community','new']}


def esc(s): return html.escape(str(s))

def statusbar():
    return '<div class="statusbar"><span>11:29</span><span class="status-right"><span>5G</span><span>89%</span><span class="battery"></span></span></div>'

def topbar(title:str, back=True, action=None, root=False):
    left=f'<div class="back-btn"><img src="{ICON["back"]}"></div>' if back else '<div class="back-btn ghost"></div>'
    if action:
        right=f'<div class="top-action"><img src="{ICON.get(action,action)}"></div>'
    else: right='<div class="top-action ghost"></div>'
    return f'<div class="topbar {"root" if root else ""}">{left}<div class="topbar-title">{esc(title)}</div>{right}</div>'

def bottom_nav(active):
    items=[('home','首页','nav_home'),('project','项目','nav_project'),('mall','商城','nav_mall'),('discover','发现','nav_discover'),('me','我的','nav_me')]
    return '<div class="bottom-nav">'+''.join(f'<div class="nav-item {"active" if active==k else ""}"><img src="{ICON[i]}"><span>{t}</span></div>' for k,t,i in items)+'</div>'

def btn(text,kind='primary',full=False,compact=False,img=None,disabled=False):
    cls=f'btn {kind}'+(' full' if full else '')+(' compact' if compact else '')+(' disabled' if disabled else '')
    icon=f'<img src="{img}">' if img else ''
    return f'<button class="{cls}">{icon}<span>{esc(text)}</span></button>'

def field(label, placeholder, icon='order', area=False, error=None):
    er=' error' if error else ''
    a=' area' if area else ''
    err=f'<div class="field-error">{esc(error)}</div>' if error else ''
    return f'<div class="field"><label>{esc(label)}</label><div class="input{a}{er}"><img src="{ICON.get(icon,ICON["order"])}"><span>{esc(placeholder)}</span></div>{err}</div>'

def panel(body, cls='panel-pad', extra=''):
    return f'<div class="panel {extra}"><div class="{cls}">{body}</div></div>'

def sec(title, more=''):
    return f'<div class="section-head"><h2>{esc(title)}</h2><span>{esc(more)}</span></div>'

def badge(text,kind='member'): return f'<span class="badge {kind}">{esc(text)}</span>'

def asset_cards():
    vals=[('star','星矿值','15,620'),('energy','能源芯片','8,230'),('cash','账户余额','¥520.30')]
    return '<div class="asset-row">'+''.join(f'<div class="asset-card {k}"><div class="asset-label">{t}</div><img src="{TOK[k]}"><div class="asset-value">{v}</div></div>' for k,t,v in vals)+'</div>'

def mini_assets():
    vals=[('star','星矿值','15,620'),('energy','芯片','8,230'),('cash','余额','520.30')]
    return '<div class="asset-row">'+''.join(f'<div class="asset-mini"><img src="{TOK[k]}"><div><div class="label">{t}</div><div class="value">{v}</div></div></div>' for k,t,v in vals)+'</div>'

def list_row(icon,title,sub='',value='',chev=True):
    return f'<div class="list-row"><div class="row-icon"><img src="{ICON.get(icon,icon)}"></div><div class="row-main"><div class="row-title">{esc(title)}</div><div class="row-sub">{esc(sub)}</div></div><div class="row-value">{esc(value)}</div>{"<div class=\"chev\">›</div>" if chev else ""}</div>'

def menu_tile(icon,title): return f'<div class="menu-tile"><img src="{ICON[icon]}"><span>{esc(title)}</span></div>'

def state_toast(state):
    if state=='ERROR': return '<div class="toast error"><b>!</b> 网络请求失败，请检查网络后重试</div>'
    if state=='LOADING': return '<div class="toast"><b>•</b> 正在同步最新数据…</div>'
    if state in ('SUBMITTING','PROCESSING','VERIFYING','UPLOADING'): return '<div class="toast"><b>•</b> 正在安全处理，请勿重复操作</div>'
    if state in ('SUCCESS','TASK_SUCCESS'): return '<div class="toast success"><b>✓</b> 操作已成功完成</div>'
    if state in ('FAILURE','REJECTED'): return '<div class="toast error"><b>!</b> 操作未完成，请根据提示处理</div>'
    if state=='EXPIRED': return '<div class="toast error"><b>!</b> 当前订单已过期</div>'
    return ''

def doc(body,shell='app',bg='business',title=None,back=True,action=None,nav=None,root=False,modal=None,content_class='content'):
    bgmap={'business':'bg_business_space.svg','auth':'bg_auth_space.svg','game':'bg_mine_scene.svg','market':'bg_market.svg','profile':'bg_profile.svg','secure':'bg_secure.svg'}
    style=f' style="--page-bg:url(../../07_GAME_ASSETS/v130/backgrounds/{bgmap[bg]})"'
    top='' if title is None else topbar(title,back=back,action=action,root=root)
    navhtml=bottom_nav(nav) if nav else ''
    if nav and 'with-nav' not in content_class: content_class+=' with-nav'
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=360,initial-scale=1,maximum-scale=1"><title>{esc(title or '星矿纪元')}</title><link rel="stylesheet" href="../shared/styles_v130.css"></head><body><main class="app {shell}"{style}>{statusbar()}{top}<section class="{content_class}">{body}</section>{navhtml}{modal or ''}</main></body></html>'''

# ---------- core pages ----------
def splash():
    b=f'''<div class="system-center" style="padding:0 20px"><div style="width:100%;text-align:center"><div class="brand-logo" style="font-size:48px">星矿纪元</div><div class="brand-en">STAR MINE ERA</div><img class="system-art" style="width:230px;height:230px;margin-top:25px" src="{MIN}/MINER_L36.png"><div style="font-size:11px;color:#dce6f7;margin-top:10px">合成 · 放置 · 探索星际矿脉</div><div class="loading-bar" style="margin:28px 28px 0"><span style="width:82%"></span></div><div class="tiny muted" style="margin-top:8px">正在装载矿区资源 82%</div></div></div>'''
    return doc(b,bg='auth',content_class='content no-top')

def system_page(name,state):
    art=ROBOT; title=name; desc='服务正在维护，预计很快恢复。您的资产与游戏进度不会受到影响。'
    if '更新' in name: desc='发现新版本，包含矿场体验优化、性能改进与安全更新。'
    if '下载' in name: desc='请通过平台官方安装包完成下载与安装，安装前请核对版本号。'
    actions=btn('重新检查',full=True) if '维护' in name else btn('立即更新',full=True)
    b=f'<div class="system-center"><div class="system-card"><img class="system-art" src="{art}"><h1>{esc(title)}</h1><p>{desc}</p>{actions}<div class="hint">当前版本 V1.3.0 · 官方渠道</div></div></div>'
    return doc(b,bg='secure',content_class='content no-top')

def auth_page(name,state,page_id):
    tab='<div class="segmented"><span class="active">密码登录</span><span>验证码登录</span></div>' if page_id=='APP-AUTH-001' else ''
    if page_id=='APP-AUTH-001':
        fields=field('邮箱','请输入邮箱地址','message',error='邮箱或密码错误' if state=='ERROR' else None)+field('登录密码','请输入登录密码','settings')
        primary='正在登录…' if state=='SUBMITTING' else '登录矿区'
        links='<div class="auth-links"><span>注册新账号</span><span>忘记密码</span></div>'
    elif page_id=='APP-AUTH-002':
        fields=field('邮箱','请输入邮箱地址','message',error='该邮箱已注册' if state=='ERROR' else None)+field('邮箱验证码','输入6位验证码','message')+field('登录密码','8～32位字母和数字','settings')+field('邀请码（选填）','例如：2026','invite')
        primary='正在创建账号…' if state=='SUBMITTING' else '创建星矿账号'; links='<div class="hint">注册即表示同意《用户协议》和《隐私政策》</div>'
    elif page_id=='APP-AUTH-003':
        fields=field('邮箱','请输入注册邮箱','message')+field('邮箱验证码','输入6位验证码','message');primary='验证并继续';links=''
    elif page_id=='APP-AUTH-004':
        fields=field('新密码','8～32位字母和数字','settings')+field('确认新密码','请再次输入','settings');primary='保存新密码';links=''
    else:
        fields='<div class="panel panel-pad"><h2 style="margin-top:0">用户协议与隐私政策</h2><p class="small muted" style="line-height:1.8">请在使用星矿纪元前阅读平台服务规则、资产说明、隐私处理方式和账号安全要求。</p></div>';primary='我已阅读';links=''
    b=f'''<div class="auth-content"><div class="brand-block"><div class="brand-logo">星矿纪元</div><div class="brand-en">STAR MINE ERA</div><img class="mascot" src="{ROBOT}"></div><div class="auth-card">{tab}{'<div style="height:12px"></div>' if tab else ''}{fields}{btn(primary,full=True,disabled=state=='SUBMITTING')}{links}</div></div>'''
    modal=None
    if state=='SUBMITTING': modal=f'<div class="modal-layer"><div class="modal" style="max-width:270px"><div class="spinner"></div><h2>正在登录</h2><p>正在校验账号、设备和会话安全状态</p></div></div>'
    return doc(b,bg='auth',content_class='content no-top',modal=modal)

def security_modal(name):
    title=name.replace('弹窗','');
    if '图形' in name:
        inner='<div style="height:74px;border-radius:12px;background:linear-gradient(135deg,#19275c,#44328a);display:flex;align-items:center;justify-content:center;font-size:28px;letter-spacing:9px;font-weight:900;color:#f8d56a">7K3M9</div>'+field('验证码','请输入上图字符','warning')
    elif '邮箱' in name:
        inner='<p class="small muted">验证码将发送至 c***@example.com</p>'+field('邮箱验证码','输入6位数字','message')
    else: inner=field('赠送密码','输入6位赠送密码','settings')
    modal=f'<div class="modal-layer" style="inset:22px 0 0;background:rgba(1,4,13,.3)"><div class="modal"><h2>{title}</h2><p>完成安全验证后，系统会自动继续刚才的操作。</p>{inner}<div class="button-row">{btn("取消",kind="dark-btn")}{btn("确认",kind="primary")}</div></div></div>'
    b='<div class="system-center"><div class="system-card"><img class="system-art" src="'+ROBOT+'"><h1>安全验证</h1><p>高风险操作需要额外验证。</p></div></div>'
    return doc(b,bg='secure',content_class='content no-top',modal=modal)

def game_home(state):
    levels=[1,1,2,3,4,4,5,6,7,8,9,10]
    slots=[]
    for lv in levels:
        slots.append(f'<div class="slot"><img class="miner" src="{MIN}/MINER_L{lv:02d}.png"><span class="level">Lv.{lv}</span></div>')
    for _ in range(4): slots.append(f'<div class="slot locked"><img src="{ICON["identity"]}"></div>')
    toast=''
    if state=='OFFLINE': toast='<div class="toast success" style="margin:0 13px 5px">网络已恢复，矿场数据校准完成</div>'
    elif state=='BOARD_FULL': toast='<div class="toast error" style="margin:0 13px 5px">棋盘已满，请先合成或将矿机存入仓库</div>'
    elif state=='NEW_USER': toast='<div class="toast" style="margin:0 13px 5px">拖动两台相同等级矿机，完成首次合成</div>'
    bubble='<div class="bubble">+36.80</div>' if state=='CLAIMABLE' else ''
    hud=f'''<div class="game-hud"><div class="player-chip"><img src="{AVATAR}"><div><div class="player-name">星矿小队长</div><div class="player-sub">UID 2026 · VIP5</div></div></div><div class="hud-asset"><img src="{TOK['star']}"><div><div class="hl">星矿值</div><div class="hv">15,620</div></div></div><div class="hud-asset"><img src="{TOK['energy']}"><div><div class="hl">能源芯片</div><div class="hv">8,230</div></div></div></div>'''
    stage=f'''<div class="game-stage"><div class="stage-top"><div class="rate-chip"><span class="green">●</span><b>+125.6 / 小时</b></div><div class="stage-actions"><div class="stage-action"><img src="{ICON['task']}"></div><div class="stage-action"><img src="{ICON['gift']}"></div><div class="stage-action"><img src="{ICON['ranking']}"></div></div></div><div class="board-wrap"><div class="board">{''.join(slots)}</div></div><div class="claim-bar"><img src="{TOK['star']}"><div><div class="claim-main">领取收益</div><div class="claim-sub">离线与当前产出已结算</div></div><div class="claim-amount">+36.80 SP</div></div>{bubble}</div>'''
    dock='<div class="game-dock">'+''.join(f'<div class="dock-item"><img src="{ICON[i]}"><span>{t}</span></div>' for i,t in [('store','购买矿机'),('warehouse','仓库'),('atlas','图鉴'),('task','任务'),('box','补给箱')])+'</div>'
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=360,initial-scale=1,maximum-scale=1"><title>矿场首页</title><link rel="stylesheet" href="../shared/styles_v130.css"></head><body><main class="app game-app">{statusbar()}{hud}{toast}{stage}{dock}{bottom_nav('home')}</main></body></html>'''

def tutorial():
    b=f'<div class="system-center"><div class="system-card"><img class="system-art" src="{MIN}/MINER_L01.png"><h1>欢迎来到星矿纪元</h1><p>领取初始矿机，收集第一笔星矿值，再获得第二台矿机完成首次合成。</p>{btn("开始新手引导",full=True)}</div></div>'
    return doc(b,bg='game',content_class='content no-top')

def miner_store():
    cards=[]
    for lv,price in [(1,'100'),(2,'220'),(3,'500'),(4,'1,200'),(5,'2,800'),(6,'6,500')]:
        cards.append(f'<div class="product-card"><div class="product-art"><img src="{MIN}/MINER_L{lv:02d}.png"></div><div class="product-name">Lv.{lv} 矿机</div><div class="product-price">{price} 星矿值</div><div style="margin-top:7px">{btn("购买",compact=True,kind="primary",full=True)}</div></div>')
    b=mini_assets()+'<div style="height:9px"></div><div class="segmented"><span class="active">矿机</span><span>道具</span><span>补给</span></div>'+sec('可购买矿机','最高可购 Lv.6')+f'<div class="product-grid">{"".join(cards)}</div>'
    return doc(b,bg='business',title='矿机商店',back=True,nav='home')

def warehouse():
    lvls=[4,4,6,8,10]
    cards=''.join(f'<div class="slot" style="height:116px"><img class="miner" src="{MIN}/MINER_L{lv:02d}.png"><span class="level">Lv.{lv}</span></div>' for lv in lvls)+''.join('<div class="slot" style="height:116px"></div>' for _ in range(3))
    b=panel('<div style="display:flex;justify-content:space-between;align-items:center"><div><div class="strong">仓库容量</div><div class="small muted" style="margin-top:4px">仓库内矿机不参与生产</div></div><div class="gold strong" style="font-size:20px">5 / 8</div></div>')+sec('矿机仓库','长按查看详情')+f'<div class="panel panel-pad"><div class="board" style="height:auto;grid-template-rows:repeat(2,116px);gap:8px">{cards}</div></div><div style="height:10px"></div><div class="button-row">{btn("自动整理",kind="secondary",full=True)}{btn("扩容仓库",kind="primary",full=True)}</div>'
    return doc(b,bg='business',title='矿机仓库',back=True,nav='home')

def atlas():
    items=[]
    for lv in range(1,13):
        unlocked=lv<=10
        items.append(f'<div class="product-card" style="padding:7px;opacity:{1 if unlocked else .45}"><div class="product-art" style="height:75px"><img src="{MIN}/MINER_L{lv:02d}.png" style="width:68px;height:68px"></div><div class="product-name">Lv.{lv} {"已解锁" if unlocked else "未解锁"}</div><div class="tiny muted">+{round(.05*(2.05**(lv-1)),2)}/h</div></div>')
    b=panel('<div style="display:flex;justify-content:space-between"><div><b>已解锁 10 / 36</b><div class="tiny muted" style="margin-top:4px">收集全部矿机，解锁纪元成就</div></div>'+badge('28%','member')+'</div>')+sec('矿机图鉴','六大科技阶段')+f'<div class="product-grid">{"".join(items)}</div>'
    return doc(b,bg='business',title='矿机图鉴',back=True,nav='home')

def miner_detail():
    b=f'<div class="panel panel-pad" style="text-align:center"><img src="{MIN}/MINER_L10.png" style="width:190px;height:190px;object-fit:contain"><h2 style="margin:0">Lv.10 深层掘进机</h2><div class="small muted">机械工业时代 · 稀有矿机</div><div class="divider"></div><div class="metric-grid" style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px"><div class="price-summary"><span class="small">每小时产出</span><b>+25.6</b></div><div class="price-summary"><span class="small">历史获得</span><b>3</b></div></div><div style="height:12px"></div>{btn("放回棋盘",full=True)}</div>'
    return doc(b,bg='business',title='矿机详情',back=True,nav='home')

def game_modal(name,page_id):
    art=MIN+'/MINER_L09.png';title=name;desc='系统已完成本次操作。'
    if page_id=='APP-GAME-007': title='离线收益';desc='离线 02:45:30，共产出 18.60 星矿值。'
    elif page_id=='APP-GAME-008': title='新矿机解锁';desc='Lv.9 熔岩采矿机已加入图鉴，产出效率显著提升。'
    elif page_id=='APP-GAME-011': title='补给箱开启';desc='获得 12 星矿值、8 能源芯片和一台 Lv.2 矿机。';art=ICON['box']
    elif page_id=='APP-GAME-014': title='回收矿机';desc='回收后将返还当前基础价的20%，该操作不可撤回。'
    elif page_id=='APP-GAME-015': title='解锁新格位';desc='最高矿机达到要求，新的生产格位已解锁。';art=ICON['check']
    elif page_id=='APP-GAME-016': title='扩容仓库';desc='消耗200星矿值与400能源芯片，容量提升至12格。';art=ICON['warehouse']
    base=game_home('DEFAULT')
    modal=f'<div class="modal-layer"><div class="modal"><img class="modal-art" src="{art}"><h2>{title}</h2><p>{desc}</p>{btn("确定",full=True)}</div></div>'
    return base.replace('</main>',modal+'</main>')

def task_center():
    rows=''.join(list_row('task',t,s,v) for t,s,v in [('领取矿机收益','进度 2/3','+1 SP'),('完成矿机合成','进度 1/3','+2 SP'),('购买矿机','进度 2/2','领取'),('浏览项目任务','进度 1/2','+2 SP'),('每日登录','已完成','已领')])
    b=panel('<div style="display:flex;justify-content:space-between;align-items:center"><div><b>今日活跃度</b><div class="tiny muted">完成任务获得额外奖励</div></div><b class="gold">60 / 100</b></div><div class="progress" style="margin-top:10px"><span style="width:60%"></span></div>')+sec('每日任务','00:00刷新')+f'<div class="list">{rows}</div>'
    return doc(b,bg='business',title='任务中心',back=True,nav='home')

def sign_in():
    days=''.join(f'<div class="product-card" style="text-align:center;padding:8px"><div class="tiny muted">第{i}天</div><img src="{TOK["star"] if i%2 else TOK["energy"]}" style="width:45px;height:45px;margin:6px"><div class="small gold">+{i*2}</div>{badge("已领" if i<4 else "待签", "success" if i<4 else "warn")}</div>' for i in range(1,8))
    b=panel('<div style="text-align:center"><div class="gold strong" style="font-size:24px">连续签到 3 天</div><div class="small muted">第7天可领取稀有补给箱</div></div>')+sec('本轮奖励')+f'<div class="product-grid">{days}</div><div style="height:10px"></div>{btn("今日签到",full=True)}'
    return doc(b,bg='business',title='七日签到',back=True,nav='home')

def ranking():
    names=['星河队长','深空矿工','量子旅人','晶核猎手','轨道先锋']
    rows=''.join(f'<div class="rank-row"><div class="rank-num">{i}</div><img src="{AVATAR}"><div><div class="row-title">{n}</div><div class="row-sub">最高矿机 Lv.{37-i}</div></div><b class="gold">{round(9800/i):,}</b></div>' for i,n in enumerate(names,1))
    b='<div class="segmented"><span class="active">最高等级</span><span>累计产出</span><span>今日产出</span></div>'+sec('全服排行','我的排名 128')+panel(rows)
    return doc(b,bg='business',title='排行榜',back=True,nav='home')

def production_detail():
    rows=''.join(list_row('merge',t,s,v,False) for t,s,v in [('矿场领取','今天 11:20','+36.80'),('离线收益','今天 08:35','+18.60'),('矿场领取','昨天 22:16','+41.20'),('任务奖励','昨天 20:10','+2.00'),('矿场领取','昨天 17:02','+35.75')])
    b=panel('<div class="price-summary"><div><div class="tiny">当前每小时产出</div><strong>125.60</strong></div><img src="'+TOK['star']+'" style="width:52px;height:52px"></div>')+sec('产出记录','最近30天')+f'<div class="list">{rows}</div>'
    return doc(b,bg='business',title='产出明细',back=True,nav='home')

# project pages
def project_cards(count=5):
    data=[('frontier','星际矿脉开发计划','完成浏览任务，领取星矿值奖励','12.8w','1,256',['头条','置顶']),('ai','AI智能工具推广平台','高效AI工具，轻松提升工作效率','5.2w','421',['置顶']),('web3','Web3生态任务平台','完成生态任务，赢取平台奖励','3.1w','302',['刷新']),('city','区域链应用推广项目','新场景、新应用、新机会','8.6w','982',['头条']),('new','新用户福利活动','限量福利，先到先得','2.6w','210',['刷新'])]
    htmls=[]
    for img,title,desc,view,likes,tags in data[:count]:
        tag=''.join(badge(x,{'头条':'headline','置顶':'pin','刷新':'refresh'}[x]) for x in tags)
        htmls.append(f'<div class="project-card"><img class="project-img" src="{TH[img]}"><div class="project-body"><div class="project-tags">{tag}</div><div class="project-title">{title}</div><div class="project-desc">{desc}</div><div class="project-meta"><span>浏览 {view}</span><span>收藏 {likes}</span></div></div></div>')
    return ''.join(htmls)

def project_home(state):
    if state=='EMPTY': content='<div class="empty"><img src="'+ICON['nav_project']+'"><h3>暂无项目</h3><p>当前分类暂无内容，换个分类看看。</p></div>'
    elif state=='LOADING': content=''.join('<div class="project-card" style="height:88px;opacity:.45"><div class="project-img" style="background:#18264d"></div><div class="project-body"><div style="height:10px;background:#23345e;border-radius:5px;width:70%"></div><div style="height:8px;background:#1a284a;border-radius:4px;margin-top:14px"></div></div></div>' for _ in range(5))
    else: content=project_cards()
    b=state_toast(state)+'<div class="input"><img src="'+ICON['search']+'"><span>搜索项目名称或关键词</span></div><div style="height:9px"></div><div class="chips"><div class="chip active">推荐</div><div class="chip">头条</div><div class="chip">置顶</div><div class="chip">红包</div></div>'+sec('热门项目','按推广权重排序')+content
    return doc(b,bg='business',title='项目 · 星际情报站',back=False,action='plus',nav='project',root=True)

def project_search():
    b='<div class="input"><img src="'+ICON['search']+'"><span>AI工具</span></div>'+sec('搜索结果','共 12 条')+project_cards(4)
    return doc(b,bg='business',title='搜索项目',back=True,nav='project')

def project_form(name='发布或编辑项目'):
    b=field('项目标题','5～40字','nav_project')+field('项目简介','10～120字','order')+field('详细介绍','20～5000字','order',area=True)+field('项目链接（选填）','https://','search')+field('联系方式','微信、QQ或手机号','message')+sec('项目图片','最多8张')+'<div class="media-grid"><div class="media-box"><img src="'+ICON['plus']+'" style="width:28px;height:28px;opacity:.65"></div><div class="media-box"><img src="'+TH['frontier']+'"></div><div class="media-box"><img src="'+TH['ai']+'"></div></div><div style="height:12px"></div>'+btn('保存并提交审核',full=True)
    return doc(b,bg='business',title=name,back=True,nav='project')

def project_image_manager():
    boxes=''.join(f'<div class="media-box"><img src="{TH[n]}"></div>' for n in ['frontier','ai','web3','city'])+'<div class="media-box"><img src="'+ICON['plus']+'" style="width:30px;height:30px;opacity:.6"></div>'
    b=panel('<b>已上传 4 / 8</b><div class="tiny muted" style="margin-top:4px">长按拖动调整图片顺序</div>')+sec('项目图片')+f'<div class="media-grid">{boxes}</div><div style="height:12px"></div>{btn("保存顺序",full=True)}'
    return doc(b,bg='business',title='项目图片管理',back=True,nav='project')

def project_result():
    b='<div class="system-center" style="height:630px"><div class="system-card"><div class="result-icon"><img src="'+ICON['check']+'"></div><h1>提交成功</h1><p>项目已进入审核队列，审核结果将通过消息中心通知。</p>'+btn('查看我的项目',full=True)+'</div></div>'
    return doc(b,bg='business',title='发布结果',back=True,nav='project')

def project_detail(state):
    task=''
    if state=='TASK_RUNNING': task=panel('<div style="display:flex;justify-content:space-between"><b>浏览任务进行中</b><b class="gold">00:12</b></div><div class="progress" style="margin-top:9px"><span style="width:60%"></span></div><div class="tiny muted" style="margin-top:6px">保持页面在前台，完成后自动发放奖励</div>')
    elif state=='TASK_SUCCESS': task=panel('<div style="display:flex;justify-content:space-between"><b class="green">任务完成</b><b class="gold">+2.00 SP</b></div>')
    elif state=='OFFLINE_BY_ADMIN': task='<div class="toast error">该项目已被平台下架，内容仅供历史查看</div>'
    b=task+f'<div class="panel"><img src="{TH["frontier"]}" style="width:100%;height:176px;object-fit:cover"><div class="panel-pad"><div class="project-tags">{badge("头条","headline")}{badge("置顶","pin")}{badge("VIP","member")}</div><h2 style="font-size:18px;margin:8px 0">星际矿脉开发计划</h2><div class="small muted">发布者：星河计划 · UID 2058</div><div class="divider"></div><p class="small muted" style="line-height:1.75">聚焦星际资源开发、智能矿机协作与新型任务场景，为推广用户提供更高效的曝光渠道。</p><div class="media-grid"><div class="media-box"><img src="{TH["frontier"]}"></div><div class="media-box"><img src="{TH["city"]}"></div><div class="media-box"><img src="{TH["web3"]}"></div></div><div style="height:12px"></div><div class="button-row">{btn("获取联系方式",kind="purple-btn",full=True)}{btn("打开项目链接",kind="primary",full=True)}</div><div class="hint">请谨慎核实项目主体与外部链接，平台不对站外交易承担担保责任。</div></div></div>'
    return doc(b,bg='business',title='项目详情',back=True,action='message',nav='project')

def contact_panel():
    base=project_detail('DEFAULT')
    modal=f'<div class="modal-layer"><div class="modal"><h2>联系方式与项目链接</h2><p>确认后将展示完整联系方式，并记录本次获取行为。</p>{list_row("message","微信","xkjy2026",chev=False)}{list_row("search","项目域名","project.example.com",chev=False)}<div style="height:12px"></div><div class="button-row">{btn("复制微信",kind="secondary",full=True)}{btn("打开链接",kind="primary",full=True)}</div></div></div>'
    return base.replace('</main>',modal+'</main>')

def project_report():
    b='<div class="chips" style="flex-wrap:wrap">'+''.join(f'<div class="chip {"active" if i==0 else ""}">{t}</div>' for i,t in enumerate(['欺诈风险','虚假宣传','违法违规','链接异常','其他']))+'</div><div style="height:12px"></div>'+field('问题说明','请描述具体情况','warning',area=True)+sec('证据图片','最多3张')+'<div class="media-grid"><div class="media-box"><img src="'+ICON['plus']+'" style="width:30px;height:30px;opacity:.6"></div></div><div style="height:14px"></div>'+btn('提交举报',kind='red-btn',full=True)
    return doc(b,bg='business',title='举报项目',back=True,nav='project')

def my_projects():
    rows=''.join(list_row('nav_project',t,s,v) for t,s,v in [('星际矿脉开发计划','已发布 · 头条+置顶','管理'),('AI智能工具推广平台','审核中','查看'),('新用户福利活动','已下架','修改')])
    b='<div class="segmented"><span class="active">全部</span><span>已发布</span><span>审核中</span><span>已下架</span></div>'+sec('我的项目','共3条')+f'<div class="list">{rows}</div>'
    return doc(b,bg='business',title='我的项目',back=True,nav='project')

def project_manage():
    b=panel('<div style="display:flex;gap:10px"><img src="'+TH['frontier']+'" style="width:100px;height:72px;border-radius:10px;object-fit:cover"><div><b>星际矿脉开发计划</b><div class="tiny muted" style="margin-top:5px">已发布 · 浏览12.8w</div><div style="margin-top:6px">'+badge('头条','headline')+badge('置顶','pin')+'</div></div></div>')+sec('运营数据')+asset_cards()+sec('项目操作')+'<div class="grid-menu">'+''.join(menu_tile(i,t) for i,t in [('order','编辑'),('member','推广'),('task','任务'),('settings','下架')])+'</div>'
    return doc(b,bg='business',title='项目管理',back=True,nav='project')

def promotion_card():
    cards=''.join(f'<div class="product-card"><div class="product-art"><img src="{ICON[i]}"></div><div class="product-name">{t}</div><div class="product-price">库存 {n} 张</div>{btn("立即使用",compact=True,full=True)}</div>' for i,t,n in [('member','头条卡',3),('identity','置顶卡',5),('sign','刷新卡',12)])
    b=panel('<b>选择项目</b><div class="input" style="margin-top:9px"><img src="'+ICON['nav_project']+'"><span>星际矿脉开发计划</span></div>')+sec('可用推广卡')+f'<div class="product-grid">{cards}</div>'
    return doc(b,bg='business',title='使用推广卡',back=True,nav='project')

def promotion_history():
    rows=''.join(list_row('member',t,s,v) for t,s,v in [('头条卡','2026-08-16 12:00 生效','至明日12:00'),('置顶卡','2026-08-16 12:00 生效','至明日12:00'),('刷新卡','2026-08-16 11:50 使用','已完成')])
    return doc(sec('推广服务记录','最近30天')+f'<div class="list">{rows}</div>',bg='business',title='推广记录',back=True,nav='project')

def favorite_projects(): return doc(sec('我的收藏','共12条')+project_cards(5),bg='business',title='我的收藏',back=True,nav='project')

def gallery():
    imgs=''.join(f'<img src="{TH[n]}" style="width:100%;height:180px;border-radius:16px;object-fit:cover;margin-bottom:10px;border:1px solid #2f4f7d">' for n in ['frontier','city','ai'])
    return doc(imgs,bg='business',title='项目图片',back=True,nav='project')

def category_selector():
    rows=''.join(list_row('nav_project',t,'后台配置分类','已选' if i==0 else '') for i,t in enumerate(['综合','推广服务','工具软件','Web3生态','福利活动']))
    return doc('<div class="list">'+rows+'</div>',bg='business',title='选择项目分类',back=True,nav='project')

def task_campaign_form():
    b=field('单人奖励','2.00 星矿值','star')+field('目标人数','100人','invite')+field('浏览时长','20秒','task')+field('活动结束时间','2026-08-23 23:59','sign')+panel('<div style="display:flex;justify-content:space-between"><span>预计总预算</span><b class="gold">200.00 SP</b></div><div class="tiny muted" style="margin-top:6px">支付后活动进入待开始状态</div>')+btn('确认预算并支付',full=True)
    return doc(b,bg='business',title='创建浏览任务',back=True,nav='project')

# mall/payment
def mall_home():
    products=[('member','年度会员VIP','¥99 / 年'),('member','头条卡 ×1','500 SP'),('identity','置顶卡 ×1','300 SP'),('sign','刷新卡 ×1','100 SP'),('gift','红包卡 10元','20,000 SP'),('box','星际补给箱','1,000 SP')]
    cards=''.join(f'<div class="product-card"><div class="product-art"><img src="{ICON[i]}"></div><div class="product-name">{t}</div><div class="product-price">{p}</div>{btn("购买",compact=True,full=True)}</div>' for i,t,p in products)
    b=mini_assets()+'<div style="height:9px"></div><div class="segmented"><span class="active">推荐</span><span>会员</span><span>推广</span><span>红包</span></div>'+sec('精选商品','全部为虚拟商品')+f'<div class="product-grid">{cards}</div>'
    return doc(b,bg='business',title='商城 · 补给站',back=False,action='order',nav='mall',root=True)

def product_detail():
    b=f'<div class="panel panel-pad" style="text-align:center"><div class="product-art" style="height:190px"><img src="{ICON["member"]}" style="width:145px;height:145px"></div><h2>年度会员 VIP</h2><div class="gold strong" style="font-size:22px">¥99 / 年</div><div class="divider"></div><div class="small muted" style="line-height:1.8;text-align:left">· 推广服务5折<br>· 项目专属会员标识<br>· 会员权益与专属主题<br>· 有效期365天</div><div style="height:12px"></div>{btn("立即购买",full=True)}</div>'
    return doc(b,bg='business',title='商品详情',back=True,nav='mall')

def order_confirm():
    b=panel('<div style="display:flex;gap:12px;align-items:center"><div class="row-icon"><img src="'+ICON['member']+'"></div><div><b>年度会员 VIP</b><div class="tiny muted">365天会员权益</div></div></div><div class="divider"></div><div style="display:flex;justify-content:space-between"><span class="small muted">商品原价</span><b>¥198.00</b></div><div style="display:flex;justify-content:space-between;margin-top:8px"><span class="small muted">会员活动优惠</span><b class="green">-¥99.00</b></div><div class="divider"></div><div style="display:flex;justify-content:space-between"><b>应付金额</b><b class="gold" style="font-size:20px">¥99.00</b></div>')+sec('购买说明')+panel('<div class="small muted" style="line-height:1.8">虚拟商品支付成功后立即生效，请核对账号与商品信息。</div>')+btn('进入收银台',full=True)
    return doc(b,bg='business',title='订单确认',back=True,nav='mall')

def backpack():
    rows=''.join(list_row(i,t,s,v) for i,t,s,v in [('member','头条卡','有效期长期','3张'),('identity','置顶卡','有效期长期','5张'),('sign','刷新卡','有效期长期','12张'),('box','星际补给箱','2026-09-01到期','2个')])
    return doc('<div class="segmented"><span class="active">全部</span><span>推广卡</span><span>补给箱</span></div>'+sec('虚拟背包')+f'<div class="list">{rows}</div>',bg='business',title='虚拟背包',back=True,nav='mall')

def pay_page(state):
    b=state_toast(state)+panel('<div style="text-align:center"><div class="tiny muted">订单应付金额</div><div class="gold strong" style="font-size:32px;margin-top:5px">¥99.00</div><div class="tiny muted">订单号 XKJY202608160001</div></div>')+sec('选择支付方式')+f'<div class="list">{list_row("wallet","账户余额","可用 ¥520.30","推荐")}{list_row(TOK["cash"],"支付宝","XApay在线支付","")}{list_row("message","微信支付","XApay在线支付","")}{list_row("camera","人工扫码","支付宝 / 微信 / QQ","")}</div><div style="height:12px"></div>{btn("确认支付",full=True,disabled=state in ("PROCESSING","SUCCESS","FAILURE","EXPIRED"))}'
    modal=None
    if state=='PROCESSING': modal='<div class="modal-layer"><div class="modal" style="max-width:270px"><div class="spinner"></div><h2>正在确认支付</h2><p>请勿重复支付或关闭应用</p></div></div>'
    if state=='SUCCESS': modal='<div class="modal-layer"><div class="modal"><div class="result-icon"><img src="'+ICON['check']+'"></div><h2>支付成功</h2><p>会员权益已发放，有效期至2027-08-16。</p>'+btn('完成',full=True)+'</div></div>'
    if state=='FAILURE': modal='<div class="modal-layer"><div class="modal"><div class="result-icon fail"><img src="'+ICON['warning']+'"></div><h2>支付失败</h2><p>支付未完成，未扣除任何平台资产。</p>'+btn('重新支付',full=True)+'</div></div>'
    return doc(b,bg='secure',title='安全收银台',back=True,nav=None,modal=modal)

def manual_pay(state):
    sub={'DEFAULT':'请使用对应应用扫码付款','UPLOADING':'付款截图正在上传','REVIEW_PENDING':'付款凭证已提交审核','REJECTED':'审核未通过，请重新提交截图'}[state]
    b=state_toast(state)+panel(f'<div style="text-align:center"><div class="gold strong" style="font-size:25px">¥99.00</div><div class="small muted">{sub}</div><div style="height:12px"></div><img src="{QR}" class="qr"><div class="tiny muted" style="margin-top:7px">付款备注：160001</div></div>')+sec('付款截图')+'<div class="media-box" style="height:120px"><img src="'+(TH['ai'] if state!='DEFAULT' else ICON['camera'])+'" style="'+('width:100%;height:100%;object-fit:cover' if state!='DEFAULT' else 'width:38px;height:38px;opacity:.65')+'"></div><div style="height:12px"></div>'+btn('提交付款审核' if state!='REJECTED' else '重新上传并提交',full=True,disabled=state in ('UPLOADING','REVIEW_PENDING'))
    return doc(b,bg='secure',title='人工扫码支付',back=True)

def pay_result():
    b='<div class="system-center" style="height:690px"><div class="system-card"><div class="spinner"></div><h1>正在查询订单</h1><p>系统正在核对支付通道状态，结果将自动刷新。</p>'+btn('再次查询',kind='secondary',full=True)+'</div></div>'
    return doc(b,bg='secure',title='支付结果',back=True)

def order_list():
    rows=''.join(list_row('order',t,s,v) for t,s,v in [('年度会员VIP','2026-08-16 · 已支付','¥99.00'),('头条卡×1','2026-08-15 · 已完成','500 SP'),('项目任务预算','2026-08-14 · 已完成','200 SP')])
    return doc('<div class="segmented"><span class="active">全部</span><span>待支付</span><span>已完成</span></div>'+sec('订单记录')+f'<div class="list">{rows}</div>',bg='business',title='我的订单',back=True,nav='mall')

def order_detail():
    b=panel('<div style="text-align:center"><div class="badge success">已完成</div><div class="gold strong" style="font-size:28px;margin-top:9px">¥99.00</div><div class="tiny muted">年度会员VIP</div></div>')+sec('订单信息')+f'<div class="list">{list_row("order","订单号","XKJY202608160001","",False)}{list_row("wallet","支付方式","账户余额","",False)}{list_row("sign","支付时间","2026-08-16 11:29","",False)}</div>'
    return doc(b,bg='business',title='订单详情',back=True,nav='mall')

def member_center():
    b=f'<div class="panel panel-pad" style="text-align:center;background:linear-gradient(145deg,#3d285d,#172451)"><img src="{ICON["member"]}" style="width:110px;height:110px"><h2 style="color:#ffd96c;margin:3px 0">年度会员 VIP</h2><div class="small">有效期至 2026-12-31</div><div class="divider"></div><div class="grid-menu">{menu_tile("member","5折权益")}{menu_tile("nav_project","专属标识")}{menu_tile("task","每日奖励")}{menu_tile("help","优先服务")}</div><div style="height:14px"></div>{btn("立即续费 ¥99/年",full=True)}</div>'+sec('会员订单')+f'<div class="list">{list_row("order","年度会员VIP","订单号 208001150001","已支付")}</div>'
    return doc(b,bg='business',title='会员中心',back=True,nav='mall')

# market
def market_home():
    orders=[('0.600','50,000','微信：xx...868','2058'),('0.580','20,000','QQ：123...678','2091'),('0.570','10,000','手机：138...8888','2178'),('0.550','30,000','微信：m***123','2201')]
    oc=''.join(f'<div class="order-card"><div class="order-top"><div><div class="order-price">¥{p} / SP</div><div class="order-meta">求购 {q} 星矿值<br>{c}</div></div>{btn("联系",kind="secondary",compact=True)}</div><div class="tiny muted" style="text-align:right">UID {uid}</div></div>' for p,q,c,uid in orders)
    chart='''<div class="chart-card"><div class="chart-price">0.5300 元</div><div class="chart-up">今日 +1.00%</div><svg viewBox="0 0 320 92"><polyline points="10,78 55,69 100,60 145,50 190,42 235,31 310,14" fill="none" stroke="#42cce8" stroke-width="5"/><g fill="#f5c34d">'''+''.join(f'<circle cx="{x}" cy="{y}" r="6"/>' for x,y in [(10,78),(55,69),(100,60),(145,50),(190,42),(235,31),(310,14)])+'''</g></svg></div>'''
    b='<div class="segmented"><span class="active">集市</span><span>游戏</span></div>'+sec('7日积分参考价值','每日00:00更新')+chart+sec('求购订单','单价从高到低')+oc+'<div style="height:8px"></div>'+btn('发布求购订单',full=True)
    return doc(b,bg='market',title='发现 · 积分集市',back=False,nav='discover',root=True)

def buy_order_form():
    b=field('求购数量','输入星矿值数量','star')+field('求购单价','输入每个星矿值的价格','cash')+field('联系方式类型','微信 / QQ / 手机号','message')+field('联系方式','请输入完整联系方式','message')+field('备注','0～200字','order',area=True)+panel('<div style="display:flex;justify-content:space-between"><span class="small muted">预计总金额</span><b class="gold" style="font-size:21px">¥0.00</b></div><div class="hint">所有关键字段由后端再次校验</div>')+btn('保存并提交',full=True)
    return doc(b,bg='market',title='发布或编辑求购单',back=True,nav='discover')

def buy_order_detail():
    b=panel('<div class="order-price">¥0.600 / SP</div><div class="divider"></div><div style="display:flex;justify-content:space-between"><span class="small muted">求购数量</span><b>50,000 SP</b></div><div style="display:flex;justify-content:space-between;margin-top:9px"><span class="small muted">预计总额</span><b class="gold">¥30,000</b></div><div style="display:flex;justify-content:space-between;margin-top:9px"><span class="small muted">发布者</span><b>UID 2058</b></div>')+sec('联系方式')+panel('<div style="display:flex;justify-content:space-between;align-items:center"><span>微信：xkjy888</span>'+btn('复制',compact=True,kind='secondary')+'</div>')+btn('赠送星矿值',full=True)
    return doc(b,bg='market',title='求购单详情',back=True,nav='discover')

def my_buy_orders():
    rows=''.join(list_row('order',t,s,v) for t,s,v in [('求购50,000 SP','¥0.600 / SP · 有效','管理'),('求购20,000 SP','¥0.580 / SP · 审核中','查看'),('求购10,000 SP','¥0.550 / SP · 已过期','复制')])
    return doc('<div class="segmented"><span class="active">全部</span><span>有效</span><span>审核中</span><span>已结束</span></div>'+sec('我的求购单')+f'<div class="list">{rows}</div>',bg='market',title='我的求购单',back=True,nav='discover')

def discover_container():
    b='<div class="segmented"><span class="active">集市</span><span>游戏</span></div>'+sec('发现中心','积分交易与玩法入口')+panel('<div style="display:flex;align-items:center;gap:14px"><img src="'+ICON['nav_discover']+'" style="width:70px;height:70px"><div><b>积分集市</b><div class="small muted" style="margin-top:5px">查看7日参考价格与求购订单</div></div></div>')+panel('<div style="display:flex;align-items:center;gap:14px"><img src="'+ICON['merge']+'" style="width:70px;height:70px"><div><b>更多游戏</b><div class="small muted" style="margin-top:5px">后续扩展积分消耗场景</div></div></div>')
    return doc(b,bg='market',title='发现',back=False,nav='discover',root=True)

def future_games():
    cards=''.join(f'<div class="product-card"><div class="product-art"><img src="{ICON[i]}"></div><div class="product-name">{t}</div><div class="tiny muted">开发预留入口</div></div>' for i,t in [('merge','晶核合成'),('ranking','星际竞速'),('gift','幸运补给'),('commission','矿区挑战')])
    return doc('<div class="segmented"><span>集市</span><span class="active">游戏</span></div>'+sec('玩法实验室','后续按版本开放')+f'<div class="product-grid">{cards}</div>',bg='market',title='发现 · 游戏',back=False,nav='discover',root=True)

# wallet/invite
def wallet_overview():
    b=asset_cards()+'<div style="height:10px"></div><div class="action-quad">'+''.join(btn(t,kind='secondary') for t in ['充值','提现','赠送','兑换'])+'</div>'+sec('资产服务')+'<div class="grid-menu">'+''.join(menu_tile(i,t) for i,t in [('wallet','资产明细'),('commission','积分提成'),('order','消费佣金'),('settings','赠送密码')])+'</div>'+sec('最近变动')+f'<div class="list">{list_row("merge","矿机产出","今天 11:20","+36.80")}{list_row("commission","一级好友提成","今天 10:15","+12.50")}{list_row("wallet","红包卡兑换","昨天 18:20","+¥10.00")}</div>'
    return doc(b,bg='profile',title='资产总览',back=True,nav='me')

def transaction_list(asset):
    icon={'星矿值流水':'star','能源芯片流水':'energy','账户余额流水':'cash'}[asset]
    rows=''.join(list_row('wallet',t,s,v) for t,s,v in [('矿机产出','今天 11:20','+36.80'),('商城消费','今天 10:16','-100.00'),('任务奖励','昨天 21:02','+2.00'),('好友提成','昨天 18:40','+12.50'),('积分赠送','前天 16:30','-50.00')])
    b=panel('<div class="price-summary"><div><div class="tiny">当前可用</div><strong>15,620.00</strong></div><img src="'+TOK[icon]+'" style="width:50px;height:50px"></div>')+sec('收支明细','最近30天')+f'<div class="list">{rows}</div>'
    return doc(b,bg='profile',title=asset,back=True,nav='me')

def transfer_form():
    b=field('收款UID','输入纯数字UID','invite')+field('赠送数量','输入星矿值数量','star')+panel('<div style="display:flex;justify-content:space-between"><span>额外消耗能源芯片</span><b class="purple">0 EP</b></div><div class="hint">每赠送1个星矿值，额外消耗2个能源芯片</div>')+btn('查询收款人',full=True)
    return doc(b,bg='profile',title='赠送星矿值',back=True,nav='me')

def recipient_confirm():
    b=panel('<div style="text-align:center"><img src="'+AVATAR+'" class="avatar-lg"><h2>深空矿工</h2><div class="small muted">UID 2058</div><div class="divider"></div><div style="display:flex;justify-content:space-between"><span>赠送星矿值</span><b class="gold">100 SP</b></div><div style="display:flex;justify-content:space-between;margin-top:8px"><span>消耗能源芯片</span><b class="purple">200 EP</b></div></div>')+field('赠送密码','输入6位赠送密码','settings')+btn('确认赠送',full=True)
    return doc(b,bg='profile',title='确认收款人',back=True,nav='me')

def transfer_result():
    b='<div class="system-center" style="height:630px"><div class="system-card"><div class="result-icon"><img src="'+ICON['check']+'"></div><h1>赠送成功</h1><p>100星矿值已到账至UID 2058，双方均已收到站内通知。</p>'+btn('完成',full=True)+'</div></div>'
    return doc(b,bg='profile',title='赠送结果',back=True,nav='me')

def password_form(title):
    b=field('邮箱验证码','输入6位验证码','message')+field('新赠送密码','输入6位纯数字','settings')+field('确认赠送密码','再次输入','settings')+btn('保存密码',full=True)
    return doc(b,bg='profile',title=title,back=True,nav='me')

def exchange_chip():
    b=panel('<div style="text-align:center"><img src="'+TOK['energy']+'" style="width:90px;height:90px"><h2>兑换能源芯片</h2><div class="small muted">消耗100星矿值，可获得50能源芯片</div></div>')+field('兑换星矿值数量','输入数量','star')+panel('<div style="display:flex;justify-content:space-between"><span>预计获得</span><b class="purple" style="font-size:21px">0 EP</b></div>')+btn('确认兑换',full=True)
    return doc(b,bg='profile',title='兑换能源芯片',back=True,nav='me')

def invite_overview():
    b=f'<div class="poster"><h2 style="margin:0">邀请好友，一起开矿</h2><div class="small" style="margin:4px 0 12px">邀请码 / UID</div><div class="price-summary"><strong>2026</strong>{btn("复制",compact=True)}</div><img src="{QR}" class="qr" style="margin-top:14px"><div class="button-row" style="margin-top:12px">{btn("复制链接",kind="secondary",full=True)}{btn("保存海报",kind="primary",full=True)}</div></div>'+sec('邀请数据')+asset_cards()+sec('好友关系')+f'<div class="list">{list_row("invite","一级好友","直接邀请用户","128人")}{list_row("invite","二级好友","一级好友邀请用户","356人")}{list_row("commission","累计提成","积分与消费佣金","1,250.30")}</div>'
    return doc(b,bg='profile',title='邀请好友',back=True,nav='me')

def invite_poster():
    b=f'<div class="poster" style="padding:22px"><div class="brand-logo" style="font-size:28px">星矿纪元</div><div class="small">邀请好友一起探索星际矿脉</div><img src="{AVATAR}" class="avatar-lg" style="margin:18px"><div class="price-summary"><strong>2026</strong><span class="small">我的UID</span></div><img src="{QR}" class="qr" style="margin:18px 0"><div class="tiny">扫码注册，邀请码自动填写</div></div><div style="height:12px"></div>{btn("保存海报到相册",full=True)}'
    return doc(b,bg='profile',title='邀请海报',back=True,nav='me')

def friend_list(title,second=False):
    names=['深空矿工','晶核猎手','星轨旅人','量子先锋','银河采集者']
    rows=''.join(f'<div class="list-row"><img src="{AVATAR}" style="width:40px;height:40px;border-radius:12px"><div class="row-main"><div class="row-title">{n}</div><div class="row-sub">UID {2058+i} · 注册 2026-08-{10+i:02d}</div></div><div class="row-value">+{12.5-i:.2f}</div></div>' for i,n in enumerate(names))
    return doc(sec(title,'累计5人')+f'<div class="list">{rows}</div>',bg='profile',title=title,back=True,nav='me')

def superior():
    b=panel('<div style="text-align:center"><img src="'+AVATAR+'" class="avatar-lg"><h2>星河领航员</h2><div class="small muted">UID 2025 · 注册于2026-08-01</div></div>')+sec('关系说明')+panel('<div class="small muted" style="line-height:1.8">上级关系注册时绑定，普通用户不可自行修改。如存在异常，请联系平台客服。</div>')
    return doc(b,bg='profile',title='我的上级',back=True,nav='me')

def commission_list(title):
    rows=''.join(list_row('commission',t,s,v) for t,s,v in [('一级好友矿机产出','UID 2058 · 今天11:20','+12.50'),('二级好友任务奖励','UID 2091 · 今天10:05','+6.25'),('一级好友推广消费','订单 208001','+9.90'),('佣金冲正','订单退款','-3.00')])
    return doc(panel('<div style="text-align:center"><div class="tiny muted">累计'+title+'</div><div class="gold strong" style="font-size:28px;margin-top:6px">1,250.30</div></div>')+sec('明细记录')+f'<div class="list">{rows}</div>',bg='profile',title=title,back=True,nav='me')

# identity/withdraw
def identity_entry():
    b=panel('<div style="text-align:center"><img src="'+ICON['identity']+'" style="width:110px;height:110px"><h2>完成实名认证</h2><div class="small muted">姓名 + 身份证号 + 人脸动作采集</div><div class="divider"></div><div class="small muted" style="line-height:1.8;text-align:left">· 提现前必须完成认证<br>· 采集媒体静默上传并按策略清理<br>· 平台仅展示脱敏认证结果</div><div style="height:12px"></div>'+btn('开始认证',full=True)+'</div>')
    return doc(b,bg='secure',title='实名认证',back=True,nav='me')

def identity_form():
    return doc(field('真实姓名','请输入真实姓名','identity')+field('身份证号','请输入18位身份证号','identity')+panel('<div class="small muted" style="line-height:1.7">继续即表示同意实名认证信息处理说明。</div>')+btn('下一步',full=True),bg='secure',title='实名认证',back=True,nav='me')

def camera_permission():
    b=panel('<div style="text-align:center"><img src="'+ICON['camera']+'" style="width:110px;height:110px"><h2>需要相机权限</h2><div class="small muted" style="line-height:1.8">仅在动作采集页面启用前置摄像头，退出页面后立即释放。</div><div style="height:12px"></div>'+btn('授权并继续',full=True)+'</div>')
    return doc(b,bg='secure',title='摄像头权限',back=True,nav='me')

def identity_capture(state):
    if state=='PERMISSION_DENIED':
        b=panel('<div style="text-align:center"><img src="'+ICON['warning']+'" style="width:100px;height:100px"><h2>未获得相机权限</h2><div class="small muted">请在系统设置中允许相机权限后重试。</div><div style="height:12px"></div>'+btn('打开系统设置',full=True)+'</div>')
    else:
        b='<div class="panel panel-pad" style="text-align:center"><div style="height:330px;border-radius:180px 180px 28px 28px;background:linear-gradient(180deg,#132957,#071126);border:2px solid #3e72ad;display:flex;align-items:center;justify-content:center;overflow:hidden"><img src="'+AVATAR+'" style="width:220px;height:220px;border-radius:50%"></div><h2>请缓慢向右转头</h2><div class="gold strong" style="font-size:32px">3</div><div class="progress"><span style="width:42%"></span></div></div>'
    return doc(b,bg='secure',title='人脸动作采集',back=True,nav='me')

def identity_verifying(state):
    if state=='VERIFYING':
        b='<div class="system-center" style="height:630px"><div class="system-card"><div class="spinner"></div><h1>身份核验中</h1><p>正在安全提交采集结果并核对身份信息，请保持网络连接。</p><div class="progress"><span style="width:68%"></span></div></div></div>'
    else:
        b='<div class="system-center" style="height:630px"><div class="system-card"><img class="system-art" src="'+ICON['identity']+'"><h1>采集完成</h1><p>身份资料已加密上传，点击开始核验后将提交至认证服务。</p>'+btn('开始核验',full=True)+'</div></div>'
    return doc(b,bg='secure',title='实名认证',back=True,nav='me')

def identity_result(state):
    if state=='DEFAULT':
        title='认证结果'; desc='核验结果将在此显示，也可稍后从实名认证入口重新查询。'; icon='identity'; success=True; action='返回个人中心'
    else:
        success=state=='SUCCESS'; rec=state=='RECAPTURE'
        title='认证成功' if success else ('需要重新采集' if rec else '认证失败')
        desc='身份信息已通过核验，提现功能现已开放。' if success else ('采集画面质量不足，请重新完成动作。' if rec else '身份信息未通过核验，请检查资料后重试。')
        icon='check' if success else 'warning'; action='完成' if success else '重新认证'
    b='<div class="system-center" style="height:630px"><div class="system-card"><div class="result-icon '+('' if success else 'fail')+'"><img src="'+ICON[icon]+'"></div><h1>'+title+'</h1><p>'+desc+'</p>'+btn(action,full=True)+'</div></div>'
    return doc(b,bg='secure',title='实名认证结果',back=True,nav='me')

def withdrawal_home(state):
    disabled=state=='DISABLED'
    tiers=[('0.30','今日剩3次'),('5.00','今日剩2次'),('10.00','今日剩1次'),('50.00','每周1次')]
    tierhtml=''.join(f'<div class="list-row"><img src="{TOK["cash"]}" style="width:34px;height:34px"><div class="row-main"><div class="row-title">¥{a}</div><div class="row-sub">{s}</div></div><div class="chev">›</div></div>' for a,s in tiers)
    b=state_toast('ERROR' if disabled else '')+panel('<div class="tiny muted">可提现余额</div><div class="strong" style="font-size:30px;margin-top:5px">¥520.30</div><div class="small muted" style="margin-top:4px">支付宝：c***@example.com</div>')+sec('提现档位','后台动态配置')+f'<div class="list">{tierhtml}</div><div style="height:12px"></div>{btn("立即提现",full=True,disabled=disabled)}'
    return doc(b,bg='secure',title='提现中心',back=True,nav='me')

def bind_alipay():
    return doc(panel('<div class="small muted">实名认证姓名</div><div class="strong" style="font-size:18px;margin-top:5px">陈*</div>')+field('支付宝账号','手机号或邮箱','wallet')+field('邮箱验证码','输入6位验证码','message')+btn('保存收款方式',full=True),bg='secure',title='绑定支付宝',back=True,nav='me')

def withdraw_confirm():
    b=panel('<div style="text-align:center"><div class="tiny muted">本次提现</div><div class="gold strong" style="font-size:34px;margin-top:5px">¥10.00</div><div class="tiny muted">到账至支付宝 c***@example.com</div></div>')+sec('费用与次数')+f'<div class="list">{list_row("wallet","手续费","平台当前免手续费","¥0.00",False)}{list_row("sign","今日剩余次数","10元档位","1次",False)}</div><div style="height:12px"></div>{btn("确认提现",full=True)}'
    return doc(b,bg='secure',title='提现确认',back=True,nav='me')

def withdraw_result(state):
    if state=='DEFAULT':
        title='提现申请已提交'; desc='¥10.00已冻结并进入处理队列，可在提现记录中查看进度。'; icon='check'; good=True
    elif state=='PROCESSING':
        title='出款处理中'; desc='支付宝通道正在处理，未知状态下系统不会提前返还冻结余额。'; icon='wallet'; good=True
    elif state=='SUCCESS':
        title='提现成功'; desc='¥10.00已转入绑定支付宝账户。'; icon='check'; good=True
    else:
        title='提现失败'; desc='出款未成功，冻结余额已按规则处理。'; icon='warning'; good=False
    b='<div class="system-center" style="height:630px"><div class="system-card"><div class="result-icon '+('' if good else 'fail')+'"><img src="'+ICON[icon]+'"></div><h1>'+title+'</h1><p>'+desc+'</p>'+btn('查看提现详情',full=True)+'</div></div>'
    return doc(b,bg='secure',title='提现结果',back=True,nav='me')

def withdrawal_records():
    rows=''.join(list_row('withdraw',t,s,v) for t,s,v in [('提现 ¥10.00','今天 11:29 · 处理中','查询'),('提现 ¥5.00','昨天 19:20 · 成功','已到账'),('提现 ¥0.30','昨天 10:15 · 成功','已到账')])
    return doc('<div class="segmented"><span class="active">全部</span><span>处理中</span><span>已完成</span></div>'+sec('提现记录')+f'<div class="list">{rows}</div>',bg='secure',title='提现记录',back=True,nav='me')

def withdrawal_detail():
    b=panel('<div style="text-align:center"><div class="badge warn">出款处理中</div><div class="gold strong" style="font-size:30px;margin-top:8px">¥10.00</div><div class="tiny muted">提现单 WD202608160001</div></div>')+sec('处理进度')+'<div class="panel panel-pad"><div class="timeline"><div class="timeline-item"><div class="timeline-title">提交申请</div><div class="timeline-sub">2026-08-16 11:29</div></div><div class="timeline-item"><div class="timeline-title">风控检查通过</div><div class="timeline-sub">2026-08-16 11:29</div></div><div class="timeline-item"><div class="timeline-title">支付宝出款处理中</div><div class="timeline-sub">等待通道最终结果</div></div></div></div>'
    return doc(b,bg='secure',title='提现详情',back=True,nav='me')

# profile/settings/messages
def me_page():
    actions=''.join(btn(t,kind='secondary') for t in ['充值','提现','赠送','明细'])
    menu=''.join(menu_tile(i,t) for i,t in [('identity','实名认证'),('nav_project','我的项目'),('invite','邀请好友'),('task','我的任务'),('settings','设置'),('help','帮助中心'),('wallet','收款方式'),('message','消息中心')])
    b=f'<div class="profile-hero"><img src="{AVATAR}" class="avatar-lg"><div class="profile-name">星矿小队长</div><div class="small muted">UID: 2026</div><div class="vip-pill">VIP 5 · 有效期至 2026-12-31</div></div>{asset_cards()}<div class="action-quad">{actions}</div>{sec("常用功能")}<div class="grid-menu">{menu}</div>'
    return doc(b,bg='profile',title='我的',back=False,action='settings',nav='me',root=True)

def edit_profile():
    b=panel('<div style="text-align:center"><img src="'+AVATAR+'" class="avatar-lg"><div style="margin-top:8px">'+btn('更换头像',compact=True,kind='secondary')+'</div></div>')+field('昵称','星矿小队长','nav_me')+field('个人简介','探索星际矿脉，合成更高等级矿机','order',area=True)+btn('保存资料',full=True)
    return doc(b,bg='profile',title='编辑资料',back=True,nav='me')

def messages():
    rows=''.join(list_row(i,t,s,v) for i,t,s,v in [('withdraw','提现处理中','提现单WD202608160001正在处理','刚刚'),('nav_project','项目审核通过','星际矿脉开发计划已发布','10:20'),('commission','佣金到账','一级好友消费佣金+9.90','昨天'),('message','平台公告','新版本矿场玩法说明','前天')])
    return doc('<div class="segmented"><span class="active">全部</span><span>系统</span><span>资产</span><span>项目</span></div>'+sec('消息中心','全部已读')+f'<div class="list">{rows}</div>',bg='profile',title='消息中心',back=True,nav='me')

def message_detail():
    b=panel('<div class="tiny muted">系统通知 · 2026-08-16 11:29</div><h2>提现申请已进入出款处理</h2><p class="small muted" style="line-height:1.8">您的提现申请已通过风控检查，当前由支付宝通道处理。请勿重复提交，最终结果将通过消息中心通知。</p><div class="divider"></div>'+btn('查看提现详情',full=True)+'</div>')
    return doc(b,bg='profile',title='消息详情',back=True,nav='me')

def settings_page(name,page_id):
    if page_id=='APP-SET-001':
        rows=''.join(list_row(i,t,s) for i,t,s in [('nav_me','账号与安全','密码、设备与赠送密码'),('settings','声音与通知','背景音乐、音效、震动'),('help','帮助中心','常见问题与客服'),('order','协议与隐私','用户协议、隐私政策'),('message','关于和更新','当前版本V1.3.0')])
        b=f'<div class="list">{rows}</div><div style="height:12px"></div>{btn("退出登录",kind="red-btn",full=True)}'
    elif page_id=='APP-SET-002':
        b='<div class="list">'+''.join(list_row(i,t,s) for i,t,s in [('settings','修改登录密码','邮箱验证'),('settings','赠送密码','已设置'),('nav_me','登录设备','当前2台设备'),('warning','注销账号','进入冷静期')])+'</div>'
    elif page_id=='APP-SET-003':
        b='<div class="list">'+list_row('nav_me','Windows · Chrome','新加坡 · 当前设备','在线')+list_row('nav_me','Android · 星矿纪元','新加坡 · 2小时前','退出')+'</div>'
    elif page_id=='APP-SET-004':
        b='<div class="list">'+list_row('settings','背景音乐','矿场与页面BGM','开启')+list_row('settings','游戏音效','合成、领取与操作音效','开启')+list_row('settings','震动反馈','关键交互震动','开启')+list_row('message','消息通知','系统与资产通知','开启')+'</div>'
    elif page_id=='APP-SET-005':
        b=panel('<div style="text-align:center"><img src="'+MIN+'/MINER_L36.png" style="width:130px;height:130px"><h2>星矿纪元</h2><div class="small muted">版本 V1.3.0</div><div style="height:12px"></div>'+btn('检查更新',full=True)+'</div>')
    elif page_id=='APP-SET-006':
        b='<div class="input"><img src="'+ICON['search']+'"><span>搜索常见问题</span></div>'+sec('常见问题')+'<div class="list">'+''.join(list_row('help',t,'查看答案') for t in ['如何合成矿机？','离线收益如何计算？','如何使用推广卡？','提现为什么处理中？'])+'</div>'
    elif page_id=='APP-SET-007':
        b='<div class="list">'+list_row('order','用户协议','2026-08-16更新')+list_row('order','隐私政策','2026-08-16更新')+list_row('order','实名认证说明','查看数据处理规则')+'</div>'
    else:
        b=panel('<div style="text-align:center"><img src="'+ICON['warning']+'" style="width:90px;height:90px"><h2>注销账号</h2><div class="small muted" style="line-height:1.8">注销申请提交后进入冷静期，期间可撤销。请先处理未完成订单、提现和项目任务。</div></div>')+field('邮箱验证码','输入6位验证码','message')+btn('提交注销申请',kind='red-btn',full=True)
    return doc(b,bg='profile',title=name,back=True,nav='me')

def support():
    b=field('问题类型','功能异常 / 资产问题 / 其他','help')+field('问题描述','请描述问题和复现步骤','message',area=True)+sec('截图','最多3张')+'<div class="media-grid"><div class="media-box"><img src="'+ICON['plus']+'" style="width:30px;height:30px;opacity:.6"></div></div><div style="height:12px"></div>'+btn('提交反馈',full=True)
    return doc(b,bg='profile',title='意见反馈',back=True,nav='me')

# generic dispatcher
def render_page(page_id,name,state):
    key=f'{page_id}__{state}'
    if page_id=='APP-SYS-001': return splash()
    if page_id.startswith('APP-SYS-'): return system_page(name,state)
    if page_id.startswith('APP-AUTH-'): return auth_page(name,state,page_id)
    if page_id.startswith('APP-SEC-'): return security_modal(name)
    if page_id=='APP-GAME-001': return tutorial()
    if page_id=='APP-GAME-002': return game_home(state)
    if page_id=='APP-GAME-003': return miner_store()
    if page_id=='APP-GAME-004': return warehouse()
    if page_id=='APP-GAME-005': return atlas()
    if page_id=='APP-GAME-006': return miner_detail()
    if page_id in {'APP-GAME-007','APP-GAME-008','APP-GAME-011','APP-GAME-014','APP-GAME-015','APP-GAME-016'}: return game_modal(name,page_id)
    if page_id=='APP-GAME-009': return task_center()
    if page_id=='APP-GAME-010': return sign_in()
    if page_id=='APP-GAME-012': return ranking()
    if page_id=='APP-GAME-013': return production_detail()
    if page_id=='APP-PROJ-001': return project_home(state)
    if page_id=='APP-PROJ-002': return project_search()
    if page_id=='APP-PROJ-003': return project_form()
    if page_id=='APP-PROJ-004': return project_image_manager()
    if page_id=='APP-PROJ-005': return project_result()
    if page_id=='APP-PROJ-006': return project_detail(state)
    if page_id=='APP-PROJ-007': return contact_panel()
    if page_id=='APP-PROJ-008': return project_report()
    if page_id=='APP-PROJ-009': return my_projects()
    if page_id=='APP-PROJ-010': return project_manage()
    if page_id=='APP-PROJ-011': return promotion_card()
    if page_id=='APP-PROJ-012': return promotion_history()
    if page_id=='APP-PROJ-013': return favorite_projects()
    if page_id=='APP-PROJ-014': return gallery()
    if page_id=='APP-PROJ-015': return category_selector()
    if page_id=='APP-PROJ-016': return task_campaign_form()
    if page_id=='APP-MALL-001': return mall_home()
    if page_id=='APP-MALL-002': return product_detail()
    if page_id=='APP-MALL-003': return order_confirm()
    if page_id=='APP-MALL-004': return backpack()
    if page_id=='APP-PAY-001': return pay_page(state)
    if page_id=='APP-PAY-002': return manual_pay(state)
    if page_id=='APP-PAY-003': return pay_result()
    if page_id=='APP-ORDER-001': return order_list()
    if page_id=='APP-ORDER-002': return order_detail()
    if page_id=='APP-MEMBER-001': return member_center()
    if page_id=='APP-DISC-001': return discover_container()
    if page_id=='APP-MARKET-001': return market_home()
    if page_id=='APP-MARKET-002': return buy_order_form()
    if page_id=='APP-MARKET-003': return buy_order_detail()
    if page_id=='APP-MARKET-004': return my_buy_orders()
    if page_id=='APP-DISC-002': return future_games()
    if page_id=='APP-WALLET-001': return wallet_overview()
    if page_id=='APP-WALLET-002': return transaction_list('星矿值流水')
    if page_id=='APP-WALLET-003': return transaction_list('能源芯片流水')
    if page_id=='APP-WALLET-004': return transaction_list('账户余额流水')
    if page_id=='APP-WALLET-005': return transfer_form()
    if page_id=='APP-WALLET-006': return recipient_confirm()
    if page_id=='APP-WALLET-007': return transfer_result()
    if page_id=='APP-WALLET-008': return password_form('设置赠送密码')
    if page_id=='APP-WALLET-009': return password_form('修改赠送密码')
    if page_id=='APP-WALLET-010': return exchange_chip()
    if page_id=='APP-INVITE-001': return invite_overview()
    if page_id=='APP-INVITE-002': return invite_poster()
    if page_id=='APP-INVITE-003': return friend_list('一级好友')
    if page_id=='APP-INVITE-004': return friend_list('二级好友',True)
    if page_id=='APP-INVITE-005': return superior()
    if page_id=='APP-COMM-001': return commission_list('积分提成')
    if page_id=='APP-COMM-002': return commission_list('消费佣金')
    if page_id=='APP-ID-001': return identity_entry()
    if page_id=='APP-ID-002': return identity_form()
    if page_id=='APP-ID-003': return camera_permission()
    if page_id=='APP-ID-004': return identity_capture(state)
    if page_id=='APP-ID-005': return identity_verifying(state)
    if page_id=='APP-ID-006': return identity_result(state)
    if page_id=='APP-WD-001': return withdrawal_home(state)
    if page_id=='APP-WD-002': return bind_alipay()
    if page_id=='APP-WD-003': return withdraw_confirm()
    if page_id=='APP-WD-004': return withdraw_result(state)
    if page_id=='APP-WD-005': return withdrawal_records()
    if page_id=='APP-WD-006': return withdrawal_detail()
    if page_id=='APP-ME-001': return me_page()
    if page_id=='APP-ME-002': return edit_profile()
    if page_id=='APP-MSG-001': return messages()
    if page_id=='APP-MSG-002': return message_detail()
    if page_id.startswith('APP-SET-'): return settings_page(name,page_id)
    if page_id=='APP-SUPPORT-001': return support()
    return doc(panel(f'<h2>{esc(name)}</h2><p class="small muted">页面规格已建立。</p>'),bg='business',title=name,back=True)

out=[]
for e in ENTRIES:
    fname=f"{e['page_id']}__{e['state']}.html"
    text=render_page(e['page_id'],e['name'],e['state'])
    (HTML_DIR/fname).write_text(text,encoding='utf-8')
    out.append({'platform':'APP','page_id':e['page_id'],'name':e['name'],'state':e['state'],'html':f'10_HTML/APP/{fname}'})
(ROOT/'10_HTML'/'RENDER_INDEX_V130_APP.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('generated',len(out),'html pages')
