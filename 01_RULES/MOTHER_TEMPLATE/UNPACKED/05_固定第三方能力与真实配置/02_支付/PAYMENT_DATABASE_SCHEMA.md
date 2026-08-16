# 支付数据结构合同

以下是逻辑结构，字段类型按项目数据库映射。金额必须使用定点十进制，禁止浮点数。

## `payment_business_orders`

统一业务支付订单：`id`、`out_trade_no UNIQUE`、`user_id`、`business_type`、`business_id`、`order_kind`、`title`、`amount DECIMAL`、`currency`、`status`、`selected_method`、商品/价格快照、`expires_at`、`paid_at`、`entitlement_granted_at`、`version`、时间戳。

`order_kind` 创建后不可由客户端修改；所有 provider 和人工扫码结算都使用同一订单。

## `payment_method_configs`

`code PRIMARY KEY`、`display_name`、`description`、`enabled`、`sort_order`、`provider`、`allowed_business_types JSON`、`hidden_order_kinds JSON NOT NULL DEFAULT []`、`version`、更新人和时间。

方式代码至少包括：

- 富运：`ALIPAY`、`WECHAT`、`USDT`；
- XApay：`ALIPAY_XAPAY`、`WECHAT_XAPAY`；
- 扫码：`ALIPAY_QR`、`WECHAT_QR`、`QQ_QR`。

如果项目保留余额支付，`BALANCE` 仍走内部钱包事务，不属于第三方 provider。

## `payment_attempts`

每次在线发起：`id`、`payment_order_id`、`user_id`、`provider`、`provider_trade_no UNIQUE NULLABLE`、`payment_method`、`amount`、`status`、`provider_payment_url`、`expire_at`、请求/响应脱敏摘要和时间戳。

同一订单可有多次 attempt，但任何 attempt 成功后订单只能结算一次。

## `payment_events`

追加式事件：`id`、`payment_order_id`、`payment_attempt_id NULLABLE`、`event_type`、`status`、`error_code`、`idempotency_key UNIQUE NULLABLE`、`payload JSON`、时间戳。

人工扫码事件至少包含 `MANUAL_QR_OPENED`、`MANUAL_QR_SUBMITTED`、`MANUAL_QR_APPROVED`、`MANUAL_QR_REJECTED`。

## `payment_qr_codes`

`id UUID PRIMARY KEY`、`method_code`、`file_id UNIQUE`、`label`、`active`、`sort_order`、时间戳。`method_code` 只允许 `ALIPAY_QR`、`WECHAT_QR`、`QQ_QR`。

索引：`(method_code, active, sort_order)`。被历史订单引用后只停用，不级联删除文件。

## `manual_payment_submissions`

`id UUID PRIMARY KEY`、`payment_order_id UNIQUE`、`user_id`、`payment_method`、`qr_code_id NULLABLE`、`screenshot_file_id`、`status`、`review_reason`、`reviewed_by`、`reviewed_at`、`version`、时间戳。

状态只允许 `PENDING_REVIEW`、`APPROVED`、`REJECTED`。索引：`(status, created_at DESC)`、`(user_id, created_at DESC)`。

## `file_objects`

支付相关 `business_type` 增加 `PAYMENT_QR`、`PAYMENT_SCREENSHOT`。保存 bucket、object_key、owner、business_id、MIME、大小、SHA-256、状态和绑定时间。二维码文件 owner 为空或管理员主体；付款截图 owner 必须为订单用户。

## 权益和返佣幂等

- 权益记录唯一键：`payment_order_id + benefit_type`；
- 返佣记录唯一键：`source_payment_order_id + beneficiary_user_id + commission_type`；
- 订单完成、权益发放、返佣入账、人工提交通过和支付事件必须在同一事务内提交；
- 回调、主动查单和人工审核不得各自复制业务发放代码，只调用同一 `settlePaidOrder` 服务。

## 迁移要求

1. 迁移前按全局数据库规范备份并记录恢复点。
2. 新字段使用兼容默认值；`hidden_order_kinds` 默认为空数组，不能改变现有支付方式可见性。
3. 先建表/列/索引和枚举，再部署兼容新旧结构的后端，最后开放后台与 App。
4. 回滚只能关闭新增支付方式和入口；不得删除已经产生的订单、付款截图、权益或返佣记录。
