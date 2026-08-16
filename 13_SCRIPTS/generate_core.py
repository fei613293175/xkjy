from __future__ import annotations

import json, math, os, random, shutil, textwrap
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

from page_catalog import flatten, EXTRA_STATES

BASE = Path('/mnt/data/xkjy_v110_work/XKJY_V110')
FONT_REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'

COLORS = {
    'space_950': '#07111F',
    'space_900': '#0B1830',
    'space_800': '#102A4C',
    'space_700': '#173B66',
    'primary_600': '#F0642F',
    'primary_500': '#FF7A3D',
    'primary_400': '#FF965F',
    'gold_500': '#FFC84A',
    'gold_300': '#FFE29A',
    'energy_500': '#27D5C4',
    'energy_300': '#8AF0E5',
    'blue_500': '#3A8CFF',
    'violet_500': '#8B5CFF',
    'magenta_500': '#ED5CBE',
    'surface': '#FFF9F1',
    'surface_2': '#FFFFFF',
    'surface_dark': '#11243D',
    'text_primary': '#172034',
    'text_secondary': '#68728A',
    'border': '#E8DFD3',
    'success': '#24B878',
    'warning': '#F4A62A',
    'error': '#E55454',
    'info': '#3A8CFF',
}


def ensure(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str):
    ensure(path.parent)
    path.write_text(text, encoding='utf-8')


def write_yaml(path: Path, obj):
    ensure(path.parent)
    path.write_text(yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=140), encoding='utf-8')


def font(size: int, bold: bool=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def hex_to_rgb(h: str):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))


def mix(c1: str, c2: str, t: float) -> Tuple[int,int,int]:
    a=hex_to_rgb(c1); b=hex_to_rgb(c2)
    return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))


def vertical_gradient(size, top: str, bottom: str):
    w,h=size
    im=Image.new('RGB', size)
    d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/(h-1)
        d.line([(0,y),(w,y)], fill=mix(top,bottom,t))
    return im


def starfield(im: Image.Image, seed=2026, count=140, top_fraction=0.68):
    rnd=random.Random(seed)
    d=ImageDraw.Draw(im, 'RGBA')
    w,h=im.size
    for _ in range(count):
        x=rnd.randrange(w); y=rnd.randrange(max(1,int(h*top_fraction)))
        r=rnd.choice([1,1,1,2,2,3])
        a=rnd.randrange(80,230)
        d.ellipse((x-r,y-r,x+r,y+r), fill=(255,255,255,a))
    return im


def save_png_svg(svg: str, svg_path: Path, png_path: Path, out_size=512):
    write_text(svg_path, svg)
    ensure(png_path.parent)
    cairosvg.svg2png(bytestring=svg.encode('utf-8'), write_to=str(png_path), output_width=out_size, output_height=out_size)


# ---------------------------------------------------------------------------
# Project-level structured files
# ---------------------------------------------------------------------------

def generate_project_files():
    design_tokens = {
        'meta': {
            'project': '星矿纪元', 'version': '1.1.0', 'design_system': 'XKJY-SPACE-MINE',
            'baseline': '母版V1.4.2 + 项目专属视觉扩展',
        },
        'viewport': {
            'android_design_width_dp': 360, 'android_reference_height_dp': 800,
            'android_effect_viewport_css_px': [390, 844], 'android_effect_scale': 3,
            'admin_viewport_px': [1440, 900], 'h5_viewport_css_px': [390, 844], 'h5_effect_scale': 3,
        },
        'spacing_dp': {'xxs':2,'xs':4,'sm':8,'md':12,'lg':16,'xl':20,'xxl':24,'xxxl':32},
        'radius_dp': {'xs':6,'sm':10,'md':14,'lg':18,'xl':24,'dialog':28,'pill':999},
        'typography_sp': {
            'display':30,'hero':26,'title_large':22,'title_medium':19,'title_small':17,
            'body_large':16,'body_medium':14,'body_small':12,'label':11,'micro':10,
        },
        'line_height_sp': {'display':38,'hero':34,'title_large':30,'title_medium':27,'body_large':24,'body_medium':21,'body_small':18},
        'component_height_dp': {'input':52,'primary_button':50,'secondary_button':44,'top_bar':56,'game_hud':72,'game_toolbar':68,'bottom_nav':64},
        'icon_size_dp': {'xs':14,'sm':16,'md':20,'lg':24,'xl':32,'game':40},
        'colors': COLORS,
        'gradients': {
            'space': ['#07111F','#102A4C'], 'brand': ['#FF965F','#F0642F'],
            'reward': ['#FFE29A','#FFC84A'], 'energy': ['#8AF0E5','#27D5C4'],
            'member': ['#8B5CFF','#ED5CBE'], 'panel_dark': ['#173B66','#0B1830'],
        },
        'shadow': {
            'card': {'color':'#14233A24','blur_dp':18,'offset_y_dp':8},
            'floating': {'color':'#07111F40','blur_dp':28,'offset_y_dp':12},
            'glow_gold': {'color':'#FFC84A66','blur_dp':24},
            'glow_energy': {'color':'#27D5C466','blur_dp':24},
        },
        'motion': {
            'fast_ms':120,'standard_ms':220,'emphasis_ms':420,'dialog_ms':280,
            'merge_ms':680,'unlock_ms':1200,'bubble_float_ms':1800,'stagger_ms':48,
        },
        'icon_system': {
            'policy_id':'LB-ICON','source_format':'svg','default_canvas':'24x24','minimum_touch_target_dp':48,
            'default_style':'rounded_line','selected_style':'filled_tinted_container','text_as_icon_forbidden':True,
            'icon_font_forbidden':True,'registry_required':True,
        },
        'accessibility': {'minimum_text_contrast':4.5,'minimum_large_text_contrast':3.0,'minimum_touch_target_dp':48,'supports_font_scale_up_to':1.3},
    }
    write_text(BASE/'03_SPECS/DESIGN_TOKENS.json', json.dumps(design_tokens, ensure_ascii=False, indent=2))

    project_profile = {
        'project': {'name_cn':'星矿纪元','code':'XKJY','package_name':'cc.orbexa.xkjy','version':'1.1.0','date':'2026-08-16'},
        'platforms': {'android':True,'admin_web':True,'h5':True,'ios':False,'desktop_user_web':False},
        'stack': {
            'android':['Kotlin','Jetpack Compose','Material 3','CameraX','Media3','SoundPool','Room','DataStore'],
            'backend':['Go','PostgreSQL','Redis','Outbox Worker','Docker Compose','Nginx'],
            'admin':['Vue 3','TypeScript','Vite','Pinia'],
        },
        'domains': {
            'api':'xkjy-api.orbexa.cc','admin':'xkjy-admin.orbexa.cc','h5':'xkjy-h5.orbexa.cc',
            'invite':'xkjy-yq.orbexa.cc','download':'xkjy-download.orbexa.cc','assets':'oss.orbexa.cc',
        },
        'timezone':'Asia/Shanghai',
        'uid': {'type':'numeric','sequence_start':2026,'invite_code_same_as_uid':True},
        'business_mode_frozen': True,
        'visual_source_of_truth': '04_UI + 10_HTML + 03_SPECS/pages',
    }
    write_yaml(BASE/'03_SPECS/PROJECT_PROFILE.yaml', project_profile)

    modules = [
        ('account',True,'邮箱注册/登录/找回/会话'),('email',True,'母版SMTP能力'),('captcha',True,'自研图形验证码'),
        ('identity',True,'母版阿里云人证比对'),('storage',True,'母版Cloudflare R2'),('payment',True,'母版XApay与人工扫码'),
        ('withdrawal',True,'母版支付宝证书出款'),('wallet_ledger',True,'三资产事务账本'),('game_merge',True,'36级矿机合成'),
        ('project_promotion',True,'用户项目与推广道具'),('market',True,'积分求购集市'),('referral_commission',True,'二级提成'),
        ('physical_goods',False,'明确禁止实物'),('sms',False,'只使用邮箱'),('ios',False,'当前不开发'),('instant_chat',False,'当前不开发'),
        ('third_party_ad_network',False,'当前广告指平台项目任务'),('extra_games',False,'仅预留发现入口'),
    ]
    write_yaml(BASE/'03_SPECS/MODULE_SELECTION.yaml', {
        'project':'星矿纪元','version':'1.1.0','mother_template':'V1.4.2',
        'modules':[{'module_id':m,'enabled':e,'reason':r} for m,e,r in modules],
        'rule_priority':['项目所有者最新明确指令','项目专属规则','母版全局规则','启用模块默认规则','参考截图'],
    })

    resolved = {
        'project':'星矿纪元','version':'1.1.0','ruleset':'XKJY_RESOLVED_20260816',
        'global_rules':'G-001~G-047全部启用','lightweight_baseline':'LIGHTWEIGHT_COMPLETE',
        'fixed_integrations':['identity','payment','cloudflare_r2','email','withdrawal'],
        'hard_rules':[
            '商业模式按用户当前定义实现，不擅自替换','母版私有配置直接复用，不再次索取密钥或账号',
            '首页必须是矿机合成游戏场景','所有资产变化必须经过事务账本','所有关键写操作必须幂等',
            '所有页面返回保持滚动、Tab、筛选、分页、草稿和已加载内容','禁止文字、Emoji和Icon Font代替图标',
            '每个Page ID按独立效果图和页面规格实现','每个Android版本交付签名APK、功能清单和测试清单',
        ],
    }
    write_yaml(BASE/'03_SPECS/RESOLVED_RULESET.yaml', resolved)

    write_yaml(BASE/'03_SPECS/DOMAIN_PLAN.yaml', {'domains':project_profile['domains'],'ssl_required':True,'dns_pending_is_not_local_dev_blocker':True})
    write_yaml(BASE/'03_SPECS/CURRENT_RELEASE.yaml', {'project':'星矿纪元','package_version':'1.1.0','development_release':'P00','status':'READY_FOR_CODEX','next_release':'P01'})
    write_yaml(BASE/'03_SPECS/LIGHTWEIGHT_BASELINE_RESOLUTION.yaml', {
        'profile':'LIGHTWEIGHT_COMPLETE','enabled':['standard_api','captcha','release_signing','db_migration','backup','structured_logs','health_checks','config_center','idempotency','page_state_retention','icon_registry'],
        'excluded_heavy_governance':['Governance V5.0','multi-stage approval gates','unbounded documentation loops'],
    })

    feature_matrix = {
        'project':'星矿纪元','version':'1.1.0','features':[
            {'feature_id':'F-ACCOUNT','name':'邮箱账号与会话','release':'P01','enabled':True},
            {'feature_id':'F-GAME-CORE','name':'矿机合成核心','release':'P02','enabled':True},
            {'feature_id':'F-GAME-GROWTH','name':'36级成长与任务','release':'P03','enabled':True},
            {'feature_id':'F-PROJECT','name':'项目发布与信息流','release':'P04','enabled':True},
            {'feature_id':'F-PROJECT-TASK','name':'浏览任务与推广服务','release':'P05','enabled':True},
            {'feature_id':'F-MALL','name':'商城会员与统一订单','release':'P06','enabled':True},
            {'feature_id':'F-PAYMENT','name':'XApay与人工扫码','release':'P07','enabled':True},
            {'feature_id':'F-WALLET-MARKET','name':'三资产账本、赠送、集市、红包卡','release':'P08','enabled':True},
            {'feature_id':'F-REFERRAL','name':'邀请与二级提成','release':'P09','enabled':True},
            {'feature_id':'F-ID-WD','name':'实名认证与提现','release':'P10','enabled':True},
            {'feature_id':'F-RELEASE','name':'消息、设置、更新与正式发布','release':'P11','enabled':True},
        ]
    }
    write_yaml(BASE/'03_SPECS/FEATURE_MATRIX.yaml', feature_matrix)

    # Compact version plan for Codex state tracking.
    releases=[]
    for code,name,goal in [
        ('P00','项目基线','仓库、Docker、数据库、Android壳、后台壳、规则解析和健康检查'),
        ('P01','账号安全','邮箱注册、密码/验证码登录、找回、会话、自研图形验证码'),
        ('P02','游戏核心竖切','新手、4×4棋盘、1~6级、购买、拖动、合成、产出、领取、离线收益'),
        ('P03','完整游戏成长','7~36级、仓库、图鉴、任务、签到、补给箱、排行榜'),
        ('P04','项目平台','分类、发布、审核、信息流、详情、收藏、举报'),
        ('P05','项目任务与推广','浏览任务、心跳、自动奖励、头条、置顶、刷新'),
        ('P06','商城会员订单','虚拟商品、会员、背包、统一订单、权益处理器'),
        ('P07','支付','原生收银台、XApay、人工扫码、回调、查单、对账'),
        ('P08','钱包与集市','三资产账本、积分兑换、赠送、价格曲线、求购单、红包卡'),
        ('P09','邀请与佣金','邀请关系、海报、一级二级好友、积分提成、消费佣金'),
        ('P10','实名与提现','CameraX采集、人证比对、支付宝绑定、档位提现、证书出款'),
        ('P11','发布候选','消息、设置、更新、全后台、真机回归、正式签名APK'),
    ]:
        releases.append({'release':code,'name':name,'goal':goal,'deliverables':['APK（涉及Android时）','功能完成清单','测试清单','已知问题','数据库迁移','页面截图']})
    write_yaml(BASE/'03_SPECS/RELEASE_PLAN.yaml', {'project':'星矿纪元','releases':releases})


