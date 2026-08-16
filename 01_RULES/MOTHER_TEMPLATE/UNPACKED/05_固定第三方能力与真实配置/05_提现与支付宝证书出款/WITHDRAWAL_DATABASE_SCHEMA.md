# 提现数据库模式

表名可按项目命名规范调整，但约束语义不可删减。

## `withdrawal_methods`

| 字段 | 约束 |
|---|---|
| `user_id` | 唯一外键 |
| `provider` | 固定 `ALIPAY` |
| `real_name_cipher` | 非空，服务端实名姓名带认证加密 |
| `account_cipher` | 非空，支付宝账号带认证加密 |
| `real_name_masked` / `account_masked` | 列表安全展示 |
| `version` / `updated_at` | 乐观锁和审计 |

## `withdrawal_tiers`

`amount NUMERIC(18,2)` 必须大于 0 且唯一；可包含固定手续费、单档累计上限、启停、排序和版本。不能用整数列承载小额档位，也不能把金额从字符串经整数解析。

## `withdrawals`

核心字段：

- 业务：`request_no`、`user_id`、`tier_id`、`amount`、`fee`、`net_amount`、`status`、`version`；
- 幂等：`idempotency_key` 与 `(user_id, idempotency_key)` 唯一约束、`event_id`；
- 快照：`real_name_masked`、`account_masked`、`payout_real_name_cipher`、`payout_account_cipher`、`config_snapshot JSONB`；
- 出款：`payout_mode`、`payout_provider`、`payout_request_no`、`payout_attempts`、`payout_requested_at`；
- 响应：`payment_reference`、`payout_response_code`、`payout_response_message`、`payout_failure_reason`；
- 对账：`payout_reconciliation_status`、`last_reconciled_at`、`next_reconcile_at`；
- 审核：`reviewed_by`、`reviewed_at`、`reason`、`paid_at`、时间戳。

约束与索引：

- `net_amount = amount - fee`，三者使用同一精度；
- `payout_request_no` 非空时全局唯一；
- `payout_mode IN ('AUTO','MANUAL')`；
- 状态和对账状态使用 CHECK 或数据库枚举；
- 为 `(user_id, created_at)`、`(status, created_at)`、待对账 `next_reconcile_at` 建索引；
- 历史出款快照创建后不可通过普通更新接口修改。

## 账本

钱包账户至少区分 `available` 与 `frozen`。账本类型至少包含：

- `WITHDRAWAL_FROZEN`：可用减少、冻结增加；
- `WITHDRAWAL_PAID`：冻结减少，外部资金已确认支付；
- `WITHDRAWAL_RETURN`：冻结减少、可用恢复。

每类使用 `withdrawal:{action}:{withdrawal_id}` 唯一幂等键。数据库约束必须保证一个提现订单只有一个冻结事件和一个终态账本事件。

## 配置键

- `withdrawal.enabled`
- `withdrawal.dailyMaxCount`
- `withdrawal.restoreDailyCountAfterReturn`
- `withdrawal.minimumRemainingBalance`
- `withdrawal.autoPayoutEnabled`
- `withdrawal.autoPayoutLimit`
- `withdrawal.payoutReason`
- `withdrawal.payoutRemark`
- `withdrawal.rule`
- `withdrawal.businessTimezone`

配置表应保存类型、版本、更新人和更新时间；保存档位与配置必须同事务，不能因一个无效字段造成部分更新。
