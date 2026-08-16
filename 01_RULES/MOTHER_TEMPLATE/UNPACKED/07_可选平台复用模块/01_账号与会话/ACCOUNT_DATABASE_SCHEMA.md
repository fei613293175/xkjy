# 账号模块数据库设计

建议最小表：

- `users`：UID、状态、昵称、创建时间、注销状态；
- `user_login_identifiers`：邮箱/手机号/用户名、规范化值、验证状态和唯一约束；
- `user_password_credentials`：密码哈希、算法、更新时间；
- `user_sessions`：设备、Refresh Token 摘要、状态、过期和撤销；
- `verification_code_records`：用途、目标摘要、验证码哈希、次数、过期和消费状态；
- `password_recovery_tokens`：一次性令牌摘要、目标用户、过期和消费；
- `user_login_logs`：成功/失败、设备、IP 摘要、App 版本、错误码；
- `account_status_history`：冻结、解封、注销等状态变更；
- 图形验证码记录按全局验证码规范使用现有缓存或短期数据库表。

所有账号标识必须规范化后建立唯一约束。密码、业务验证码、Refresh Token 和找回令牌只保存不可逆摘要。表结构需按项目实际登录方式裁剪。