# ---------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------
ICON_ITEMS = [
('ICON-NAV-HOME','首页','home'),('ICON-NAV-PROJECT','项目','project'),('ICON-NAV-MALL','商城','mall'),('ICON-NAV-DISCOVER','发现','discover'),('ICON-NAV-ME','我的','user'),
('ICON-ACTION-BACK','返回','back'),('ICON-ACTION-SEARCH','搜索','search'),('ICON-ACTION-CLOSE','关闭','close'),('ICON-ACTION-MORE','更多','more'),('ICON-ACTION-SETTINGS','设置','settings'),
('ICON-NOTIFICATION','通知','notification'),('ICON-MAIL','邮箱','mail'),('ICON-LOCK','安全锁','lock'),('ICON-USER','用户','user'),('ICON-EDIT','编辑','edit'),('ICON-CHECK','完成','check'),
('ICON-CHEVRON-RIGHT','进入','chevron'),('ICON-UPLOAD','上传','upload'),('ICON-CAMERA','相机','camera'),('ICON-IMAGE','图片','image'),('ICON-LINK','链接','link'),('ICON-CONTACT','联系','contact'),
('ICON-HEART','收藏','heart'),('ICON-HEART-FILL','已收藏','heart_fill'),('ICON-REPORT','举报','report'),('ICON-SHARE','分享','share'),('ICON-QR','二维码','qr'),('ICON-DOWNLOAD','下载','download'),('ICON-COPY','复制','copy'),
('ICON-WALLET','钱包','wallet'),('ICON-STAR-POINT','星矿值','coin'),('ICON-ENERGY-CHIP','能源芯片','energy'),('ICON-CASH','账户余额','cash'),('ICON-TRANSFER','赠送','transfer'),('ICON-EXCHANGE','兑换','exchange'),
('ICON-INVITE','邀请','invite'),('ICON-USERS','好友','users'),('ICON-LEVEL','等级','level'),('ICON-MEMBER','会员','crown'),('ICON-MINER','矿机','miner'),('ICON-MINER-STORE','矿机商店','store'),('ICON-WAREHOUSE','仓库','warehouse'),
('ICON-ATLAS','图鉴','atlas'),('ICON-TASK','任务','task'),('ICON-SIGNIN','签到','signin'),('ICON-BOX','补给箱','box'),('ICON-RANK','排行榜','rank'),('ICON-RECYCLE','回收','recycle'),('ICON-ORGANIZE','整理','organize'),
('ICON-VOLUME','音效','volume'),('ICON-VOLUME-OFF','静音','volume_off'),('ICON-VIBRATE','震动','vibrate'),('ICON-SECURITY','安全','security'),('ICON-IDENTITY','实名','identity'),
('ICON-PAY-ALIPAY','支付宝','alipay'),('ICON-PAY-WECHAT','微信支付','wechat'),('ICON-PAY-QQ','QQ支付','qq'),('ICON-PAY-CARD','支付','payment'),('ICON-ORDER','订单','order'),
('ICON-FILTER','筛选','filter'),('ICON-SORT','排序','sort'),('ICON-CALENDAR','日期','calendar'),('ICON-CLOCK','时间','clock'),('ICON-CHART','图表','chart'),('ICON-HELP','帮助','help'),
('ICON-LOGOUT','退出','logout'),('ICON-DELETE','删除','delete'),('ICON-MESSAGE','消息','message'),('ICON-PROFILE','资料','profile'),('ICON-REFRESH','刷新','refresh'),('ICON-PIN','置顶','pin'),('ICON-HEADLINE','头条','headline'),
]


def svg_icon(kind: str, stroke='#172034', fill='none') -> str:
    common='stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"'
    paths=''
    if kind=='home': paths='<path d="M3 10.5 12 3l9 7.5V21h-6v-6H9v6H3z"/>'
    elif kind=='project': paths='<rect x="4" y="3" width="16" height="18" rx="3"/><path d="M8 8h8M8 12h8M8 16h5"/>'
    elif kind=='mall' or kind=='store': paths='<path d="M4 9h16l-1 12H5zM7 9V7a5 5 0 0 1 10 0v2"/>'
    elif kind=='discover': paths='<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2.2 4.8-4.8 2.2 2.2-4.8z"/>'
    elif kind in ('user','profile'): paths='<circle cx="12" cy="8" r="4"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0"/>'
    elif kind=='back': paths='<path d="m15 18-6-6 6-6"/>'
    elif kind=='search': paths='<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>'
    elif kind=='close': paths='<path d="M5 5l14 14M19 5 5 19"/>'
    elif kind=='more': paths='<circle cx="5" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="19" cy="12" r="1" fill="currentColor"/>'
    elif kind=='settings': paths='<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4v-.2a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1z"/>'
    elif kind=='notification': paths='<path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 8h18c0-1-3-1-3-8M10 21h4"/>'
    elif kind=='mail': paths='<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/>'
    elif kind=='lock': paths='<rect x="5" y="10" width="14" height="11" rx="3"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>'
    elif kind=='edit': paths='<path d="m4 20 4.5-1 10-10-3.5-3.5-10 10zM14 6.5l3.5 3.5"/>'
    elif kind=='check': paths='<path d="m4 12 5 5L20 6"/>'
    elif kind=='chevron': paths='<path d="m9 5 7 7-7 7"/>'
    elif kind=='upload': paths='<path d="M12 16V3m0 0-5 5m5-5 5 5M4 15v6h16v-6"/>'
    elif kind=='download': paths='<path d="M12 3v13m0 0 5-5m-5 5-5-5M4 15v6h16v-6"/>'
    elif kind=='camera': paths='<path d="M4 7h4l1.5-2h5L16 7h4v13H4z"/><circle cx="12" cy="13" r="4"/>'
    elif kind=='image': paths='<rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="8" cy="9" r="2"/><path d="m4 18 5-5 4 4 3-3 4 4"/>'
    elif kind=='link': paths='<path d="M9.5 14.5 14.5 9M7 17H5a4 4 0 0 1 0-8h4M17 7h2a4 4 0 0 1 0 8h-4"/>'
    elif kind in ('contact','message'): paths='<path d="M4 4h16v12H8l-4 4z"/><path d="M8 9h8M8 12h5"/>'
    elif kind.startswith('heart'): paths='<path d="M12 21S3 15.5 3 9.5A4.5 4.5 0 0 1 12 7a4.5 4.5 0 0 1 9 2.5C21 15.5 12 21 12 21z"/>'
    elif kind=='report': paths='<path d="M5 21V4m0 1h11l-2 4 2 4H5"/>'
    elif kind=='share': paths='<circle cx="5" cy="12" r="2"/><circle cx="18" cy="5" r="2"/><circle cx="18" cy="19" r="2"/><path d="m7 11 9-5M7 13l9 5"/>'
    elif kind=='qr': paths='<path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM15 14h2v2h-2zM19 14h2v5h-2zM14 19h4v2h-4z"/>'
    elif kind=='copy': paths='<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V4H4v12h4"/>'
    elif kind=='wallet': paths='<path d="M3 6h15v14H3zM3 8l3-4h13v4M15 12h6v5h-6a2.5 2.5 0 1 1 0-5z"/>'
    elif kind=='coin': paths='<circle cx="12" cy="12" r="9"/><path d="m12 6 1.7 3.5 3.8.6-2.7 2.7.7 3.8-3.5-1.8-3.5 1.8.7-3.8-2.7-2.7 3.8-.6z"/>'
    elif kind=='energy': paths='<path d="m13 2-8 12h6l-1 8 9-13h-6z"/>'
    elif kind=='cash': paths='<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 9h.01M18 15h.01"/>'
    elif kind=='transfer': paths='<path d="M4 7h13m0 0-4-4m4 4-4 4M20 17H7m0 0 4 4m-4-4 4-4"/>'
    elif kind=='exchange' or kind=='refresh': paths='<path d="M20 7v5h-5M4 17v-5h5M18 12a6 6 0 0 0-10-4L4 12M6 12a6 6 0 0 0 10 4l4-4"/>'
    elif kind=='invite': paths='<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0M18 8v8M14 12h8"/>'
    elif kind=='users': paths='<circle cx="8" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M2 21a6 6 0 0 1 12 0M14 16a5 5 0 0 1 8 5"/>'
    elif kind=='level': paths='<path d="M4 20V12h4v8M10 20V7h4v13M16 20V3h4v17"/>'
    elif kind=='crown': paths='<path d="m3 7 4 4 5-7 5 7 4-4-2 12H5z"/><path d="M6 22h12"/>'
    elif kind=='miner': paths='<path d="M4 17h11V8H7l-3 4zM15 11h4l2 3-2 3h-4M7 17v3M12 17v3"/><path d="m19 14 3-2M19 14l3 2"/>'
    elif kind=='warehouse': paths='<path d="m3 9 9-6 9 6v12H3zM7 21v-8h10v8M8 9h8"/>'
    elif kind=='atlas': paths='<path d="M4 4h6a4 4 0 0 1 4 4v12H8a4 4 0 0 0-4 1zM20 4h-6a4 4 0 0 0-4 4"/>'
    elif kind=='task': paths='<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2h6v2M8 10l2 2 4-4M8 16h8"/>'
    elif kind=='signin' or kind=='calendar': paths='<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18M8 15l2 2 5-5"/>'
    elif kind=='box': paths='<path d="m4 8 8-4 8 4-8 4zM4 8v9l8 4 8-4V8M12 12v9"/>'
    elif kind=='rank': paths='<path d="M7 4h10v6a5 5 0 0 1-10 0zM7 6H3v2a4 4 0 0 0 4 4M17 6h4v2a4 4 0 0 1-4 4M12 15v4M8 21h8"/>'
    elif kind=='recycle': paths='<path d="m8 5 3-3 3 3M11 2v6M19 10l3 3-3 3M22 13h-6M5 19l-3-3 3-3M2 16h6"/><path d="M8 8a6 6 0 0 1 10 3M16 16a6 6 0 0 1-10-3"/>'
    elif kind=='organize': paths='<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>'
    elif kind.startswith('volume'): paths='<path d="M4 10h4l5-4v12l-5-4H4zM17 9a4 4 0 0 1 0 6M19 6a8 8 0 0 1 0 12"/>'
    elif kind=='vibrate': paths='<rect x="8" y="3" width="8" height="18" rx="2"/><path d="M4 7v10M20 7v10M2 9v6M22 9v6"/>'
    elif kind=='security': paths='<path d="M12 2 4 5v6c0 5 3 8 8 11 5-3 8-6 8-11V5z"/><path d="m8 12 3 3 5-6"/>'
    elif kind=='identity': paths='<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8" cy="11" r="2"/><path d="M5 16a3 3 0 0 1 6 0M13 9h5M13 13h5"/>'
    elif kind=='payment': paths='<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 9h18M7 15h4"/>'
    elif kind=='order': paths='<path d="M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6M9 16h4"/>'
    elif kind=='filter': paths='<path d="M3 5h18l-7 8v6l-4 2v-8z"/>'
    elif kind=='sort': paths='<path d="M8 4v16m0 0-4-4m4 4 4-4M16 20V4m0 0-4 4m4-4 4 4"/>'
    elif kind=='clock': paths='<circle cx="12" cy="12" r="9"/><path d="M12 7v5l4 2"/>'
    elif kind=='chart': paths='<path d="M4 20V4M4 20h16M7 16l4-5 3 2 5-7"/>'
    elif kind=='help': paths='<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.7 2.7 0 1 1 4 2.4c-1.2.7-1.5 1.2-1.5 2.6M12 18h.01"/>'
    elif kind=='logout': paths='<path d="M10 4H4v16h6M14 8l4 4-4 4M8 12h10"/>'
    elif kind=='delete': paths='<path d="M4 7h16M9 7V4h6v3M7 7l1 14h8l1-14M10 11v6M14 11v6"/>'
    elif kind=='pin': paths='<path d="M8 3h8l-1 6 3 3v2H6v-2l3-3zM12 14v8"/>'
    elif kind=='headline': paths='<path d="M3 11h4l9-5v12l-9-5H3zM7 13v6h4"/><path d="M19 9l2-2M19 15l2 2"/>'
    elif kind=='alipay':
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="6" fill="#1677FF"/><path d="M5 8h14M8 5v8c0 4-2 6-4 7M7 14c4 0 8 1 12 5M13 8c0 5-2 9-7 12" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/></svg>'
    elif kind=='wechat':
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="6" fill="#16B855"/><ellipse cx="9" cy="10" rx="6" ry="4.5" fill="#fff"/><ellipse cx="16" cy="14" rx="5" ry="4" fill="#fff"/><path d="m5 13-1 3 3-2M19 17l1 3-3-2" fill="#fff"/><circle cx="7" cy="9" r=".7" fill="#16B855"/><circle cx="11" cy="9" r=".7" fill="#16B855"/><circle cx="14.5" cy="13" r=".6" fill="#16B855"/><circle cx="17.5" cy="13" r=".6" fill="#16B855"/></svg>'
    elif kind=='qq':
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="6" fill="#2B7DE9"/><path d="M12 4c-3 0-5 3-5 7v2l-2 3 2 1 1-1c1 2 2 3 4 3s3-1 4-3l1 1 2-1-2-3v-2c0-4-2-7-5-7z" fill="#fff"/><ellipse cx="10" cy="10" rx=".7" ry="1" fill="#2B7DE9"/><ellipse cx="14" cy="10" rx=".7" ry="1" fill="#2B7DE9"/><path d="M9 14h6" stroke="#F6B700" stroke-width="1.2"/><path d="M9 20h6" stroke="#F05A4F" stroke-width="2"/></svg>'
    else: paths='<path d="m12 3 8 4v10l-8 4-8-4V7z"/><circle cx="12" cy="12" r="2"/>'
    fill_attr = 'currentColor' if kind=='heart_fill' else fill
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{fill_attr}" color="{stroke}" stroke="currentColor" {common}>{paths}</svg>'


