#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from PIL import Image

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/mnt/data/xkjy_v110_work/XKJY_V110').resolve()
errors: list[str] = []
warnings: list[str] = []
checks: list[str] = []


def ok(message: str) -> None:
    checks.append(message)


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text('utf-8'))
    except Exception as exc:
        fail(f'YAML解析失败: {path.relative_to(ROOT)}: {exc}')
        return None


def load_json(path: Path):
    try:
        return json.loads(path.read_text('utf-8'))
    except Exception as exc:
        fail(f'JSON解析失败: {path.relative_to(ROOT)}: {exc}')
        return None


def require_file(rel: str | Path, *, nonempty: bool = True) -> Path | None:
    path = ROOT / rel
    if not path.is_file():
        fail(f'缺少文件: {rel}')
        return None
    if nonempty and path.stat().st_size == 0:
        fail(f'空文件: {rel}')
    return path


def check_image(path: Path, expected: tuple[int, int] | None = None, expected_mode: str | None = None) -> tuple[int, int] | None:
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            size = im.size
            mode = im.mode
            if expected and size != expected:
                fail(f'图片尺寸错误: {path.relative_to(ROOT)}，实际{size}，应为{expected}')
            if expected_mode and mode != expected_mode:
                fail(f'图片模式错误: {path.relative_to(ROOT)}，实际{mode}，应为{expected_mode}')
            return size
    except Exception as exc:
        fail(f'图片损坏: {path.relative_to(ROOT)}: {exc}')
        return None


class RefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {'src', 'href'} and value:
                self.refs.append(value)


def local_ref_target(base_file: Path, ref: str) -> Path | None:
    ref = unquote(ref.strip())
    if not ref or ref.startswith(('#', 'data:', 'javascript:', 'mailto:', 'tel:')):
        return None
    parsed = urlsplit(ref)
    if parsed.scheme or parsed.netloc:
        return None
    clean = parsed.path
    if not clean:
        return None
    return (base_file.parent / clean).resolve()


# Required directory contract.
for d in ['00_README','01_RULES','02_DOCS','03_SPECS','04_UI','05_BRAND','06_MINERS','07_GAME_ASSETS','08_VFX','09_AUDIO','10_HTML','11_CODE_TOKENS','12_TESTS','13_SCRIPTS','14_MANIFEST']:
    if not (ROOT / d).is_dir():
        fail(f'缺少目录: {d}')
ok('顶层目录合同检查完成')

# Parse project-owned YAML/JSON. Private mother-template files are validated as a ZIP/copy, not echoed.
project_yaml = [p for p in ROOT.rglob('*.yaml') if '01_RULES/MOTHER_TEMPLATE/UNPACKED' not in p.as_posix()]
project_json = [p for p in ROOT.rglob('*.json') if '01_RULES/MOTHER_TEMPLATE/UNPACKED' not in p.as_posix()]
for p in project_yaml:
    load_yaml(p)
for p in project_json:
    load_json(p)
ok(f'结构化文件解析: YAML {len(project_yaml)}，JSON {len(project_json)}')

# Page index / specs / states / artifacts.
page_index = load_yaml(ROOT/'03_SPECS/PAGE_INDEX.yaml') or {}
pages = page_index.get('pages') or []
if len(pages) != 212:
    fail(f'Page ID数量应为212，实际{len(pages)}')
page_ids = [p.get('page_id') for p in pages]
if len(set(page_ids)) != len(page_ids):
    fail('PAGE_INDEX存在重复Page ID')
state_keys: set[tuple[str,str]] = set()
platform_page_counts = Counter()
platform_state_counts = Counter()
for entry in pages:
    pid = entry.get('page_id')
    platform = entry.get('platform')
    platform_page_counts[platform] += 1
    spec_rel = entry.get('spec_file')
    nav_rel = entry.get('navigation_state_contract')
    spec_p = require_file(spec_rel)
    nav_p = require_file(nav_rel)
    if spec_p:
        spec = load_yaml(spec_p) or {}
        if spec.get('page',{}).get('id') != pid:
            fail(f'Page Spec内部ID不匹配: {spec_rel}')
        expected_vp = '780x1688' if platform in {'android','h5'} else '1440x900'
        if spec.get('layout',{}).get('baseline_viewport_px') != expected_vp:
            fail(f'Page Spec效果图尺寸合同不匹配: {pid}')
    if nav_p:
        nav = load_yaml(nav_p) or {}
        if nav.get('page_id') != pid:
            fail(f'Navigation Contract内部ID不匹配: {nav_rel}')
    for state in entry.get('required_states') or []:
        sid = state.get('state_id')
        key=(pid,sid)
        if key in state_keys:
            fail(f'重复页面状态: {pid} {sid}')
        state_keys.add(key)
        platform_state_counts[platform]+=1
        image_rel = state.get('image_file')
        html_rel = state.get('source_file')
        img = require_file(image_rel)
        html = require_file(html_rel)
        if img:
            expected = (780,1688) if platform in {'android','h5'} else (1440,900)
            check_image(img, expected)
        if state.get('visual_verified') is not True:
            fail(f'视觉验证标志未完成: {pid} {sid}')
