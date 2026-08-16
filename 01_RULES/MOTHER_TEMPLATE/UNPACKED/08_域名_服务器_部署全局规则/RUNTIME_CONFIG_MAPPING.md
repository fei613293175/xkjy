# 运行配置映射

ChatGPT 根据 `RESOLVED_RULESET.yaml` 生成：

```text
PROJECT_RUNTIME.env
PROJECT_INTEGRATIONS_RESOLVED.yaml
PROJECT_PLATFORM_BASELINE.yaml
PROJECT_GENERATED_SECRETS.yaml
```

规则：

1. 五项固定第三方能力只从 `PRIVATE_INTEGRATIONS.yaml` 抽取已启用模块所需字段；提现证书文件从其 `PRIVATE_CREDENTIALS` 目录按需复制；
2. 轻量平台基线和账号模块的非密钥默认值从对应 YAML 生成，不需要重复询问；
3. 自研图形验证码不需要第三方密钥，但需要项目内部 `CAPTCHA_HMAC_SECRET`；Codex 在服务器首次初始化时自动生成至少 32 字节随机值，不得向用户索取；
4. 技术方案使用签名 Token 或框架要求独立 CSRF 密钥时，同样由 Codex按 `GENERATED_RUNTIME_SECRETS_TEMPLATE.yaml` 自动生成；
5. 项目内部生成密钥必须跨版本稳定保留，不能每次构建重新生成；
6. 关闭模块不复制对应第三方配置，自动依赖模块必须复制必要配置；
7. 运行配置只进入私有项目包和服务器，不进入 APK、管理后台前端、H5 静态资源或公开仓库；
8. 配置测试失败时记录明确错误证据，不重新询问已经存在的第三方值；
9. 提现启用时为收款快照生成项目独立加密密钥，稳定保留；证书以只读 Secret 挂载，初次部署保持底层通道关闭直至预检通过；
10. 证书材料存在不代表支付宝权限、余额和风控长期有效；这些属于部署时可核验外部状态，不得在文档阶段重复索取材料或无条件保证到账。