def generate_icons():
    src=BASE/'07_GAME_ASSETS/objects/icons'
    ensure(src)
    registry=[]
    for icon_id, semantic, kind in ICON_ITEMS:
        svg=svg_icon(kind)
        p=src/f'{icon_id}.svg'
        write_text(p,svg)
        registry.append({
            'icon_id':icon_id,'semantic_name_cn':semantic,
            'role':'brand' if kind in ('alipay','wechat','qq') else ('project_specific' if kind in ('coin','energy','miner','headline','pin') else 'functional'),
            'source_type':'custom_svg','source_name':kind,'source_svg_file':str(p.relative_to(BASE)).replace('\\','/'),
            'android_resource':f'app/src/main/res/drawable/{icon_id.lower().replace("-","_")}.xml',
            'web_resource':f'admin/src/assets/icons/{icon_id}.svg','style':'brand' if kind in ('alipay','wechat','qq') else 'rounded_line',
            'default_size_dp':24,'touch_target_dp':48,'color_token':'icon.primary','accessibility':{'decorative':False,'label_cn':semantic},
        })
    write_yaml(BASE/'03_SPECS/ICON_REGISTRY.yaml', {
        'project':'星矿纪元','profile':'LB-ICON','default_functional_library':'project_custom_svg','icons':registry,
        'validation':{'text_as_icon_found':[],'icon_font_found':[],'missing_source_files':[],'mixed_unapproved_families':[],'missing_accessibility_labels':[]},
    })


# ---------------------------------------------------------------------------
# Miner art and brand assets
# ---------------------------------------------------------------------------
STAGES = [
    ('原始采矿','#FFB14A','#E85D28','#6B3B26'),
    ('机械工业','#FF835E','#B93B32','#4E2C38'),
    ('智能矿业','#5CD6E8','#2577C8','#173B66'),
    ('等离子时代','#B37CFF','#6E3DD6','#2D245E'),
    ('星际采矿','#FFD45F','#3D8CFF','#173B66'),
    ('量子矿业','#F5F8FF','#52DCD1','#6C4DFF'),
]
MINER_NAMES = [
'初级钻探机','双钻采矿机','履带采矿车','蒸汽钻井机','磁力采集机','重型碎岩机',
'自动矿车','齿轮钻塔','联合作业机','深层掘进机','熔岩采矿机','工业核心机',
'智能勘探机','无人采矿车','多轴机械臂','晶脉扫描器','激光切矿机','智能矿业中枢',
'等离子钻机','悬浮采矿机','能量脉冲机','深空裂岩机','核聚变采矿机','等离子矿业站',
'星港采矿艇','陨石捕获器','轨道采矿台','星尘提炼机','行星钻探舰','星际矿业母舰',
'量子勘探核心','空间折叠钻机','暗物质采集器','恒星能量井','银河采矿矩阵','纪元量子核心']


