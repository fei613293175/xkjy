# 星矿纪元 V1.3.0：Codex 唯一执行入口

> 仓库状态已于 2026-08-17 封板为 `V1.3.0-PREDEV-HARDENED`。先读取 `PREDEV_HARDENING.md` 与 `03_SPECS/PREDEV_BASELINE.yaml`。本仓库不含任何真实凭据、私钥、证书、V1.2.0 视觉资料或私有母版 ZIP；原始交接压缩包只保留在仓库外作为审计源。

## 1. 本包性质

本仓库是从《星矿纪元》完整合并开发交接包净化得到的开发事实源。

- **业务、后端、数据库、支付、实名、Cloudflare R2、邮箱、提现：** 继承 V1.1.0 功能文档与私有母版规则；真实配置只允许部署到服务器秘密存储。
- **Android 视觉、HTML、CSS、游戏素材、按钮与组件约束：** V1.3.0 是唯一有效基线，覆盖并否决 V1.2.0 Android 视觉。
- **管理后台和 H5：** 继承现有功能与页面基线，开发时按 V1.3.0 品牌色做一致性复核。
- **实际代码状态：** 尚未完成 P00—P11 业务开发，Codex 必须从 P00 开始。

V1.2.0 视觉资料已从仓库剔除，任何内容不得重新导入、引用或建立截图门禁。

## 2. 首次读取顺序

1. `README.md`
2. `00_README/PREDEV_HARDENING.md`
3. `03_SPECS/PREDEV_BASELINE.yaml`
4. `03_SPECS/SECURITY_BOUNDARY.yaml`
5. `03_SPECS/CURRENT_RELEASE.yaml`
6. `03_SPECS/RESOLVED_RULESET.yaml`
7. `03_SPECS/PROJECT_PROFILE.yaml`
8. `03_SPECS/MODULE_SELECTION.yaml`
9. `02_DOCS/星矿纪元_前后端与视觉资源完整开发文档_V1.1.0.md`
10. `02_DOCS/星矿纪元_V1.3.0_游戏视觉重建与像素级开发规范.md`
11. `03_SPECS/GAME_UI_ARCHITECTURE_V130.yaml`
12. `03_SPECS/DESIGN_TOKENS_GAME_V130.json`
13. `03_SPECS/NINE_SLICE_AND_STRETCH_RULES_V130.yaml`
14. 当前 Page ID 的 Page Spec、PNG、同名 HTML 和资源文件
15. `11_CODE_TOKENS/compose_v130`
16. `12_TESTS/V130_视觉与防变形验收清单.md`

## 3. Android 视觉事实源优先级

当文字规格、旧文件或历史示例冲突时，按以下顺序裁决：

```text
1. 04_UI/APP/<PageID>__<StateID>.png
2. 10_HTML/APP/<PageID>__<StateID>.html
3. 10_HTML/shared/styles_v130.css
4. 03_SPECS/DESIGN_TOKENS_GAME_V130.json
5. 03_SPECS/NINE_SLICE_AND_STRETCH_RULES_V130.yaml
6. 07_GAME_ASSETS/v130
7. 06_MINERS/PNG_V130 和 SVG_V130
8. 03_SPECS/pages/<PageID>.yaml
```

V1.2.0 Android PNG、HTML、CSS、Token、九宫格规则、联系表和视觉基线哈希均已作废。

## 4. 不可协商的实现规则

- 首页必须开发为 Kotlin + Jetpack Compose 原生 2D 矿场，禁止 WebView、整页截图伪装和静态背景替代交互。
- 业务模式不得擅自删除或修改：36 级矿机、主副积分、积分集市、项目推广、会员、二级提成、红包卡、账户余额与档位提现均保留。
- Android 使用真实系统状态栏；效果图中的时间、信号、电量仅是预览，不得开发成 App 组件。
- 一级 Tab 根页面不显示顶部返回按钮。
- 主按钮固定 42dp；紧凑按钮 34dp；输入框 46dp；底部导航 58dp。
- 按钮只能横向自适应父容器，不得通过非等比拉伸位图改变形状。
- 文案默认单行；长度不足时压缩间距或省略，不得撑高按钮。
- 矿机统一 `ContentScale.Fit`，保持宽高比；禁止 `FillBounds`、裁切和非等比缩放。
- 页面含底部导航时，滚动内容必须预留至少 76dp 底部安全空间。
- 模态框必须处于安全视口内，遮罩覆盖完整内容区域。
- 返回上级页面必须保留滚动、Tab、筛选、分页、展开项和草稿，禁止返回即白屏、回顶或全量重载。
- 图标必须来自 V1.3.0 SVG/PNG 资源，不得使用文字、Emoji 或 Icon Font 代替。
- 支付、实名、R2、邮箱和提现按私有母版规则集成；任何密钥、AppCode、证书或密码只能在服务器预检中以存在性和权限结果验证，禁止写入仓库或客户端。
- 所有资产、合成、领取、支付、佣金和提现操作必须由服务端最终确认，并具备事务、幂等和审计。

## 5. 截图生成和视觉门禁

只允许 Chromium/Playwright 生成网页视觉基线：

```text
python 13_SCRIPTS/render_ui_chromium_v130.py
python 13_SCRIPTS/validate_visual_v130.py
```

禁止使用：

```text
WeasyPrint
wkhtmltopdf
PDF 转 PNG
旧 V1.2.0 渲染脚本
```

Compose 真机截图最终必须与 V1.3.0 基线比较。建议门限：

```text
主要组件边界偏差 ≤ 2dp
文字基线偏差 ≤ 1dp
按钮高度偏差 = 0dp
图标尺寸偏差 ≤ 1dp
核心页面全图差异 ≤ 3%
无横向溢出、无文案裁切、无按钮变形、无导航遮挡
```

## 6. 开发顺序

仍按 `P00 → P11` 推进。

P00 只完成：环境预检、仓库事实源、模块解析、Docker/PostgreSQL/Redis、Android 壳、后台壳、资源注册、V1.3.0 Token 接入、截图测试框架。不得把设计资料误报为已开发功能。

从 P02 开始实现真实矿机拖动、移动、合成、产出和领取。每个涉及 Android 的版本必须交付：

- 正式签名 APK；
- 真机截图；
- 功能完成清单；
- 测试清单；
- 已知问题与修复记录；
- 数据库迁移与接口变更；
- 当前版本视觉差异报告。
