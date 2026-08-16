# 星矿纪元

`xkjy` 是《星矿纪元》的专属开发仓库。当前提交为 `V1.3.0-PREDEV-HARDENED`：它提供从 P00 开始的业务、视觉、资源、接口和数据基线，但不代表 Android、后端、后台或 H5 已开发完成。

## 当前状态

- 当前开发阶段：`P00`。
- 实际业务代码：未开始。
- Android 视觉事实源：V1.3.0。
- 业务规则基线：V1.1.0。
- 私有母版规则基线：V1.4.2。
- 允许的构建、部署和非设备测试位置：已连接的服务器。

开始任何工程工作前，先阅读：

1. `00_README/README_交给Codex.md`
2. `00_README/PREDEV_HARDENING.md`
3. `03_SPECS/PREDEV_BASELINE.yaml`
4. `03_SPECS/CURRENT_RELEASE.yaml`
5. `03_SPECS/RESOLVED_RULESET.yaml`

## 仓库安全边界

本仓库不保存真实密钥、私钥、证书、支付凭据或私有母版 ZIP。运行时配置只允许放在服务器的受控秘密目录或 Secret 管理系统中。禁止将这些数据写入 Git、客户端、前端构建产物、日志或截图。详细规则见 `SECURITY.md`。

## 视觉与交付

Android 视觉基线只使用 `04_UI/APP`、`10_HTML/APP`、`10_HTML/shared/styles_v130.css`、V1.3.0 令牌与资源。V1.2.0 资料没有进入本仓库，不能作为开发或验收依据。

P00 之后的每个 Android 版本必须在真实 Android 设备安装、启动、完整操作并留存截图和日志证据；未完成服务端验证、真机测试和视觉门禁不得标记为完成。
