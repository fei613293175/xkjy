# Android 签名、版本与最小在线更新规范

## 首版必须固定

- `applicationId`；
- 正式 keystore、alias 和证书指纹；
- keystore 的服务器受限路径和独立备份；
- `versionCode` 递增规则；
- `versionName`；
- JDK、Gradle、AGP、Kotlin 和 Compose 版本；
- APK SHA-256 和对应 Git Commit。

不得每个版本重新生成签名。签名密码不得进入 APK、前端或公开仓库。

## 最小更新能力

App 启动按缓存周期检查版本，并在“关于”页支持手动检查。后台可发布：版本号、APK 地址、大小、SHA-256、更新说明、发布时间、可选/强制更新和最低可用版本。App 支持下载进度、失败重试、哈希校验和安装权限提示。

第一版不强制灰度比例、用户分群、A/B、多渠道包和自动回滚平台。项目明确需要时再扩展。
