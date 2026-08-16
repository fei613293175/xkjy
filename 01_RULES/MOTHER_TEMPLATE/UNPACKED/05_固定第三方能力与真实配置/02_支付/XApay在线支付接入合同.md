# XApay 在线支付接入合同

> 本合同按当前项目 2026-08-16 已落地实现和 [XApay 开发文档](https://xa.2xrr.com/doc) 整理。私有 PID 和密钥以 `PRIVATE_INTEGRATIONS.yaml#payment.providers.xapay` 为准。

## 1. 已确认能力边界

| 本地方式 | XApay `type` | 展示名称 | 状态 |
|---|---|---|---|
| `ALIPAY_XAPAY` | `alipay` | 支付宝 | 已确认 |
| `WECHAT_XAPAY` | `wxpay` | 微信支付 | 已确认 |
| 在线 QQ | 未确认 | QQ 支付 | 禁止生成 |

QQ 付款使用 `QQ_QR` 人工扫码 profile。不得仅因上游文档存在相似字段就声称在线 QQ 已接通。

## 2. 固定端点与运行配置

- 页面支付：`https://xa.2xrr.com/xpay/epay/submit.php`
- 主动查单：`https://xa.2xrr.com/xpay/epay/api.php`
- 异步通知：`/api/v1/payments/callback/xapay`
- 默认生产通知：`https://x-api.orbexa.cc/api/v1/payments/callback/xapay`
- 默认支付返回页：`https://x-api.orbexa.cc/payment-return`
- 后端环境变量：`XAPAY_PID`、`XAPAY_KEY`、`XAPAY_GATEWAY`、`XAPAY_QUERY_URL`、`XAPAY_NOTIFY_URL`、`XAPAY_RETURN_URL`
- 后台运行配置：`payment.xapayEnabled`、`payment.xapayGateway`、`payment.xapayQueryUrl`、`payment.xapayNotifyUrl`、`payment.xapayReturnUrl`

项目域名变化时只替换回调和返回域名；路径、HTTPS、服务端验签和幂等要求不变。PID 与密钥禁止进入 APK、H5、管理后台静态资源、客户端网络请求、日志或异常响应。

## 3. 发起页面支付

服务端创建本地订单并锁定金额快照后，向页面支付网关提交以下字段：

| 字段 | 必填 | 来源与约束 |
|---|---:|---|
| `pid` | 是 | 服务端私有配置 |
| `type` | 是 | `alipay` 或 `wxpay` |
| `out_trade_no` | 是 | 本地全局唯一订单号 |
| `notify_url` | 是 | 自有服务端 HTTPS 回调 |
| `return_url` | 是 | 自有 H5 返回页；不发放权益 |
| `name` | 是 | 服务端商品/服务标题快照 |
| `money` | 是 | 服务端计算，十进制元，两位小数 |
| `clientip` | 是 | 服务端解析后的客户端 IP |
| `device` | 是 | App 默认 `mobile` |
| `sign_type` | 是 | 固定 `MD5` |
| `sign` | 是 | 按本合同计算 |

服务端返回 `paymentUrl` 给 App。App 只能打开经过协议白名单和域名校验的 URL，回到前台后查询自有后端订单，不直接相信浏览器成功页。

## 4. MD5 签名

1. 移除 `sign`、`sign_type` 和值为空的字段。
2. 按参数名 ASCII 升序排序。
3. 拼接为 `a=b&c=d`，签名前的值不做 URL 编码。
4. 在拼接串末尾直接追加 XApay 密钥。
5. 计算 MD5，输出小写 32 位十六进制。

```text
plain = join('&', sort(non_empty(params - sign - sign_type))) + XAPAY_KEY
sign = lower_hex(md5(plain))
```

签名比较使用固定长度校验和 timing-safe compare；缺少 PID/Key 时健康检查必须报告未就绪，禁止带空密钥发起支付。

## 5. 回调

XApay 以查询参数通知服务端，至少核验：

- MD5 签名；
- `pid` 等于当前项目配置；
- `out_trade_no` 存在且属于 XApay 支付尝试；
- `money` 与订单金额精确到分一致；
- 成功状态为上游明确成功值；
- `trade_no` 未绑定到其他订单。

验签与核对成功后，在数据库事务中锁定订单、记录支付事件、标记已支付、调用统一业务结算器、写权益和返佣幂等记录。重复通知返回纯文本 `success`，但不得重复发放。失败返回 `fail` 并记录脱敏错误，不能记录原始密钥或签名串。

## 6. 主动查单与补偿

App 回前台、支付中订单定时任务和后台“查单”都调用自有后端；自有后端再请求 XApay 查单端点。查单结果必须核对 PID、订单号、金额和状态，成功后复用同一结算事务。网络超时、非 JSON、签名/字段不完整只能保持待确认，不能直接判成功或再次发放。

## 7. 上线门禁

- 环境变量存在且不在前端构建产物；
- 网关、查单、通知和返回地址均为 HTTPS；
- 两种已确认方式分别完成创建、跳转、取消、回前台查单；
- 错误签名、错误 PID、错金额、错订单号和重复回调均被拒绝或幂等；
- 回调与主动查单并发时只结算一次；
- 真实资金测试必须使用项目所有者明确授权的订单和金额。
