# 图形验证码服务端存储结构

优先复用项目已有缓存；无缓存时可使用短期数据库表。不得为了验证码单独强制引入 Redis。

## challenge 最小字段

- `challenge_id`：不可预测的随机标识；
- `purpose`：登录、注册、找回、发送验证码、后台登录等；
- `answer_hash` 与 `salt`：不可逆保存；
- `anonymous_session_id` 或设备摘要；
- `target_hash`：邮箱/手机号等目标的摘要，可为空；
- `attempt_count`、`max_attempts`；
- `expires_at`；
- `verified_at`、`invalidated_at`；
- `created_at`。

## ticket 最小字段

- `ticket_id` 或票据摘要；
- `purpose`；
- `challenge_id`；
- `anonymous_session_id` 或设备摘要；
- `target_hash`；
- `expires_at`；
- `consumed_at`；
- `created_at`。

答案、输入内容和完整目标标识不得进入日志。过期 challenge 和 ticket 必须定时清理。使用数据库时应为 `expires_at`、`purpose` 和状态建立必要索引。