def miner_svg(level: int) -> str:
    stage=(level-1)//6
    within=(level-1)%6+1
    stage_name,c1,c2,c3=STAGES[stage]
    nodes=within
    defs=f'''<defs>
      <linearGradient id="body" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
      <radialGradient id="core"><stop offset="0" stop-color="#fff"/><stop offset=".35" stop-color="{c1}"/><stop offset="1" stop-color="{c3}"/></radialGradient>
      <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#07111f" flood-opacity=".38"/></filter>
      <filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>'''
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">{defs}<g filter="url(#shadow)">']
    # Ground shadow
    out.append('<ellipse cx="256" cy="424" rx="150" ry="28" fill="#07111f" opacity=".24"/>')
    if stage==0:
        out += [
            '<g stroke="#4A2B28" stroke-width="12" stroke-linejoin="round">',
            '<rect x="115" y="238" width="255" height="130" rx="40" fill="url(#body)"/>',
            '<path d="M105 318H70l-28-34 28-34h35" fill="#FFD45F"/>',
            f'<path d="M42 284 10 {284-12*within} 10 {284+12*within}z" fill="#F8E7B0"/>',
            '<rect x="165" y="188" width="128" height="78" rx="30" fill="#F7D38E"/>',
            '<circle cx="180" cy="386" r="42" fill="#2D3343"/><circle cx="180" cy="386" r="17" fill="#FFB14A"/>',
            '<circle cx="320" cy="386" r="42" fill="#2D3343"/><circle cx="320" cy="386" r="17" fill="#FFB14A"/>',
            '</g>'
        ]
    elif stage==1:
        out += [
            '<g stroke="#4E2C38" stroke-width="11" stroke-linejoin="round">',
            '<path d="M105 330h285l-25 70H130z" fill="#323846"/>',
            '<rect x="95" y="210" width="280" height="140" rx="28" fill="url(#body)"/>',
            '<rect x="145" y="150" width="145" height="85" rx="22" fill="#FFB96E"/>',
            '<path d="M375 250h60l48 38-48 38h-60" fill="#FFC84A"/>',
            f'<path d="m483 288 25 {-15-within*3}v{30+within*6}z" fill="#FFF0B2"/>',
            '<path d="M130 375h230" stroke="#FF835E" stroke-width="28" stroke-dasharray="28 18"/>',
            '</g>'
        ]
    elif stage==2:
        out += [
            '<g stroke="#173B66" stroke-width="10" stroke-linejoin="round">',
            '<rect x="100" y="245" width="300" height="125" rx="45" fill="url(#body)"/>',
            '<path d="M160 245v-70h120v70" fill="#C9F7F4"/>',
            '<circle cx="220" cy="210" r="28" fill="url(#core)" filter="url(#glow)"/>',
            '<path d="M300 245v-65h65l30 30-30 35" fill="#79E8E0"/>',
            '<path d="M395 275h70l35 32-35 32h-70" fill="#3A8CFF"/>',
            '<path d="M130 370v35M190 370v35M310 370v35M370 370v35"/>',
            '</g>'
        ]
    elif stage==3:
        out += [
            '<g stroke="#2D245E" stroke-width="10" stroke-linejoin="round">',
            '<ellipse cx="250" cy="390" rx="170" ry="35" fill="#6E3DD6" opacity=".42" filter="url(#glow)"/>',
            '<path d="M100 300 160 200h190l65 100-45 80H145z" fill="url(#body)"/>',
            '<circle cx="255" cy="282" r="70" fill="url(#core)" filter="url(#glow)"/>',
            '<path d="M420 270h60l25 25-25 25h-60" fill="#ED5CBE"/>',
            '<path d="M125 350h250" stroke="#D6C2FF" stroke-width="8" stroke-dasharray="10 16"/>',
            '</g>'
        ]
    elif stage==4:
        out += [
            '<g stroke="#173B66" stroke-width="10" stroke-linejoin="round">',
            '<path d="M80 330 150 190h210l80 140-95 70H170z" fill="url(#body)"/>',
            '<path d="M160 190 215 120h90l55 70" fill="#D9EDFF"/>',
            '<ellipse cx="260" cy="245" rx="85" ry="55" fill="#07111F"/><ellipse cx="260" cy="245" rx="62" ry="36" fill="url(#core)" filter="url(#glow)"/>',
            '<path d="M440 300h55l15 30-15 30h-55" fill="#FFC84A"/>',
            '<path d="M130 390h250" stroke="#3A8CFF" stroke-width="18" stroke-dasharray="30 14"/>',
            '</g>'
        ]
    else:
        out += [
            '<g stroke="#392C74" stroke-width="9" stroke-linejoin="round">',
            '<circle cx="256" cy="278" r="120" fill="url(#body)" opacity=".92"/>',
            '<circle cx="256" cy="278" r="68" fill="url(#core)" filter="url(#glow)"/>',
            '<ellipse cx="256" cy="278" rx="185" ry="72" fill="none" stroke="#52DCD1" stroke-width="12" transform="rotate(-18 256 278)"/>',
            '<ellipse cx="256" cy="278" rx="165" ry="58" fill="none" stroke="#8B5CFF" stroke-width="8" transform="rotate(28 256 278)"/>',
            '<path d="M100 390h312l-32 45H132z" fill="#172A50"/>',
            '</g>'
        ]
    # attachments/nodes for intra-stage differentiation
    for i in range(nodes):
        angle=math.pi*(0.15 + 0.7*(i/max(1,nodes-1)))
        x=256+150*math.cos(angle); y=300-120*math.sin(angle)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{8+stage}" fill="{c1}" stroke="#fff" stroke-width="4" filter="url(#glow)"/>')
    if within>=4:
        out.append(f'<path d="M180 165 Q256 {100-within*3} 332 165" fill="none" stroke="{c1}" stroke-width="10" stroke-linecap="round"/>')
    if within>=5:
        out.append(f'<circle cx="256" cy="130" r="22" fill="url(#core)" filter="url(#glow)"/>')
    if within==6:
        out.append(f'<ellipse cx="256" cy="278" rx="205" ry="170" fill="none" stroke="{c1}" stroke-width="5" stroke-dasharray="14 22" opacity=".8"/>')
    out.append('</g></svg>')
    return ''.join(out)


def generate_miners():
    manifest=[]
    for level in range(1,37):
        svg=miner_svg(level)
        code=f'MINER_L{level:02d}'
        save_png_svg(svg, BASE/f'06_MINERS/SVG/{code}.svg', BASE/f'06_MINERS/PNG/{code}.png', 512)
        stage=(level-1)//6
        # Formula frozen from V1.0 functional doc.
        production=0.05*(2.05**(level-1))
        base_price=1.00*(2.20**(level-1))
        manifest.append({
            'miner_id':code,'level':level,'name_cn':MINER_NAMES[level-1],'stage':STAGES[stage][0],
            'production_per_hour_seed':f'{production:.8f}','base_purchase_price_seed':f'{base_price:.8f}',
            'svg':f'06_MINERS/SVG/{code}.svg','png':f'06_MINERS/PNG/{code}.png',
            'idle_vfx':f'08_VFX/miner_idle/{code}_IDLE.png','work_vfx':f'08_VFX/miner_work/{code}_WORK.png',
        })
    write_yaml(BASE/'06_MINERS/MINER_MANIFEST.yaml', {'project':'星矿纪元','max_level':36,'items':manifest})
    write_text(BASE/'06_MINERS/README.md', '# 36级矿机素材\n\n每级提供独立 SVG、512×512 透明 PNG、待机与工作动效精灵图。运行时名称、产出和价格以后端配置为准，`miner_id` 与等级不可修改。\n')


def draw_logo(size=1024):
    im=vertical_gradient((size,size), COLORS['space_900'], COLORS['space_700']).convert('RGBA')
    d=ImageDraw.Draw(im,'RGBA')
    # stars
    starfield(im,2026,90,1.0)
    cx=cy=size//2
    # orbit rings
    for w,a in [(18,150),(7,100)]:
        box=(size*.18,size*.27,size*.82,size*.73)
        d.arc(box,200,520,fill=hex_to_rgb(COLORS['energy_500'])+(a,),width=w)
    # hex asteroid
    r=size*.23
    pts=[]
    for i in range(6):
        a=math.radians(30+i*60)
        pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    d.polygon(pts, fill=hex_to_rgb(COLORS['primary_500'])+(255,), outline=hex_to_rgb(COLORS['gold_500'])+(255,))
    # central core
    d.ellipse((cx-size*.12,cy-size*.12,cx+size*.12,cy+size*.12), fill=hex_to_rgb(COLORS['gold_500'])+(255,))
    d.ellipse((cx-size*.065,cy-size*.065,cx+size*.065,cy+size*.065), fill=(255,249,220,255))
    # drill / pick silhouette
    d.rounded_rectangle((cx-size*.035,cy-size*.28,cx+size*.035,cy+size*.20), radius=size*.025, fill=hex_to_rgb(COLORS['space_900'])+(255,))
    d.polygon([(cx-size*.23,cy-size*.20),(cx+size*.23,cy-size*.20),(cx+size*.10,cy-size*.10),(cx-size*.10,cy-size*.10)], fill=hex_to_rgb(COLORS['space_900'])+(255,))
    # small orbital nodes
    for a,col in [(25,COLORS['gold_500']),(155,COLORS['energy_500']),(275,COLORS['primary_400'])]:
        rad=math.radians(a)
        x=cx+size*.31*math.cos(rad); y=cy+size*.22*math.sin(rad)
        rr=size*.027
        d.ellipse((x-rr,y-rr,x+rr,y+rr), fill=hex_to_rgb(col)+(255,), outline=(255,255,255,220), width=max(2,size//180))
    return im


def make_background(name: str, top: str, bottom: str, seed: int, mine=False, project=False, mall=False):
    im=vertical_gradient((1170,1600),top,bottom).convert('RGBA')
    starfield(im,seed,170,0.72)
    d=ImageDraw.Draw(im,'RGBA')
    # planet and nebula
    d.ellipse((760,90,1120,450), fill=(48,110,190,70), outline=(120,220,255,100), width=8)
    d.ellipse((820,145,1060,385), fill=(255,170,80,30))
    # distant mountains
    rnd=random.Random(seed)
    ridge=[]
    for x in range(-50,1220,110): ridge.append((x,760-rnd.randrange(30,210)))
    ridge += [(1220,980),(-50,980)]
    d.polygon(ridge, fill=(19,52,82,220))
    ridge2=[]
    for x in range(-50,1220,130): ridge2.append((x,860-rnd.randrange(20,140)))
    ridge2 += [(1220,1040),(-50,1040)]
    d.polygon(ridge2, fill=(28,78,94,240))
    if mine:
        # mine floor and crystals
        d.rectangle((0,900,1170,1600), fill=(44,43,52,255))
        for y in range(930,1600,90): d.line((0,y,1170,y), fill=(255,255,255,10), width=2)
        for x in range(0,1170,120): d.line((x,900,x-120,1600), fill=(255,255,255,8), width=2)
        for i in range(14):
            x=rnd.randrange(30,1140); y=rnd.randrange(960,1500); h=rnd.randrange(35,100)
            col=hex_to_rgb(COLORS['energy_500'])+(190,)
            d.polygon([(x,y),(x+18,y-h),(x+35,y)], fill=col)
            d.ellipse((x-15,y-5,x+50,y+12), fill=(39,213,196,30))
        # pipes/platforms
        d.rounded_rectangle((70,1030,1100,1540), radius=70, fill=(14,31,49,175), outline=(87,152,173,90), width=7)
        d.line((140,1000,140,1540), fill=(241,100,47,120), width=18)
        d.line((1030,1000,1030,1540), fill=(39,213,196,100), width=18)
    if project:
        d.rectangle((0,1010,1170,1600), fill=(237,244,248,255))
        # futuristic billboards
        for x,y,w,h in [(90,1040,280,180),(410,1090,300,210),(760,1020,300,190)]:
            d.rounded_rectangle((x,y,x+w,y+h), radius=24, fill=(255,255,255,235), outline=(58,140,255,80), width=5)
            d.line((x+28,y+55,x+w-28,y+55), fill=(58,140,255,110), width=8)
    if mall:
        d.rectangle((0,900,1170,1600), fill=(255,245,227,255))
        d.polygon([(0,900),(1170,900),(1080,1050),(90,1050)], fill=(255,122,61,220))
        for i in range(5):
            x=100+i*210
            d.rounded_rectangle((x,1080,x+170,1400), radius=30, fill=(255,255,255,240), outline=(255,200,74,100), width=5)
    path=BASE/f'07_GAME_ASSETS/backgrounds/{name}.png'
    ensure(path.parent); im.convert('RGB').save(path,quality=95)


def generate_brand_and_backgrounds():
    logo=draw_logo(1024)
    # Standalone launcher icon must be fully opaque, not a transparent foreground requiring user-side cropping.
    opaque_logo=Image.alpha_composite(Image.new('RGBA',logo.size,(11,24,48,255)),logo).convert('RGB')
    opaque_logo.save(BASE/'05_BRAND/app_icon/app_icon_1024.png')
    opaque_logo.resize((512,512),Image.Resampling.LANCZOS).save(BASE/'05_BRAND/app_icon/app_icon_512.png')
    for name,size in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
        p=BASE/f'05_BRAND/app_icon/{name}/ic_launcher.png'; ensure(p.parent); opaque_logo.resize((size,size),Image.Resampling.LANCZOS).save(p)
    # logo SVG source
    logo_svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#0B1830"/><stop offset="1" stop-color="#173B66"/></linearGradient></defs><rect width="1024" height="1024" rx="220" fill="url(#g)"/><ellipse cx="512" cy="512" rx="330" ry="190" fill="none" stroke="#27D5C4" stroke-width="18" transform="rotate(-12 512 512)"/><polygon points="512,270 722,390 722,634 512,754 302,634 302,390" fill="#FF7A3D" stroke="#FFC84A" stroke-width="20"/><circle cx="512" cy="512" r="120" fill="#FFC84A"/><circle cx="512" cy="512" r="64" fill="#FFF9E0"/><path d="M480 250h64v440h-64zM280 300h464l-115 90H395z" fill="#07111F"/><circle cx="786" cy="430" r="28" fill="#FFC84A" stroke="#fff" stroke-width="8"/><circle cx="270" cy="590" r="28" fill="#27D5C4" stroke="#fff" stroke-width="8"/></svg>'''
    write_text(BASE/'05_BRAND/source/app_icon.svg',logo_svg)

    # Splash
    splash=vertical_gradient((1080,2400),COLORS['space_950'],COLORS['space_700']).convert('RGBA')
    starfield(splash,2202,230,0.85)
    d=ImageDraw.Draw(splash,'RGBA')
    d.ellipse((120,470,960,1310), fill=(40,140,190,25), outline=(39,213,196,40), width=9)
    icon=logo.resize((430,430),Image.Resampling.LANCZOS)
    splash.alpha_composite(icon,(325,620))
    title='星矿纪元'; subtitle='合成矿机 · 探索星域 · 构建你的采矿帝国'
    f1=font(112,True); f2=font(38,False)
    box=d.textbbox((0,0),title,font=f1); d.text(((1080-(box[2]-box[0]))/2,1130),title,font=f1,fill=(255,255,255,255))
    box=d.textbbox((0,0),subtitle,font=f2); d.text(((1080-(box[2]-box[0]))/2,1280),subtitle,font=f2,fill=(185,226,235,230))
    d.rounded_rectangle((305,1510,775,1600),radius=45,fill=hex_to_rgb(COLORS['primary_500'])+(245,))
    label='正在启动星际矿场'; f3=font(34,True); box=d.textbbox((0,0),label,font=f3); d.text(((1080-(box[2]-box[0]))/2,1532),label,font=f3,fill=(255,255,255,255))
    d.text((0,2260),'',font=f2)
    splash.convert('RGB').save(BASE/'05_BRAND/android_splash_1080x2400.png',quality=95)

    # Brand banner
    banner=vertical_gradient((1600,900),COLORS['space_950'],COLORS['space_700']).convert('RGBA')
    starfield(banner,20268,180,1)
    db=ImageDraw.Draw(banner,'RGBA')
    db.ellipse((920,-120,1700,660),fill=(58,140,255,45),outline=(39,213,196,80),width=10)
    banner.alpha_composite(logo.resize((420,420),Image.Resampling.LANCZOS),(990,220))
    db.text((120,210),'星矿纪元',font=font(108,True),fill=(255,255,255,255))
    db.text((125,360),'MINING · MERGE · EXPLORE',font=font(38,True),fill=hex_to_rgb(COLORS['energy_300'])+(255,))
    db.text((125,450),'用矿机合成驱动成长，用项目推广连接平台价值',font=font(34),fill=(205,224,235,235))
    db.rounded_rectangle((125,565,455,655),radius=45,fill=hex_to_rgb(COLORS['primary_500'])+(255,))
    db.text((190,588),'开启矿场',font=font(34,True),fill='white')
    banner.convert('RGB').save(BASE/'05_BRAND/brand_banner_1600x900.png',quality=95)

    # Invitation poster with QR sample
    import qrcode
    poster=vertical_gradient((1080,1920),COLORS['space_900'],COLORS['space_700']).convert('RGBA')
    starfield(poster,202612,140,1)
    dp=ImageDraw.Draw(poster,'RGBA')
    dp.text((90,105),'一起进入星矿纪元',font=font(66,True),fill='white')
    dp.text((90,205),'合成矿机，解锁36级星际科技',font=font(34),fill=(188,228,235,255))
    poster.alpha_composite(logo.resize((330,330),Image.Resampling.LANCZOS),(375,300))
    dp.rounded_rectangle((80,690,1000,1660),radius=54,fill=(255,249,241,248),outline=(255,200,74,180),width=6)
    dp.text((150,780),'我的邀请码',font=font(34,True),fill=COLORS['text_secondary'])
    dp.text((150,840),'2026',font=font(98,True),fill=COLORS['primary_600'])
    qr=qrcode.make('https://xkjy-yq.orbexa.cc/i/2026').convert('RGB').resize((430,430),Image.Resampling.NEAREST)
    poster.alpha_composite(qr.convert('RGBA'),(325,990))
    dp.text((288,1460),'扫码注册并绑定邀请关系',font=font(30,True),fill=COLORS['text_primary'])
    dp.text((145,1745),'星矿纪元 · 示例邀请海报',font=font(28),fill=(190,220,230,230))
    poster.convert('RGB').save(BASE/'05_BRAND/invite_poster_1080x1920.png',quality=95)

    make_background('bg_mine_home',COLORS['space_950'],COLORS['space_700'],2026,mine=True)
    make_background('bg_deep_space',COLORS['space_950'],'#1D2652',2036,mine=False)
    make_background('bg_project',COLORS['space_900'],'#205C75',2027,project=True)
    make_background('bg_mall',COLORS['space_900'],'#73442A',2028,mall=True)

    # Token icons and service cards
    for code,label,c1,c2,sym in [
        ('star_point','星矿值',COLORS['gold_500'],COLORS['primary_500'],'star'),
        ('energy_chip','能源芯片',COLORS['energy_500'],COLORS['blue_500'],'bolt'),
        ('cash_balance','账户余额','#55C884','#178B62','cash'),
    ]:
        im=Image.new('RGBA',(512,512),(0,0,0,0)); d=ImageDraw.Draw(im,'RGBA')
        d.ellipse((58,58,454,454),fill=hex_to_rgb(c1)+(255,),outline=(255,255,255,230),width=14)
        d.ellipse((102,102,410,410),fill=hex_to_rgb(c2)+(255,),outline=(255,255,255,90),width=8)
        if sym=='star':
            pts=[]
            for i in range(10):
                a=math.radians(-90+i*36); r=112 if i%2==0 else 46
                pts.append((256+r*math.cos(a),256+r*math.sin(a)))
            d.polygon(pts,fill=(255,249,220,255))
        elif sym=='bolt': d.polygon([(285,120),(165,290),(250,290),(220,405),(355,225),(270,225)],fill=(255,255,255,245))
        else:
            d.rounded_rectangle((150,170,362,342),radius=24,outline=(255,255,255,245),width=18)
            d.ellipse((218,205,294,281),outline=(255,255,255,245),width=14)
            d.line((165,310,347,310),fill=(255,255,255,245),width=14)
        im.save(BASE/f'07_GAME_ASSETS/tokens/{code}.png')

    cards=[('headline_card','头条卡',COLORS['primary_500'],COLORS['gold_500'],'ICON-HEADLINE'),('pin_card','置顶卡',COLORS['violet_500'],COLORS['magenta_500'],'ICON-PIN'),('refresh_card','刷新卡',COLORS['energy_500'],COLORS['blue_500'],'ICON-REFRESH'),('red_packet_card','红包卡','#ED5C6D',COLORS['gold_500'],'ICON-CASH'),('member_card','星耀会员',COLORS['violet_500'],COLORS['magenta_500'],'ICON-MEMBER')]
    for code,label,c1,c2,icon in cards:
        im=vertical_gradient((720,420),c1,c2).convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
        d.rounded_rectangle((18,18,702,402),radius=54,outline=(255,255,255,90),width=4)
        d.ellipse((470,-20,760,270),fill=(255,255,255,25))
        d.text((60,70),label,font=font(62,True),fill='white')
        d.text((64,160),'星矿纪元虚拟权益',font=font(28),fill=(255,255,255,220))
        d.rounded_rectangle((60,270,330,340),radius=35,fill=(7,17,31,90))
        d.text((98,286),'立即查看',font=font(28,True),fill='white')
        im.convert('RGB').save(BASE/f'07_GAME_ASSETS/cards/{code}.png',quality=95)

    write_yaml(BASE/'05_BRAND/BRAND_ASSET_MANIFEST.yaml', {
        'project':'星矿纪元','assets':[
            {'id':'BRAND-ICON','file':'05_BRAND/app_icon/app_icon_1024.png','usage':'Android App图标','transparent':False},
            {'id':'BRAND-SPLASH','file':'05_BRAND/android_splash_1080x2400.png','usage':'Android启动图','transparent':False},
            {'id':'BRAND-BANNER','file':'05_BRAND/brand_banner_1600x900.png','usage':'品牌图','transparent':False},
            {'id':'BRAND-INVITE','file':'05_BRAND/invite_poster_1080x1920.png','usage':'邀请海报效果图','transparent':False},
        ]
    })


# ---------------------------------------------------------------------------
# Page specs and navigation contracts
# ---------------------------------------------------------------------------
RELEASE_BY_MODULE={
    'system':'P11','account':'P01','security':'P01','game':'P02','project':'P04','mall':'P06','payment':'P07','order':'P06','membership':'P06',
    'discover':'P08','market':'P08','wallet':'P08','referral':'P09','commission':'P09','identity':'P10','withdrawal':'P10','me':'P11','message':'P11','settings':'P11','support':'P11',
    'dashboard':'P00','user':'P01','asset':'P08','storage':'P00','email':'P01','captcha':'P01','content':'P11','app_release':'P11','rbac':'P00','admin_auth':'P00','h5':'P11',
}

MODULE_APIS={
'account':['POST /api/v1/auth/register','POST /api/v1/auth/login/password','POST /api/v1/auth/login/code','POST /api/v1/auth/verification-codes'],
'security':['POST /api/v1/security/captcha/challenges','POST /api/v1/security/captcha/verify'],
'game':['GET /api/v1/game/bootstrap','GET /api/v1/game/board','POST /api/v1/game/board/move','POST /api/v1/game/board/merge','POST /api/v1/game/production/claim'],
'project':['GET /api/v1/projects','POST /api/v1/projects','GET /api/v1/projects/{projectId}','POST /api/v1/projects/{projectId}/reports'],
'mall':['GET /api/v1/mall/products','POST /api/v1/orders/prepare','GET /api/v1/entitlements'],
'payment':['POST /api/v1/payments/prepare','POST /api/v1/payments/orders/{outTradeNo}/pay','POST /api/v1/payments/orders/{outTradeNo}/query'],
'order':['GET /api/v1/orders','GET /api/v1/orders/{outTradeNo}'],
'membership':['GET /api/v1/membership','GET /api/v1/membership/plans'],
'discover':['GET /api/v1/point-price/current','GET /api/v1/point-price/history'],
'market':['GET /api/v1/market/buy-orders','POST /api/v1/market/buy-orders'],
'wallet':['GET /api/v1/wallets','POST /api/v1/point-transfers','POST /api/v1/point-exchanges'],
'referral':['GET /api/v1/referrals/overview','GET /api/v1/referrals/direct','GET /api/v1/referrals/indirect'],
'commission':['GET /api/v1/commissions/points','GET /api/v1/commissions/cash'],
'identity':['GET /api/v1/identity/status','POST /api/v1/identity/sessions','POST /api/v1/identity/sessions/{sessionId}/verify'],
'withdrawal':['GET /api/v1/withdrawals/tiers','POST /api/v1/withdrawals','GET /api/v1/withdrawals/{withdrawalNo}'],
'me':['GET /api/v1/me','PATCH /api/v1/me/profile'],
'message':['GET /api/v1/messages','POST /api/v1/messages/read-all'],
'settings':['GET /api/v1/me/sessions','DELETE /api/v1/me/sessions/{sessionId}'],
'support':['POST /api/v1/feedback'],
}

MODULE_TABLES={
'account':['users','user_profiles','user_identifiers','password_credentials','user_sessions','email_verification_codes'],
'security':['captcha_challenges','captcha_tickets','login_attempts'],
'game':['user_game_profiles','miner_level_configs','user_miners','user_board_slots','production_settlements','production_claims'],
'project':['projects','project_images','project_contacts','project_review_records','project_favorites','project_reports'],
'mall':['mall_products','orders','order_items','user_entitlements','promotion_card_inventory'],
'payment':['payment_orders','payment_attempts','payment_events','manual_payment_submissions','manual_payment_reviews'],
'order':['orders','order_items','order_price_snapshots'],
'membership':['membership_plans','user_memberships'],
'discover':['point_price_rules','point_price_history'],
'market':['market_buy_orders','market_order_contacts','market_order_reports'],
'wallet':['wallet_accounts','wallet_transactions','wallet_entries','point_exchange_orders','point_transfer_orders'],
'referral':['referral_relations','referral_closure'],
'commission':['commission_records','commission_reversals'],
'identity':['identity_sessions','identity_captures','identity_provider_requests','identity_results'],
'withdrawal':['withdrawal_tiers','user_payment_accounts','withdrawal_orders','withdrawal_payout_attempts'],
'me':['users','user_profiles'],
'message':['notifications','notification_reads'],
'settings':['user_sessions','runtime_configs'],
'support':['feedback_tickets'],
}


def page_business_rules(page):
    m=page['module']; t=page['template']
    rules=[f'页面只实现“{page["name_cn"]}”对应职责，不混入未触发模块。','返回来源页面时必须恢复页面上下文，不无条件刷新。','所有图标必须从ICON_REGISTRY引用SVG。']
    if m=='game': rules += ['矿机和资产状态以后端为最终事实源。','合成、购买、领取、回收必须携带幂等键。']
    if m=='project': rules += ['项目图片最多8张。','项目详情中的任务进度不得遮挡主体内容。']
    if m=='payment': rules += ['订单金额由后端计算。','return_url不得作为发货依据。','支付结果必须通过统一查单确认。']
    if m=='identity': rules += ['CameraX只在采集页启用。','实名媒体本地零留存。','服务商异常不得映射为成功。']
    if m=='withdrawal': rules += ['提现前必须实名并绑定支付宝。','未知出款状态不得释放冻结余额。']
    if m=='wallet': rules += ['星矿值、能源芯片、账户余额独立记账。','禁止直接修改余额字段。']
    if t=='game_home': rules += ['首页必须以2D矿区为视觉主体，普通App卡片仅作HUD辅助。','4×4棋盘初始开放12格。']
    return rules


def state_description(state):
    mp={'DEFAULT':'默认业务状态','ERROR':'业务失败或校验错误','SUBMITTING':'提交中且禁止重复操作','NEW_USER':'首次进入的新手引导状态','CLAIMABLE':'存在可领取产出','BOARD_FULL':'棋盘无空位','OFFLINE':'网络不可用但保留现有内容','LOADING':'首次加载骨架','EMPTY':'空数据','TASK_RUNNING':'浏览任务倒计时进行中','TASK_SUCCESS':'浏览任务达标并自动发放','OFFLINE_BY_ADMIN':'项目被管理员下架','PROCESSING':'通道处理中','SUCCESS':'业务成功','FAILURE':'终态失败','EXPIRED':'订单过期','UPLOADING':'付款截图上传中','REVIEW_PENDING':'人工扫码待审核','REJECTED':'人工审核拒绝可重提','PERMISSION_DENIED':'摄像头权限拒绝','VERIFYING':'第三方身份核验中','RECAPTURE':'结果1002需重新采集','DISABLED':'前置条件未满足'}
    return mp.get(state,state)


def generate_page_specs():
    app,h5,admin=flatten(); all_pages=app+h5+admin
    index={'project':'星矿纪元','version':'1.1.0','effect_render_count':len(all_pages)+sum(len(v) for v in EXTRA_STATES.values()),'pages':[]}
    state_matrix={'project':'星矿纪元','version':'1.1.0','pages':[]}
    for page in all_pages:
        pid=page['page_id']; states=['DEFAULT']+EXTRA_STATES.get(pid,[])
        platform=page['platform']; rel=RELEASE_BY_MODULE.get(page['module'],'P11')
        route='/' + pid.lower().replace('-','/')
        spec={
            'page': {'id':pid,'name_cn':page['name_cn'],'platform':platform,'source_scope':'project_specific','feature_id':f'F-{page["module"].upper()}','module_id':page['module'],'applicable_rule_ids':['G-001~G-047','LB-PAGE-STATE','LB-ICON'],'route':route,'release':rel,'default_state_id':'DEFAULT','state_ids':states,'shared_components':[],'security':{'captcha_gate':pid in ['APP-AUTH-001','APP-AUTH-002','ADMIN-AUTH-001'],'captcha_purpose':'LOGIN' if 'AUTH-001' in pid else None}},
            'access': {'roles':['authenticated_user'] if platform=='android' and 'AUTH' not in pid and 'SYS' not in pid else (['admin'] if platform=='admin' else ['guest_or_user']),'permissions':[],'prerequisites':[],'entry_points':[],'exit_points':[],'back_behavior':'返回已有来源页面实例，不新建同路由'},
            'navigation_state': {'policy_id':'LB-PAGE-STATE','preserve_on_return':not any(x in pid for x in ['ID-004','SEC-001']),'state_owner':'destination_view_model','preserve_fields':['scroll_anchor_item_id','scroll_offset','selected_tab','search_query','filters','sort','pagination_or_cursor','expanded_items','selected_items','form_draft','loaded_content'],'refresh_on_back':False,'refresh_on_resume':False,'refresh_policy':'stale_while_revalidate_keep_content','scroll_restore_key':'stable_item_id_and_offset','mutation_merge_strategy':'local_patch','process_recreation_restore_safe_state':True,'allowed_reset_exceptions':['实名采集媒体和密码类敏感输入不恢复'] if any(x in pid for x in ['ID-004','SEC-003','AUTH-004']) else []},
            'business': {'objective':f'完成{page["name_cn"]}的可操作业务闭环。','rules':page_business_rules(page),'visible_copy':[page['name_cn']],'forbidden_copy':['稳赚','保底现金收益','未经确认的成功状态']},
            'layout': {'baseline_viewport_px':'780x1688' if platform in ('android','h5') else '1440x900','baseline_dp':'390x844' if platform in ('android','h5') else None,'effect_scale':2 if platform in ('android','h5') else 1,'system_bar_mode':'dark_game' if page['module']=='game' else 'light_or_brand','component_tree':['status_or_admin_bar','top_navigation','primary_content','context_actions','bottom_navigation_or_footer']},
            'resolved_ui_values': {'page_background':COLORS['surface'],'content_padding_horizontal_dp':16,'content_padding_vertical_dp':16,'top_bar_height_dp':56,'title_font_sp':20,'title_weight':700,'title_line_height_sp':28,'body_font_sp':14,'body_line_height_sp':22,'card_radius_dp':18,'card_padding_dp':16,'item_gap_dp':12,'input_height_dp':52,'button_height_dp':50,'button_radius_dp':16,'icon_size_dp':24,'icon_touch_target_dp':48,'border_width_dp':1,'elevation_dp':0},
            'used_design_tokens':['colors.space_900','colors.primary_500','colors.gold_500','colors.energy_500','radius.lg','spacing.lg','motion.standard_ms'],
            'icon_usage': {'policy_id':'LB-ICON','default_functional_library':'project_custom_svg','text_as_icon_forbidden':True,'icon_font_forbidden':True,'icon_ids':['ICON-ACTION-BACK'] if not pid.endswith('001') else [],'brand_assets':[]},
            'components':[{'component_id':'TOP-BAR','type':'top_bar','text':page['name_cn'],'icon_id':'ICON-ACTION-BACK','icon_role':'functional','accessibility_label':'返回','values':{},'interactions':['返回'],'validation':[]}],
            'states':[{'state_id':s,'required':True,'description':state_description(s),'artifact_suffix':s} for s in states],
            'bindings': {'apis':MODULE_APIS.get(page['module'],[]),'database_tables':MODULE_TABLES.get(page['module'],[]),'admin_configs':[f'{page["module"]}.*'],'audit_logs':[f'{page["module"]}.operation'],'analytics_events':[f'{pid.lower()}.view']},
            'artifacts': {'png_pattern':f'04_UI/{"APP" if platform=="android" else "ADMIN" if platform=="admin" else "H5"}/{pid}__<StateID>.png','html_pattern':f'10_HTML/{"APP" if platform=="android" else "ADMIN" if platform=="admin" else "H5"}/{pid}__<StateID>.html','svg':[],'icon_registry_file':'03_SPECS/ICON_REGISTRY.yaml','index_entry':True},
            'testing': {'functional_steps':['进入页面','完成主操作','验证服务端结果','返回来源页并验证状态保持'],'state_restore_steps':['深度滚动或填写草稿','进入子页面','返回并检查位置、筛选、草稿和已加载内容'],'visual_points':['结构、字号、间距、圆角、色值、图标与效果图一致'],'icon_points':['无文字或Emoji代图标'],'accessibility_points':['触控区域不小于48dp','关键图标具备语义标签']},
        }
        write_yaml(BASE/f'03_SPECS/pages/{pid}.yaml',spec)
        nav={'page_id':pid,'policy_id':'LB-PAGE-STATE','preserve_on_return':spec['navigation_state']['preserve_on_return'],'state_owner':'destination_view_model','preserve_fields':spec['navigation_state']['preserve_fields'],'scroll_restoration':{'container':'lazy_grid' if page['template'] in ('game_home','atlas','miner_store','inventory') else 'lazy_list','stable_item_key':'business_id','anchor_and_offset_required':True},'refresh_policy':{'on_first_entry_without_cache':True,'on_back':False,'on_resume':False,'user_initiated':True,'stale_while_revalidate':True,'keep_existing_content':True},'mutation_merge':{'strategy':'local_patch','deleted_item_fallback':'keep_nearest_visible_position'},'process_recreation':{'restore_safe_state':True,'sensitive_fields_excluded':['password','verification_code','identity_media']},'allowed_reset_exceptions':spec['navigation_state']['allowed_reset_exceptions'],'test_cases':['deep_scroll_open_child_and_back','filters_tabs_pagination_preserved','background_foreground_preserved','external_activity_return_preserved','no_blank_or_duplicate_reload']}
        write_yaml(BASE/f'03_SPECS/navigation/{pid}.yaml',nav)
        state_artifacts=[]
        for s in states:
            folder='APP' if platform=='android' else 'ADMIN' if platform=='admin' else 'H5'
            state_artifacts.append({'state_id':s,'image_file':f'04_UI/{folder}/{pid}__{s}.png','source_file':f'10_HTML/{folder}/{pid}__{s}.html','visual_verified':True})
        index['pages'].append({'page_id':pid,'name_cn':page['name_cn'],'platform':platform,'module':page['module'],'release':rel,'spec_file':f'03_SPECS/pages/{pid}.yaml','navigation_state_contract':f'03_SPECS/navigation/{pid}.yaml','preserve_on_return':spec['navigation_state']['preserve_on_return'],'required_states':state_artifacts,'implemented':False})
        state_matrix['pages'].append({'page_id':pid,'page_name':page['name_cn'],'platform':platform,'states':[{'state_id':s,'required':True} for s in states]})
    write_yaml(BASE/'03_SPECS/PAGE_INDEX.yaml',index)
    write_yaml(BASE/'03_SPECS/PAGE_STATE_MATRIX.yaml',state_matrix)


# ---------------------------------------------------------------------------
# API contracts and database schema
# ---------------------------------------------------------------------------
API_GROUPS = {
'账号与安全':[
('POST','/api/v1/security/captcha/challenges','创建图形验证码挑战','guest',False),('POST','/api/v1/security/captcha/verify','验证图形验证码并签发一次性票据','guest',False),
('POST','/api/v1/auth/verification-codes','发送用途限定邮箱验证码','guest',True),('POST','/api/v1/auth/register','邮箱注册并初始化用户、钱包和游戏账户','guest',True),
('POST','/api/v1/auth/login/password','邮箱密码登录','guest',True),('POST','/api/v1/auth/login/code','邮箱验证码登录','guest',True),('POST','/api/v1/auth/password-recovery','申请找回密码','guest',True),
('POST','/api/v1/auth/password-reset','重置密码','guest',True),('POST','/api/v1/auth/refresh','旋转Refresh Token','refresh_token',True),('POST','/api/v1/auth/logout','退出当前会话','user',True),
('GET','/api/v1/me','读取当前用户','user',False),('PATCH','/api/v1/me/profile','更新资料','user',True),('PUT','/api/v1/me/password','修改登录密码','user',True),('GET','/api/v1/me/sessions','登录设备列表','user',False),('DELETE','/api/v1/me/sessions/{sessionId}','退出指定设备','user',True)],
'游戏':[
('GET','/api/v1/game/bootstrap','返回棋盘、钱包、产出、任务和资源版本快照','user',False),('GET','/api/v1/game/board','获取棋盘与版本','user',False),('GET','/api/v1/game/miner-store','可购买等级与下一台价格','user',False),
('POST','/api/v1/game/miners/quote','矿机购买报价','user',True),('POST','/api/v1/game/miners/purchase','扣星矿值并创建矿机实例','user',True),('POST','/api/v1/game/board/move','移动或交换矿机','user',True),('POST','/api/v1/game/board/merge','合成同等级矿机','user',True),
('POST','/api/v1/game/board/organize','自动整理但不自动合成','user',True),('POST','/api/v1/game/miners/{minerId}/lock','锁定矿机','user',True),('POST','/api/v1/game/miners/{minerId}/recycle','回收矿机','user',True),('GET','/api/v1/game/production','获取当前产出快照','user',False),('POST','/api/v1/game/production/claim','结算并领取全部待领取星矿值','user',True),
('GET','/api/v1/game/warehouse','仓库列表','user',False),('POST','/api/v1/game/warehouse/expand','主副积分扩容','user',True),('GET','/api/v1/game/atlas','矿机图鉴','user',False),('GET','/api/v1/game/tasks','每日任务','user',False),('POST','/api/v1/game/tasks/{taskId}/claim','领取任务奖励','user',True),('POST','/api/v1/game/sign-in/claim','每日签到','user',True),('POST','/api/v1/game/supply-boxes/{boxId}/open','服务端确定掉落后开箱','user',True),('GET','/api/v1/game/rankings','榜单快照','user',False)],
'项目与任务':[
('GET','/api/v1/project-categories','项目分类','user',False),('GET','/api/v1/projects','按权重分页查询项目','user',False),('POST','/api/v1/projects','创建项目草稿','user',True),('GET','/api/v1/projects/{projectId}','统一项目详情','user',False),('PATCH','/api/v1/projects/{projectId}','编辑本人项目','user',True),('POST','/api/v1/projects/{projectId}/submit','提交审核','user',True),('POST','/api/v1/projects/{projectId}/favorites','收藏','user',True),('POST','/api/v1/projects/{projectId}/reports','举报','user',True),('POST','/api/v1/projects/{projectId}/contact-reveal','受控展示联系方式','user',True),
('POST','/api/v1/projects/{projectId}/promotion-cards/apply','使用头条/置顶/刷新卡','user',True),('POST','/api/v1/projects/{projectId}/task-campaigns/quote','浏览任务预算报价','user',True),('POST','/api/v1/projects/{projectId}/task-campaigns','创建任务活动订单','user',True),('POST','/api/v1/project-task-sessions/start','进入详情自动创建任务会话','user',True),('POST','/api/v1/project-task-sessions/{sessionId}/heartbeat','前台可见心跳','user',True),('POST','/api/v1/project-task-sessions/{sessionId}/pause','离开页面暂停','user',True)],
'商城订单支付':[
('GET','/api/v1/mall/products','虚拟商品列表','user',False),('GET','/api/v1/mall/products/{productId}','商品详情','user',False),('POST','/api/v1/orders/prepare','服务端定价并创建订单','user',True),('GET','/api/v1/orders','订单列表','user',False),('GET','/api/v1/orders/{outTradeNo}','订单详情','user',False),
('POST','/api/v1/payments/prepare','按订单类型返回可用方式','user',True),('POST','/api/v1/payments/orders/{outTradeNo}/pay','发起XApay或余额/积分支付','user',True),('POST','/api/v1/payments/orders/{outTradeNo}/query','统一查单','user',True),('POST','/api/v1/payments/manual/{outTradeNo}/screenshot-ticket','付款截图上传票据','user',True),('POST','/api/v1/payments/manual/{outTradeNo}/submissions','提交人工扫码审核','user',True),('POST','/api/v1/payments/callback/xapay','XApay异步通知','provider',True)],
'钱包集市邀请':[
('GET','/api/v1/wallets','三资产账户','user',False),('GET','/api/v1/wallets/{asset}/transactions','资产流水','user',False),('POST','/api/v1/point-exchanges/quote','星矿值换能源芯片报价','user',True),('POST','/api/v1/point-exchanges','2:1单向兑换','user',True),('GET','/api/v1/point-transfers/recipient/{uid}','UID收款人确认','user',False),('POST','/api/v1/point-transfers/quote','赠送主副积分报价','user',True),('POST','/api/v1/point-transfers','执行赠送','user',True),
('GET','/api/v1/point-price/current','当日参考价格','user',False),('GET','/api/v1/point-price/history','历史价格曲线','user',False),('GET','/api/v1/market/buy-orders','按单价降序查询求购单','user',False),('POST','/api/v1/market/buy-orders','发布求购单','user',True),('POST','/api/v1/market/buy-orders/{orderId}/close','关闭求购单','user',True),('GET','/api/v1/referrals/overview','邀请总览','user',False),('GET','/api/v1/referrals/direct','一级好友','user',False),('GET','/api/v1/referrals/indirect','二级好友','user',False),('GET','/api/v1/commissions/points','积分提成','user',False),('GET','/api/v1/commissions/cash','消费佣金','user',False)],
'实名与提现':[
('GET','/api/v1/identity/status','实名状态','user',False),('POST','/api/v1/identity/sessions','创建实名会话和随机动作','user',True),('POST','/api/v1/identity/sessions/{sessionId}/capture-ticket','私有媒体上传票据','user',True),('POST','/api/v1/identity/sessions/{sessionId}/captures','绑定采集媒体','user',True),('POST','/api/v1/identity/sessions/{sessionId}/verify','调用母版人证比对','user',True),
('GET','/api/v1/withdrawals/tiers','固定提现档位','user',False),('POST','/api/v1/withdrawals/payment-account','绑定支付宝账号','user',True),('POST','/api/v1/withdrawals/quote','提现报价和限制校验','user',True),('POST','/api/v1/withdrawals','冻结余额并创建提现单','user',True),('GET','/api/v1/withdrawals/{withdrawalNo}','提现详情','user',False),('POST','/api/v1/withdrawals/{withdrawalNo}/query','主动查单','user',True)],
}


def generate_contracts_and_schema():
    endpoints=[]
    for group,items in API_GROUPS.items():
        for method,path,summary,auth,idem in items:
            endpoints.append({'group':group,'method':method,'path':path,'summary':summary,'auth':auth,'captcha_ticket_required':path in ['/api/v1/auth/register','/api/v1/auth/login/password','/api/v1/auth/login/code'],'idempotency_key_required':idem,'response_envelope':'standard_v1','audit':idem})
    write_yaml(BASE/'03_SPECS/contracts/API_CONTRACTS.yaml', {'project':'星矿纪元','version':'1.1.0','base_path':'/api/v1','standard_response':{'code':'SUCCESS','message':'操作成功','data':{},'request_id':'req_xxx','server_time':'ISO-8601'} ,'endpoints':endpoints})

    error_codes=[
        ('SUCCESS','成功',200),('VALIDATION_ERROR','字段校验失败',400),('UNAUTHORIZED','未登录或会话失效',401),('FORBIDDEN','无权限',403),('NOT_FOUND','资源不存在',404),('CONFLICT','状态或版本冲突',409),('RATE_LIMITED','请求过于频繁',429),
        ('CAPTCHA_REQUIRED','需要图形验证码',400),('CAPTCHA_INVALID','图形验证码错误或过期',400),('EMAIL_CODE_INVALID','邮箱验证码错误或过期',400),('BOARD_VERSION_CONFLICT','棋盘版本冲突',409),('BOARD_FULL','棋盘无空位',409),('MINER_LEVEL_MISMATCH','矿机等级不同',409),('INSUFFICIENT_STAR_POINT','星矿值不足',409),('INSUFFICIENT_ENERGY_CHIP','能源芯片不足',409),('ORDER_EXPIRED','订单已过期',409),('PAYMENT_PENDING','支付结果确认中',202),('PAYMENT_SIGNATURE_INVALID','支付签名错误',400),('IDENTITY_RECAPTURE_REQUIRED','需要重新采集',409),('WITHDRAWAL_PAYOUT_UNKNOWN','出款状态未知等待查单',202),('RISK_RESTRICTED','业务被风控限制',403),('INTERNAL_ERROR','系统内部错误',500),
    ]
    write_yaml(BASE/'03_SPECS/contracts/API_ERROR_CATALOG.yaml', {'errors':[{'code':c,'message_cn':m,'http_status':s} for c,m,s in error_codes]})

    # Full table catalog and practical core SQL. The schema is intentionally explicit enough for Codex to create migrations.
    tables = {
        '账号与用户':['users','user_profiles','user_identifiers','password_credentials','user_sessions','email_verification_codes','login_attempts','user_restrictions','account_deletion_requests'],
        '邀请会员':['referral_relations','referral_closure','membership_plans','user_memberships'],
        '游戏':['miner_level_configs','user_game_profiles','user_miners','user_board_slots','user_warehouse_slots','miner_purchase_daily_counters','miner_events','production_settlements','production_claims','user_atlas_entries','task_templates','user_task_progress','sign_in_configs','user_sign_in_records','supply_box_configs','supply_box_drop_items','user_supply_boxes','supply_box_openings','ranking_snapshots','game_resource_versions'],
        '资产':['wallet_accounts','wallet_transactions','wallet_entries','point_exchange_orders','point_transfer_orders','transfer_password_credentials','asset_adjustment_orders'],
        '价格市场':['point_price_rules','point_price_history','market_buy_orders','market_order_contacts','market_order_reports','market_order_audits'],
        '项目':['project_categories','projects','project_images','project_contacts','project_review_records','project_favorites','project_reports','promotion_service_configs','project_promotion_usages','project_task_campaigns','project_task_sessions','project_task_heartbeats','project_task_rewards'],
        '商城订单':['mall_categories','mall_products','mall_product_payment_methods','orders','order_items','order_price_snapshots','user_entitlements','promotion_card_inventory','promotion_card_ledger','red_packet_card_records'],
        '支付':['payment_method_configs','payment_orders','payment_attempts','payment_events','xapay_requests','xapay_callbacks','manual_qr_codes','manual_qr_sessions','manual_payment_submissions','manual_payment_reviews','payment_reconciliation_records','payment_settlement_records'],
        '佣金':['point_commission_rules','cash_commission_rules','commission_records','commission_reversals','commission_risk_holds'],
        '实名':['identity_configs','identity_sessions','identity_captures','identity_provider_requests','identity_results','identity_manual_actions','identity_bindings'],
        '提现':['withdrawal_configs','withdrawal_tiers','user_payment_accounts','withdrawal_orders','withdrawal_state_histories','withdrawal_review_records','withdrawal_payout_attempts','withdrawal_provider_queries','withdrawal_reconciliation_records'],
        '平台':['file_objects','file_bindings','file_operation_logs','email_templates','email_send_jobs','email_send_logs','captcha_challenges','captcha_tickets','notifications','notification_reads','announcements','feedback_tickets','admin_users','admin_roles','admin_permissions','admin_role_permissions','admin_operation_audits','runtime_configs','app_releases','scheduled_job_runs','outbox_events','service_health_records'],
    }
    write_yaml(BASE/'03_SPECS/database/SCHEMA_CATALOG.yaml', {'project':'星矿纪元','groups':[{'name':g,'tables':ts} for g,ts in tables.items()]})

    sql='''-- 星矿纪元 V1.1.0 核心数据库结构\n-- PostgreSQL 16+；所有金额和积分使用NUMERIC，禁止浮点。\nCREATE EXTENSION IF NOT EXISTS pgcrypto;\n\n'''
    sql += '''CREATE TABLE users (\n  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), uid bigint NOT NULL UNIQUE CHECK(uid>=2026),\n  status varchar(32) NOT NULL DEFAULT 'ACTIVE', created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()\n);\nCREATE SEQUENCE IF NOT EXISTS user_uid_seq START 2026;\nCREATE TABLE user_profiles (user_id uuid PRIMARY KEY REFERENCES users(id), nickname varchar(40) NOT NULL, avatar_file_id uuid, identity_status varchar(32) NOT NULL DEFAULT 'UNVERIFIED', membership_expires_at timestamptz, updated_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE user_identifiers (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), type varchar(20) NOT NULL, normalized_value varchar(255) NOT NULL, verified_at timestamptz, UNIQUE(type,normalized_value));\nCREATE TABLE password_credentials (user_id uuid PRIMARY KEY REFERENCES users(id), password_hash text NOT NULL, algorithm varchar(20) NOT NULL DEFAULT 'argon2id', updated_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE user_sessions (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), refresh_token_hash text NOT NULL UNIQUE, device_id varchar(128), expires_at timestamptz NOT NULL, revoked_at timestamptz, created_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE email_verification_codes (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), normalized_email varchar(255) NOT NULL, purpose varchar(32) NOT NULL, code_hash text NOT NULL, expires_at timestamptz NOT NULL, attempts int NOT NULL DEFAULT 0, consumed_at timestamptz, created_at timestamptz NOT NULL DEFAULT now());\n\n'''
    sql += '''CREATE TABLE referral_relations (user_id uuid PRIMARY KEY REFERENCES users(id), parent_user_id uuid REFERENCES users(id), bound_at timestamptz NOT NULL DEFAULT now(), CHECK(user_id IS DISTINCT FROM parent_user_id));\nCREATE TABLE referral_closure (ancestor_user_id uuid NOT NULL REFERENCES users(id), descendant_user_id uuid NOT NULL REFERENCES users(id), depth smallint NOT NULL CHECK(depth IN (1,2)), PRIMARY KEY(ancestor_user_id,descendant_user_id,depth));\nCREATE TABLE membership_plans (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code varchar(40) UNIQUE NOT NULL, name varchar(80) NOT NULL, duration_days int NOT NULL, cash_price numeric(18,2) NOT NULL, promotion_discount numeric(8,6) NOT NULL DEFAULT .5, enabled boolean NOT NULL DEFAULT true);\nCREATE TABLE user_memberships (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), plan_id uuid NOT NULL REFERENCES membership_plans(id), starts_at timestamptz NOT NULL, expires_at timestamptz NOT NULL, source_order_id uuid, created_at timestamptz NOT NULL DEFAULT now());\n\n'''
    sql += '''CREATE TABLE miner_level_configs (level smallint PRIMARY KEY CHECK(level BETWEEN 1 AND 36), miner_id varchar(20) UNIQUE NOT NULL, name varchar(80) NOT NULL, production_per_hour numeric(38,8) NOT NULL CHECK(production_per_hour>=0), base_price numeric(38,8) NOT NULL CHECK(base_price>=0), direct_purchase_enabled boolean NOT NULL DEFAULT true, asset_version varchar(40) NOT NULL, enabled boolean NOT NULL DEFAULT true);\nCREATE TABLE user_game_profiles (user_id uuid PRIMARY KEY REFERENCES users(id), board_version bigint NOT NULL DEFAULT 1, highest_level smallint NOT NULL DEFAULT 1, warehouse_capacity int NOT NULL DEFAULT 8, unclaimed_amount numeric(38,8) NOT NULL DEFAULT 0, last_settled_at timestamptz NOT NULL DEFAULT now(), total_produced numeric(38,8) NOT NULL DEFAULT 0, total_claimed numeric(38,8) NOT NULL DEFAULT 0);\nCREATE TABLE user_miners (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), level smallint NOT NULL REFERENCES miner_level_configs(level), state varchar(32) NOT NULL, locked boolean NOT NULL DEFAULT false, source_type varchar(32) NOT NULL, source_business_id varchar(80), created_at timestamptz NOT NULL DEFAULT now(), consumed_at timestamptz);\nCREATE TABLE user_board_slots (user_id uuid NOT NULL REFERENCES users(id), slot_no smallint NOT NULL CHECK(slot_no BETWEEN 1 AND 16), unlocked boolean NOT NULL DEFAULT false, miner_id uuid UNIQUE REFERENCES user_miners(id), PRIMARY KEY(user_id,slot_no));\nCREATE TABLE user_warehouse_slots (user_id uuid NOT NULL REFERENCES users(id), slot_no smallint NOT NULL CHECK(slot_no BETWEEN 1 AND 24), miner_id uuid UNIQUE REFERENCES user_miners(id), PRIMARY KEY(user_id,slot_no));\nCREATE TABLE miner_events (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), event_type varchar(32) NOT NULL, source_miner_id uuid, target_miner_id uuid, result_miner_id uuid, board_version_before bigint, board_version_after bigint, idempotency_key uuid NOT NULL UNIQUE, payload jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE production_claims (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), amount numeric(38,8) NOT NULL CHECK(amount>=0), idempotency_key uuid NOT NULL UNIQUE, wallet_transaction_id uuid, created_at timestamptz NOT NULL DEFAULT now());\n\n'''
    sql += '''CREATE TABLE wallet_accounts (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), asset_type varchar(32) NOT NULL, available_balance numeric(38,8) NOT NULL DEFAULT 0 CHECK(available_balance>=0), frozen_balance numeric(38,8) NOT NULL DEFAULT 0 CHECK(frozen_balance>=0), version bigint NOT NULL DEFAULT 1, UNIQUE(user_id,asset_type));\nCREATE TABLE wallet_transactions (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), business_type varchar(40) NOT NULL, business_id varchar(100) NOT NULL, idempotency_key uuid NOT NULL UNIQUE, status varchar(24) NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(business_type,business_id));\nCREATE TABLE wallet_entries (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), transaction_id uuid NOT NULL REFERENCES wallet_transactions(id), account_id uuid NOT NULL REFERENCES wallet_accounts(id), direction varchar(8) NOT NULL CHECK(direction IN ('DEBIT','CREDIT')), amount numeric(38,8) NOT NULL CHECK(amount>0), balance_before numeric(38,8) NOT NULL, balance_after numeric(38,8) NOT NULL, created_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE point_transfer_orders (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), transfer_no varchar(64) UNIQUE NOT NULL, sender_user_id uuid NOT NULL REFERENCES users(id), recipient_user_id uuid NOT NULL REFERENCES users(id), star_amount numeric(38,8) NOT NULL CHECK(star_amount>0), energy_fee numeric(38,8) NOT NULL CHECK(energy_fee>=0), status varchar(24) NOT NULL, idempotency_key uuid NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE point_price_history (price_date date PRIMARY KEY, reference_price numeric(18,8) NOT NULL CHECK(reference_price>0), daily_rate numeric(8,6) NOT NULL DEFAULT .01, source varchar(32) NOT NULL, created_at timestamptz NOT NULL DEFAULT now());\n\n'''
    sql += '''CREATE TABLE project_categories (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), name varchar(40) NOT NULL, sort_order int NOT NULL DEFAULT 0, is_system_default boolean NOT NULL DEFAULT false, enabled boolean NOT NULL DEFAULT true);\nCREATE TABLE projects (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), owner_user_id uuid NOT NULL REFERENCES users(id), category_id uuid REFERENCES project_categories(id), title varchar(80) NOT NULL, summary varchar(240) NOT NULL, content text NOT NULL, link_url text, status varchar(32) NOT NULL, published_at timestamptz, last_refresh_at timestamptz, refresh_priority_until timestamptz, headline_until timestamptz, pin_until timestamptz, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE project_images (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, file_id uuid NOT NULL, sort_order smallint NOT NULL, UNIQUE(project_id,sort_order), CHECK(sort_order BETWEEN 1 AND 8));\nCREATE TABLE project_favorites (user_id uuid NOT NULL REFERENCES users(id), project_id uuid NOT NULL REFERENCES projects(id), created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(user_id,project_id));\nCREATE TABLE project_task_campaigns (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id), owner_user_id uuid NOT NULL REFERENCES users(id), reward_per_user numeric(38,8) NOT NULL CHECK(reward_per_user>0), target_users int NOT NULL CHECK(target_users>0), completed_users int NOT NULL DEFAULT 0, required_seconds int NOT NULL CHECK(required_seconds BETWEEN 5 AND 600), starts_at timestamptz NOT NULL, ends_at timestamptz NOT NULL, status varchar(32) NOT NULL);\nCREATE TABLE project_task_sessions (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES project_task_campaigns(id), user_id uuid NOT NULL REFERENCES users(id), accumulated_seconds int NOT NULL DEFAULT 0, status varchar(24) NOT NULL, last_heartbeat_at timestamptz, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(campaign_id,user_id));\nCREATE TABLE project_task_rewards (campaign_id uuid NOT NULL REFERENCES project_task_campaigns(id), user_id uuid NOT NULL REFERENCES users(id), wallet_transaction_id uuid NOT NULL, amount numeric(38,8) NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(campaign_id,user_id));\n\n'''
    sql += '''CREATE TABLE mall_products (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), product_type varchar(40) NOT NULL, name varchar(100) NOT NULL, cash_price numeric(18,2), star_price numeric(38,8), energy_price numeric(38,8), stock bigint, handler_code varchar(80) NOT NULL, enabled boolean NOT NULL DEFAULT true, config jsonb NOT NULL DEFAULT '{}'::jsonb);\nCREATE TABLE orders (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), out_trade_no varchar(64) UNIQUE NOT NULL, user_id uuid NOT NULL REFERENCES users(id), order_type varchar(40) NOT NULL, status varchar(32) NOT NULL, currency varchar(16) NOT NULL, original_amount numeric(38,8) NOT NULL, discount_amount numeric(38,8) NOT NULL DEFAULT 0, payable_amount numeric(38,8) NOT NULL, expires_at timestamptz, idempotency_key uuid NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE order_items (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), order_id uuid NOT NULL REFERENCES orders(id), product_id uuid REFERENCES mall_products(id), item_type varchar(40) NOT NULL, quantity int NOT NULL CHECK(quantity>0), unit_price numeric(38,8) NOT NULL, benefit_snapshot jsonb NOT NULL);\nCREATE TABLE payment_orders (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), order_id uuid NOT NULL UNIQUE REFERENCES orders(id), payment_method varchar(32), provider varchar(32), provider_trade_no varchar(128) UNIQUE, status varchar(32) NOT NULL, paid_amount numeric(18,2), paid_at timestamptz, created_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE payment_events (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), payment_order_id uuid NOT NULL REFERENCES payment_orders(id), event_type varchar(40) NOT NULL, provider_event_id varchar(128), payload_hash varchar(128), verified boolean NOT NULL DEFAULT false, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(provider_event_id));\nCREATE TABLE payment_settlement_records (order_id uuid PRIMARY KEY REFERENCES orders(id), settled_at timestamptz NOT NULL, result jsonb NOT NULL);\nCREATE TABLE manual_payment_submissions (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), order_id uuid NOT NULL REFERENCES orders(id), version int NOT NULL, proof_file_id uuid NOT NULL, status varchar(32) NOT NULL, submitted_at timestamptz NOT NULL DEFAULT now(), UNIQUE(order_id,version));\n\n'''
    sql += '''CREATE TABLE commission_records (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), source_business_type varchar(40) NOT NULL, source_business_id varchar(100) NOT NULL, beneficiary_user_id uuid NOT NULL REFERENCES users(id), source_user_id uuid NOT NULL REFERENCES users(id), commission_type varchar(20) NOT NULL, level smallint NOT NULL CHECK(level IN (1,2)), rate numeric(8,6) NOT NULL, amount numeric(38,8) NOT NULL, status varchar(24) NOT NULL, wallet_transaction_id uuid, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(source_business_id,beneficiary_user_id,commission_type,level));\nCREATE TABLE identity_sessions (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), status varchar(32) NOT NULL, real_name_ciphertext text, id_number_ciphertext text, id_number_hash varchar(128), actions jsonb NOT NULL, provider_result_code varchar(20), created_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz);\nCREATE TABLE identity_captures (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), session_id uuid NOT NULL REFERENCES identity_sessions(id), photo_file_id uuid, video_file_id uuid, status varchar(24) NOT NULL, created_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE identity_bindings (user_id uuid PRIMARY KEY REFERENCES users(id), id_number_hash varchar(128) NOT NULL UNIQUE, verified_at timestamptz NOT NULL);\nCREATE TABLE withdrawal_tiers (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), amount numeric(18,2) NOT NULL UNIQUE, max_per_day int NOT NULL, max_total int, fee_amount numeric(18,2) NOT NULL DEFAULT 0, enabled boolean NOT NULL DEFAULT true);\nCREATE TABLE user_payment_accounts (user_id uuid PRIMARY KEY REFERENCES users(id), account_type varchar(20) NOT NULL DEFAULT 'ALIPAY', real_name_ciphertext text NOT NULL, account_ciphertext text NOT NULL, account_hash varchar(128) NOT NULL, verified_at timestamptz NOT NULL, updated_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE withdrawal_orders (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), withdrawal_no varchar(64) UNIQUE NOT NULL, user_id uuid NOT NULL REFERENCES users(id), tier_id uuid NOT NULL REFERENCES withdrawal_tiers(id), amount numeric(18,2) NOT NULL, fee_amount numeric(18,2) NOT NULL, status varchar(32) NOT NULL, provider_order_no varchar(128) UNIQUE, idempotency_key uuid NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz);\n\n'''
    sql += '''CREATE TABLE file_objects (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), bucket varchar(120) NOT NULL, object_key text NOT NULL UNIQUE, purpose varchar(40) NOT NULL, visibility varchar(20) NOT NULL, mime_type varchar(120), size_bytes bigint, sha256 varchar(64), status varchar(24) NOT NULL, owner_user_id uuid REFERENCES users(id), created_at timestamptz NOT NULL DEFAULT now(), delete_after timestamptz);\nCREATE TABLE notifications (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), type varchar(40) NOT NULL, title varchar(120) NOT NULL, body text NOT NULL, business_type varchar(40), business_id varchar(100), created_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE notification_reads (notification_id uuid NOT NULL REFERENCES notifications(id), user_id uuid NOT NULL REFERENCES users(id), read_at timestamptz NOT NULL, PRIMARY KEY(notification_id,user_id));\nCREATE TABLE runtime_configs (config_key varchar(160) PRIMARY KEY, value_json jsonb NOT NULL, value_type varchar(24) NOT NULL, sensitive boolean NOT NULL DEFAULT false, updated_by uuid, updated_at timestamptz NOT NULL DEFAULT now());\nCREATE TABLE outbox_events (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), aggregate_type varchar(40) NOT NULL, aggregate_id varchar(100) NOT NULL, event_type varchar(80) NOT NULL, payload jsonb NOT NULL, status varchar(20) NOT NULL DEFAULT 'PENDING', attempts int NOT NULL DEFAULT 0, available_at timestamptz NOT NULL DEFAULT now(), created_at timestamptz NOT NULL DEFAULT now());\n'''
    write_text(BASE/'03_SPECS/database/0001_xkjy_core_schema.sql',sql)

    db_md='# 星矿纪元数据库设计目录\n\n## 设计原则\n\n- PostgreSQL；金额和积分使用 `NUMERIC`。\n- 所有钱包变化通过 `wallet_transactions + wallet_entries`，禁止直接改余额。\n- 支付、合成、领取、转赠、佣金、提现均有唯一幂等键。\n- 状态变化保留事件或时间线，不物理覆盖审计历史。\n- 私有配置只以环境变量或服务器秘密文件注入。\n\n'
    for group,ts in tables.items():
        db_md += f'## {group}\n\n' + '\n'.join(f'- `{t}`' for t in ts) + '\n\n'
    write_text(BASE/'03_SPECS/database/DATABASE_SCHEMA.md',db_md)


# ---------------------------------------------------------------------------
# Documentation and README
# ---------------------------------------------------------------------------
def generate_docs():
    readme='''# 星矿纪元 V1.1.0：Codex 开始执行

## 读取顺序

1. `03_SPECS/RESOLVED_RULESET.yaml`
2. `03_SPECS/PROJECT_PROFILE.yaml`
3. `03_SPECS/MODULE_SELECTION.yaml`
4. `02_DOCS/星矿纪元_前后端与视觉资源完整开发文档_V1.1.0.md`
5. `03_SPECS/FEATURE_MATRIX.yaml` 与 `03_SPECS/RELEASE_PLAN.yaml`
6. `03_SPECS/PAGE_INDEX.yaml`
7. 当前版本涉及的 `03_SPECS/pages/<PageID>.yaml`
8. 对应 `10_HTML/<平台>/<PageID>__<StateID>.html` 与 `04_UI/<平台>/<PageID>__<StateID>.png`
9. `03_SPECS/contracts`、`03_SPECS/database`、资源映射与测试清单
10. `01_RULES/MOTHER_TEMPLATE` 内原始私有母版

## 不可协商规则

- 先按项目所有者当前商业模式完整开发，不擅自重构模式。
- 支付、实名认证、Cloudflare R2、邮箱和提现直接复用母版私有实现；不得再次向项目所有者索取密钥、账号、证书或密码。
- 私有母版及本包不得上传公开仓库。运行时秘密只安装到服务器私有目录或环境变量。
- 首页必须是原生2D矿机合成游戏场景，不得改成普通数据卡片首页。
- 视觉实现以独立 HTML/CSS/SVG 和 PNG 效果图为准；不得仅凭文字自行发挥。
- 页面返回必须保持滚动、Tab、筛选、分页、草稿和已加载数据，不得回顶、白屏或无条件重载。
- 禁止文字、字母、数字、Emoji、Icon Font代替图标。
- 所有资产变化通过事务账本；所有关键写操作必须幂等。
- 每个涉及Android的版本交付已签名APK、功能清单、测试清单、已知问题和真机截图。

## 执行方式

按 `P00 → P11` 顺序推进。每次只实现当前版本和其明确依赖，完成后更新 `CURRENT_RELEASE.yaml`、`DELIVERY_STATUS.yaml` 和 `RELEASE_MANIFEST.yaml`，然后停止扩展。
'''
    write_text(BASE/'00_README/README_交给Codex.md',readme)

    prompt='''请解压本包并在服务器工作目录中执行。先完整阅读 `00_README/README_交给Codex.md`，再按其中顺序读取规则、功能文档、Page ID、HTML源、PNG效果图、API合同、数据库结构和母版私有能力。\n\n本项目名称为“星矿纪元”。商业模式按文档冻结，不讨论替换方案。支付、实名认证、Cloudflare R2、邮箱、支付宝提现的真实配置已经在随包母版中，禁止再次向我索取密钥、账号、密码或证书。仅在真实服务器预检返回明确的鉴权失败、证书失效、权限不足或服务商错误时，提交带命令输出和日志证据的阻断报告。\n\n从 P00 开始，按 P00→P11 顺序开发。不要一次性空建全部页面；每版完成真实闭环、后台、迁移、测试和签名APK。UI必须按 Page ID 对应效果图逐页实现，所有返回状态、图标、音效和特效按合同执行。每版结束时输出APK、SHA-256、功能完成清单、测试清单、已知问题和下一版入口。'''
    write_text(BASE/'00_README/CODEX_直接执行指令.txt',prompt)

    version='''# V1.1.0 版本说明

本版是在 V1.0.0 功能冻结基础上的“视觉、素材、音频和Codex执行完整化版本”。

## 新增交付

- 212 个基础 Page ID 与 32 个关键状态，共 244 张独立效果图；
- 每张效果图对应确定性 HTML/CSS/SVG 源文件；
- 36 级原创矿机 SVG、透明 PNG 与待机/工作精灵图；
- App Logo、安卓启动图、品牌图、邀请海报和多密度图标；
- 游戏场景、双积分、推广卡和通用SVG图标；
- 5 首原创程序化 BGM 与完整交互音效；
- 完整 Design Token、Page Spec、State Matrix、Icon Registry、Navigation Contract；
- API合同、错误码、数据库目录和核心迁移SQL；
- Codex直接执行指令、版本计划和验收脚本。

## 继承

- 母版 G-001~G-047、轻量平台基线和页面状态保持规则；
- 母版邮箱、Cloudflare R2、实名认证、XApay、人工扫码、支付宝证书提现；
- 项目所有者冻结的商业模式、二级提成、双积分、红包卡、求购集市和每日价格上涨规则。
'''
    write_text(BASE/'00_README/版本说明.md',version)

    doc='''# 星矿纪元前后端与视觉资源完整开发文档 V1.1.0

## 1. 项目定义

星矿纪元是 Android 原生矿机合成游戏化平台。首页承担矿机购买、拖动、合成、持续产出、主动领取和长期成长；项目板块承担用户图文推广、浏览任务和头条/置顶/刷新服务；商城只出售虚拟商品；发现页默认进入积分求购集市；我的页面承载三资产、邀请、提成、实名和提现。

当前商业模式按项目所有者原设定冻结：星矿值初始参考价 0.5 元、每日复利上涨 1%；红包卡使用主副积分兑换账户余额；账户余额可按固定档位提现；一级与二级分别计算积分提成和现金消费佣金；积分支付推广服务不产生现金佣金。

## 2. 固定母版能力

支付、实名认证、Cloudflare R2、邮箱和支付宝提现不得重新选型。Codex直接读取 `01_RULES/MOTHER_TEMPLATE` 内 V1.4.2 私有母版，并将真实配置安装到服务端私有运行环境。任何私钥、AppCode、SMTP密码、R2密钥、XApay密钥和支付宝证书不得进入Android、H5、管理后台前端、日志或公开仓库。

## 3. 游戏核心

- 4×4 棋盘共 16 格，初始开放 12 格，8/16/24/32 级依次解锁余下格子。
- 首次注册只发一台 1 级矿机；完成首次产出气泡后发第二台，引导合成 2 级。
- 两台同等级合成下一等级；最高 36 级；不同等级交换；空位移动；锁定矿机不可操作。
- 商店可购买等级为 `max(1, highest_level - 4)`，最高直接购买 32 级。
- 矿机购买只消耗星矿值；除矿机购买外，标准每消耗 1 星矿值额外消耗 2 能源芯片。
- 生产采用服务端惰性结算，默认离线累计上限 8 小时；客户端动画不改变最终资产。
- 36 级名称、素材、默认产出和价格见 `06_MINERS/MINER_MANIFEST.yaml`。

## 4. 项目推广

项目支持标题、简介、详情、最多 8 张图片、项目链接和联系方式。默认发布页不显示分类，系统归入“综合”；后台可以开启发布者分类选择。推荐排序固定为：头条+置顶、头条、置顶+刷新、置顶、刷新、普通最新。

浏览任务进入统一项目详情页自动开始。App在前台且详情可见时每 5 秒发送心跳，离开或进入后台暂停，达到秒数后服务端自动发放星矿值，不再要求用户点击领取。进度条只能轻量贴边，不能遮挡内容。

## 5. 三资产与集市

- `STAR_POINT`：星矿值，矿机和任务产出；购买矿机、兑换能源芯片、购买服务和赠送。
- `ENERGY_CHIP`：能源芯片，星矿值按 2:1 单向兑换；作为非矿机消费和赠送的附加消耗。
- `CASH_BALANCE`：账户余额，现金佣金、红包卡兑换和平台福利来源；可支付允许商品并申请提现。

积分求购单包括数量、单价、联系方式、备注和有效期，按单价降序、创建时间降序展示。平台内赠送通过收款UID、二次确认和独立6位赠送密码执行。

## 6. 商城、会员、订单与支付

商城禁止实物和物流。商品类型限定为会员、头条卡、置顶卡、刷新卡、红包卡、补给箱和已实现处理器的虚拟权益。星耀会员默认 365 天，对头条、置顶、刷新按 5 折结算，并在项目列表、详情和个人中心显示专属标识。

所有现金类业务进入原生 Android 收银台。XApay只支持母版定义的支付宝和微信；QQ仅为人工扫码。人工扫码必须选择后台启用的收款码、上传付款截图、财务审核后调用统一结算器。异步回调、主动查单和人工审核最终都调用同一 `settlePaidOrder`，保证权益与返佣只发一次。

## 7. 邀请、提成、实名与提现

UID为纯数字，从 2026 开始；邀请码等于 UID；关系最多两级。积分提成默认一级 10%、二级 5%；消费佣金默认一级 10%、二级 5%，比例分开配置。现金或账户余额支付且订单在白名单才计现金佣金；积分支付不计。

实名使用 CameraX 采集 5~8 秒动作视频和清晰照片，随机动作来自眨眼、左转、右转、张嘴；静默上传R2私有路径，本地零留存；第三方结果 1001 成功、1002 重采或人工复核、1003/1004 失败。

提现前必须实名和绑定支付宝，档位由后台配置，初始示例 0.3、5、10 元。创建提现时将账户余额从可用转冻结；明确成功转支出，明确失败退回，未知状态保持冻结并主动查单。

## 8. 页面、视觉和资源

本包包含 212 个基础页面与 32 个关键状态。每个页面具备独立 Page Spec、Navigation Contract、HTML源和PNG效果图。Android效果图为 780×1688；管理后台为 1440×900。视觉采用深空蓝、矿业橙金和能源青色；首页是2D游戏矿区，业务页降低装饰密度但保持同一世界观。

所有图标只能从 `ICON_REGISTRY.yaml` 引用实际 SVG；不得使用汉字、字母、Emoji或Icon Font代替。返回时保留列表锚点、偏移、Tab、搜索、筛选、分页、展开项、选中项、草稿和已加载内容。

## 9. 音频与特效

BGM、交互音效和矿机动画全部使用资源ID绑定。设置页分别控制背景音乐、游戏音效和震动。合成、领取、开箱、解锁和支付结果必须具备视觉反馈；关闭声音后仍保留视觉反馈。

## 10. 开发版本

P00基线、P01账号、P02游戏核心、P03完整成长、P04项目、P05任务推广、P06商城会员订单、P07支付、P08钱包集市、P09邀请佣金、P10实名提现、P11发布候选。不得用空页面一次性宣称完成；每版按真实闭环交付。

## 11. 事实源

- 功能：本文件、`FEATURE_MATRIX.yaml`、API合同和数据库结构。
- 页面：`PAGE_INDEX.yaml`、页面规格、HTML和PNG。
- 资源：品牌、矿机、VFX、Audio Manifest。
- 状态：`CURRENT_RELEASE.yaml`、`DELIVERY_STATUS.yaml`、代码、迁移和测试报告。
'''
    write_text(BASE/'02_DOCS/星矿纪元_前后端与视觉资源完整开发文档_V1.1.0.md',doc)

    visual='''# 视觉与资源实现说明

## 视觉主题

“星际矿业 + 卡通工业科技”，不是纯白工具型App，也不是幼龄化猫咪合成游戏。首页场景采用深空、行星、矿脉、机械平台和发光晶体；业务页面沿用橙金奖励色、能源青色和深空蓝导航。

## 效果图

- Android/H5：390×844 CSS像素，2倍渲染为780×1688 PNG。
- Admin：1440×900 PNG。
- 每张PNG必须与同名HTML一一对应。
- PNG用于像素验收，HTML/CSS/SVG用于尺寸、色值和结构追溯。

## 资源目录

- `05_BRAND`：Logo、启动图、品牌图、邀请海报。
- `06_MINERS`：36级矿机SVG、PNG、清单。
- `07_GAME_ASSETS`：背景、双积分图标、推广卡、通用SVG图标。
- `08_VFX`：矿机待机/工作精灵图和核心特效。
- `09_AUDIO`：BGM、SFX、映射。

## 禁止

不得从参考截图直接裁切素材；不得使用文字代图标；不得把效果图中的示例数据写死成真实业务数据；不得因为图片数量多而跳过Page ID绑定。
'''
    write_text(BASE/'02_DOCS/视觉与资源实现说明.md',visual)

    frontend='''# 前端实现约束

- Android：Kotlin + Jetpack Compose + Material 3，游戏棋盘使用Compose自定义布局、Canvas与Pointer Input。
- 不使用Unity重做全App；不使用WebView承载矿场首页。
- 每个底部Tab独立返回栈；状态存入ViewModel/SavedStateHandle/Route Store。
- 列表使用稳定业务ID作为key；返回不重建列表。
- 先本地播放拖动反馈，再提交服务端；版本冲突时平滑回滚并同步最新棋盘。
- BGM使用Media3，短音效使用SoundPool，资源ID见Audio Cue Map。
- CameraX只在实名采集页创建，页面销毁立即释放。
- 所有上传先申请后端票据，不在客户端保存R2凭据。
- 收银台为原生页面；支付回跳后只查单，不在客户端直接发货。
'''
    write_text(BASE/'02_DOCS/前端实现约束.md',frontend)

    backend='''# 后端实现约束

- Go模块化单体，第一阶段不拆微服务。
- PostgreSQL保存核心业务与账本；Redis用于限流、验证码、短锁和缓存；Outbox Worker处理可靠事件。
- 用户矿机生产采用惰性结算，不为每个用户创建分钟级定时任务。
- 钱包使用双分录或等价平衡分录；禁止业务代码直接修改余额。
- 合成、领取、购买、赠送、订单结算、佣金和提现均使用数据库事务、行锁、幂等键和唯一约束。
- 支付回调、主动查单、人工审核都进入统一状态机和结算器。
- 私有配置从母版安装到服务器秘密目录或环境变量；日志只记录配置存在状态，不输出值。
- 每个状态变化写结构化日志和审计记录；金额、身份证、支付宝账号和对象URL脱敏。
'''
    write_text(BASE/'02_DOCS/后端实现约束.md',backend)

    tests='''# 交付与验收清单

- [ ] 当前版本功能闭环完成，不存在只展示无后端的假页面。
- [ ] 数据库迁移可在空库执行，可在已有库增量执行。
- [ ] 所有关键写接口幂等测试通过。
- [ ] 账本借贷平衡、余额不为负。
- [ ] 合成并发、领取并发、订单并发和提现并发通过。
- [ ] XApay验签、金额校验、重复回调、主动查单补单通过。
- [ ] 人工扫码未审核不发权益；审核通过只结算一次。
- [ ] 实名1001/1002/1003/1004和服务异常映射正确。
- [ ] 提现成功、明确失败、未知状态和重复出款测试通过。
- [ ] 每个受影响Page ID按效果图截图比对。
- [ ] 深度滚动返回保持位置；Tab、筛选、分页和草稿不丢失。
- [ ] 不存在文字、Emoji或Icon Font代图标。
- [ ] 真机完成注册、游戏、项目、支付、实名和提现主链路。
- [ ] 交付签名APK、SHA-256、功能清单、测试清单和已知问题。
'''
    write_text(BASE/'12_TESTS/RELEASE_DELIVERY_CHECKLIST.md',tests)

    write_yaml(BASE/'03_SPECS/DELIVERY_STATUS.yaml', {'project':'星矿纪元','version':'1.1.0','package_ready':False,'artifacts':{'page_specs':'PENDING_GENERATION','effect_png':'PENDING_RENDER','miners':'PENDING_GENERATION','audio':'PENDING_GENERATION','docx':'PENDING_GENERATION','manifest':'PENDING'}})


def main():
    generate_project_files()
    generate_icons()
    generate_miners()
    generate_brand_and_backgrounds()
    generate_page_specs()
    generate_contracts_and_schema()
    generate_docs()
    print('core generated')

if __name__=='__main__':
    main()