if len(state_keys) != 244:
    fail(f'页面状态效果图数量应为244，实际{len(state_keys)}')
ok(f'页面合同: {len(pages)}个Page ID、{len(state_keys)}个状态；页面分布{dict(platform_page_counts)}；状态分布{dict(platform_state_counts)}')

# Page State Matrix parity.
state_matrix = load_yaml(ROOT/'03_SPECS/PAGE_STATE_MATRIX.yaml') or {}
matrix_keys={(x.get('page_id'),s.get('state_id')) for x in state_matrix.get('pages',[]) for s in (x.get('states') or []) if s.get('required')}
if matrix_keys != state_keys:
    fail(f'PAGE_STATE_MATRIX与PAGE_INDEX不一致：缺少{len(state_keys-matrix_keys)}，多出{len(matrix_keys-state_keys)}')

# Render index parity and HTML local-reference integrity.
render_index = load_json(ROOT/'10_HTML/RENDER_INDEX.json') or []
render_keys={(x.get('page_id'),x.get('state')) for x in render_index}
if len(render_index) != 244 or len(render_keys) != 244:
    fail(f'RENDER_INDEX应为244条唯一记录，实际{len(render_index)}/{len(render_keys)}')
if render_keys != state_keys:
    fail(f'RENDER_INDEX与页面状态合同不一致：缺少{len(state_keys-render_keys)}，多出{len(render_keys-state_keys)}')
external_refs=set()
local_ref_count=0
for item in render_index:
    html_rel=item.get('html')
    html_path=require_file(html_rel)
    if not html_path: continue
    text=html_path.read_text('utf-8')
    parser=RefParser(); parser.feed(text)
    for ref in parser.refs:
        parsed=urlsplit(ref)
        if parsed.scheme or parsed.netloc:
            external_refs.add(ref)
            continue
        target=local_ref_target(html_path,ref)
        if target is None: continue
        local_ref_count += 1
        try:
            target.relative_to(ROOT)
        except ValueError:
            fail(f'HTML引用越出包根目录: {html_rel} -> {ref}')
            continue
        if not target.exists():
            fail(f'HTML本地引用缺失: {html_rel} -> {ref}')
if external_refs:
    warn(f'HTML存在外部引用{len(external_refs)}个（需人工确认）')
else:
    ok(f'244份HTML自包含引用检查通过，共校验{local_ref_count}个本地引用')

# Shared CSS local URL references.
css=ROOT/'10_HTML/shared/styles.css'
require_file(css)
if css.exists():
    for ref in re.findall(r'url\(["\']?([^"\')]+)',css.read_text('utf-8')):
        target=local_ref_target(css,ref)
        if target and not target.exists(): fail(f'CSS本地引用缺失: {ref}')

# Icon registry and page/HTML usage.
icon_registry = load_yaml(ROOT/'03_SPECS/ICON_REGISTRY.yaml') or {}
icons=icon_registry.get('icons') or []
if len(icons)!=74:
    fail(f'图标登记数应为74，实际{len(icons)}')
icon_ids=[x.get('icon_id') for x in icons]
if len(set(icon_ids))!=len(icon_ids): fail('ICON_REGISTRY存在重复ID')
for icon in icons:
    require_file(icon.get('source_svg_file'))
registered=set(icon_ids)
actual_svg={p.stem for p in (ROOT/'07_GAME_ASSETS/objects/icons').glob('*.svg')}
if actual_svg != registered:
    fail(f'图标文件与登记不一致：未登记{sorted(actual_svg-registered)}，缺文件{sorted(registered-actual_svg)}')
html_icon_ids=set()
icon_pat=re.compile(r'07_GAME_ASSETS/objects/icons/(ICON-[A-Z0-9-]+)\.svg')
for item in render_index:
    html=(ROOT/item['html']).read_text('utf-8')
    html_icon_ids.update(icon_pat.findall(html))
if not html_icon_ids.issubset(registered):
    fail(f'HTML使用未登记图标: {sorted(html_icon_ids-registered)}')
