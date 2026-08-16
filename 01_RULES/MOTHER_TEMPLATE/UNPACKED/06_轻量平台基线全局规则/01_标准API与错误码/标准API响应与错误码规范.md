# 标准 API 响应与错误码规范

## 统一响应

```json
{
  "code": "SUCCESS",
  "message": "操作成功",
  "data": {},
  "request_id": "req_xxx",
  "server_time": 1786500000
}
```

- `code` 为稳定业务错误码，不随文案变化；
- `message` 为适合用户或调用方理解的中文提示；
- `request_id` 贯穿 App、后台、后端和日志；
- 时间统一说明时区和格式；金额使用最小货币单位或明确小数精度。

## 最小错误分类

- `AUTH_REQUIRED`：需要登录；
- `PERMISSION_DENIED`：无权限；
- `RESOURCE_NOT_FOUND`：资源不存在；
- `STATE_CONFLICT`：业务状态冲突；
- `VALIDATION_ERROR`：字段校验失败；
- `RATE_LIMITED`：操作过于频繁；
- `CAPTCHA_REQUIRED` / `CAPTCHA_INVALID` / `CAPTCHA_EXPIRED`；
- `INTEGRATION_ERROR`：第三方服务异常；
- `INTERNAL_ERROR`：系统异常。

前端不得直接展示数据库、框架堆栈、第三方密钥或内部 URL。字段错误应可精确绑定到输入控件。

## 接口合同

每个 API 必须记录 API ID、Page ID、鉴权、角色、对象级权限、请求字段、响应、错误码、频控、验证码用途、幂等键、数据表、配置、日志和测试。项目应生成 OpenAPI 或等价机器可读合同，但不得因此引入复杂文档平台。
