# Cloudflare R2 对象存储接口与配置

> 作用域：仅当 `storage.resolved_enabled: true` 时进入项目，或作为实名认证的自动依赖启用。

真实测试值位于上级 `PRIVATE_INTEGRATIONS.yaml` 和 `.env`。

## 已有信息

- 存储桶：`fuylink`
- S3 兼容 Endpoint；
- 自定义访问域：`oss.orbexa.cc`；
- Account Token；
- Access Key ID；
- Secret Access Key；
- 原始资料记录的默认管辖区信息。

## 统一实现

- 仅后端持有 R2 凭据；
- Android 和管理后台前端通过自有后端获取上传授权或由后端代传；
- 文件表保存对象键、桶、业务类型、用户、大小、MIME、哈希、状态、创建和删除时间；
- 上传前校验类型、大小和业务权限；
- 上传成功后再绑定业务对象；
- 删除业务对象时按项目策略处理文件；
- 后台提供文件查询、预览、删除、日志和孤立文件清理；
- 实名照片和视频按专用路径和权限处理，不在 App 本地持久保存。
