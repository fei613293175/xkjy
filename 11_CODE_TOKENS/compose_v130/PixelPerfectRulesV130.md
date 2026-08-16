# Compose 像素级实现约束 V1.3.0

1. 视觉基准为 360×760dp，基线截图为 1080×2280px（3×）。
2. `WindowInsets.statusBars` 与 `WindowInsets.navigationBars` 由系统处理；效果图中的 11:29/5G/89% 仅是设备预览，不得绘制成 App 组件。
3. 一级 Tab 根页面不显示返回按钮；底部五个 Tab 各自保存独立 back stack、滚动位置和筛选条件。
4. 所有按钮使用 Compose Shape + Gradient，不使用整张按钮位图，不使用 `ContentScale.FillBounds`。
5. 矿机使用透明 PNG/SVG，固定容器尺寸，`ContentScale.Fit`，禁止非等比缩放。
6. 文字按钮必须单行；宽度不足时优先调整布局，不允许压扁图标或纵向拉伸按钮。
7. 列表最后一项必须避开底部导航，滚动容器底部保留至少 76dp。
8. 页面状态必须产生可见差异；不得只改文件名而复用同一截图。