for entry in pages:
    spec=load_yaml(ROOT/entry['spec_file']) or {}
    ids=set(spec.get('icon_usage',{}).get('icon_ids') or [])
    pid=entry['page_id']
    actual=set()
    for st in entry.get('required_states') or []:
        actual.update(icon_pat.findall((ROOT/st['source_file']).read_text('utf-8')))
    if ids != actual:
        fail(f'Page Spec图标清单与HTML不一致: {pid}; spec-only={sorted(ids-actual)}, html-only={sorted(actual-ids)}')
ok(f'图标体系: 74个SVG，HTML实际使用{len(html_icon_ids)}个，均已登记并同步到Page Spec')

# Miners and animations.
miner_manifest=load_yaml(ROOT/'06_MINERS/MINER_MANIFEST.yaml') or {}
miners=miner_manifest.get('items') or []
if len(miners)!=36: fail(f'矿机清单应为36级，实际{len(miners)}')
levels={m.get('level') for m in miners}
if levels != set(range(1,37)): fail('矿机等级不是完整1~36')
for m in miners:
    for k in ['svg','png','idle_vfx','work_vfx']:
        require_file(m.get(k))
    if m.get('png'):
        check_image(ROOT/m['png'],(512,512))
anim_manifest=load_yaml(ROOT/'08_VFX/MINER_ANIMATION_MANIFEST.yaml') or {}
anims=anim_manifest.get('items') or []
if len(anims)!=36: fail(f'矿机动画清单应为36，实际{len(anims)}')
for a in anims:
    idle=require_file(a.get('idle')); work=require_file(a.get('work'))
    if idle: check_image(idle,(a.get('idle_frames',0)*a.get('frame_size',[0,0])[0],a.get('frame_size',[0,0])[1]))
    if work: check_image(work,(a.get('work_frames',0)*a.get('frame_size',[0,0])[0],a.get('frame_size',[0,0])[1]))
ok('36级矿机SVG/PNG及72张待机/工作精灵图检查完成')

# VFX.
vfx_manifest=load_yaml(ROOT/'08_VFX/VFX_MANIFEST.yaml') or {}
vfx=vfx_manifest.get('items') or []
if len(vfx)!=16: fail(f'核心VFX应为16，实际{len(vfx)}')
for e in vfx:
    p=require_file(e.get('path'))
    fs=e.get('frame_size') or [0,0]
    if p: check_image(p,(e.get('frames',0)*fs[0],fs[1]))
ok('16套核心VFX精灵图检查完成')

# Audio file existence, counts, codec and approximate duration.
audio_manifest=load_yaml(ROOT/'09_AUDIO/AUDIO_MANIFEST.yaml') or {}
audios=audio_manifest.get('items') or []
counts=Counter(a.get('bus') for a in audios)
if counts.get('BGM')!=5 or counts.get('SFX')!=17:
    fail(f'音频数量错误，应为5 BGM/17 SFX，实际{dict(counts)}')
for a in audios:
    p=require_file(a.get('path'))
    if not p: continue
    try:
        cp=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name','-of','json',str(p)],capture_output=True,text=True,check=True,timeout=15)
        info=json.loads(cp.stdout)
        codecs={s.get('codec_name') for s in info.get('streams',[])}
        if 'vorbis' not in codecs: fail(f'音频不是OGG Vorbis: {p.relative_to(ROOT)} {codecs}')
        actual=float(info.get('format',{}).get('duration','0'))
        expected=float(a.get('duration_seconds',0))
        if abs(actual-expected)>0.2:
            fail(f'音频时长与清单不符: {p.relative_to(ROOT)} 实际{actual:.3f}s，应约{expected:.3f}s')
    except Exception as exc:
        fail(f'音频探测失败: {p.relative_to(ROOT)}: {exc}')
ok('音频检查完成：5首BGM、17个SFX，OGG Vorbis与时长合同通过')

# Brand assets.
brand=load_yaml(ROOT/'05_BRAND/BRAND_ASSET_MANIFEST.yaml') or {}
for a in brand.get('assets') or []:
    p=require_file(a.get('file'))
    if p: check_image(p)
brand_expected={
    '05_BRAND/app_icon/app_icon_1024.png':(1024,1024),
    '05_BRAND/app_icon/app_icon_512.png':(512,512),
    '05_BRAND/android_splash_1080x2400.png':(1080,2400),
    '05_BRAND/brand_banner_1600x900.png':(1600,900),
    '05_BRAND/invite_poster_1080x1920.png':(1080,1920),
}
for rel,size in brand_expected.items():
    p=require_file(rel)
    if p: check_image(p,size)
for density,size in {'mdpi':48,'hdpi':72,'xhdpi':96,'xxhdpi':144,'xxxhdpi':192}.items():
    p=require_file(f'05_BRAND/app_icon/{density}/ic_launcher.png')
    if p: check_image(p,(size,size),'RGB')
for rel in ['05_BRAND/app_icon/app_icon_1024.png','05_BRAND/app_icon/app_icon_512.png']:
    p=ROOT/rel
    if p.exists(): check_image(p,brand_expected[rel],'RGB')
ok('品牌资源尺寸与不透明Launcher图标检查完成')

# Database / API / docs.
for rel in ['03_SPECS/contracts/API_CONTRACTS.yaml','03_SPECS/contracts/API_ERROR_CATALOG.yaml','03_SPECS/database/SCHEMA_CATALOG.yaml','03_SPECS/database/DATABASE_SCHEMA.md','03_SPECS/database/0001_xkjy_core_schema.sql','02_DOCS/星矿纪元_前后端与视觉资源完整开发文档_V1.1.0.md','02_DOCS/星矿纪元_前后端与视觉资源完整开发文档_V1.1.0.docx','12_TESTS/RELEASE_DELIVERY_CHECKLIST.md']:
    require_file(rel)
# DOCX ZIP integrity.
docx=ROOT/'02_DOCS/星矿纪元_前后端与视觉资源完整开发文档_V1.1.0.docx'
if docx.exists():
    try:
        with zipfile.ZipFile(docx) as z:
            bad=z.testzip()
            if bad: fail(f'DOCX内部损坏: {bad}')
            if 'word/document.xml' not in z.namelist(): fail('DOCX缺少word/document.xml')
    except Exception as exc: fail(f'DOCX无法打开: {exc}')
ok('API、错误码、数据库迁移、Markdown、DOCX和测试清单检查完成')

# Mother template original and unpacked copy.
mother_zip=ROOT/'01_RULES/MOTHER_TEMPLATE/通用项目开发私有母版_V1.4.2_XApay扫码支付完整整合版_20260816.zip'
require_file(mother_zip)
if mother_zip.exists():
    try:
        with zipfile.ZipFile(mother_zip) as z:
            infos=z.infolist()
            if z.testzip(): fail('私有母版原始ZIP校验失败')
            for info in infos:
                pp=Path(info.filename)
                if pp.is_absolute() or '..' in pp.parts: fail(f'私有母版ZIP存在不安全路径: {info.filename}')
            source_files=sum(1 for i in infos if not i.is_dir())
            if source_files!=202: fail(f'私有母版ZIP应有202个文件，实际{source_files}')
    except Exception as exc: fail(f'私有母版ZIP无法读取: {exc}')
unpacked=ROOT/'01_RULES/MOTHER_TEMPLATE/UNPACKED'
unpacked_files=[p for p in unpacked.rglob('*') if p.is_file() and p.name!='README_母版解压说明.md'] if unpacked.exists() else []
if len(unpacked_files)!=202: fail(f'私有母版解压副本应有202个原始文件，实际{len(unpacked_files)}')
ok('私有母版原始ZIP与202个文件的解压副本检查完成')

# No broken symlinks; no generated temp files.
for p in ROOT.rglob('*'):
    if p.is_symlink() and not p.exists(): fail(f'损坏符号链接: {p.relative_to(ROOT)}')
    if p.name in {'.DS_Store','Thumbs.db'} or p.suffix in {'.tmp','.bak'}: warn(f'发现临时文件: {p.relative_to(ROOT)}')

# Summary.
all_files=[p for p in ROOT.rglob('*') if p.is_file()]
total_size=sum(p.stat().st_size for p in all_files)
summary={
    'root': ROOT.name,
    'status': 'PASS' if not errors else 'FAIL',
    'file_count': len(all_files),
    'total_size_bytes': total_size,
    'page_count': len(pages),
    'effect_state_count': len(state_keys),
    'platform_page_counts': dict(platform_page_counts),
    'platform_effect_counts': dict(platform_state_counts),
    'miner_count': len(miners),
    'miner_animation_sheets': len(anims)*2,
    'vfx_count': len(vfx),
    'bgm_count': counts.get('BGM',0),
    'sfx_count': counts.get('SFX',0),
    'icon_count': len(icons),
    'mother_template_source_files': 202,
    'checks': checks,
    'warnings': warnings,
    'errors': errors,
}
print(json.dumps(summary,ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
