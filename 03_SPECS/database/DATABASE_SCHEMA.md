# 星矿纪元数据库设计目录

## 设计原则

- PostgreSQL；金额和积分使用 `NUMERIC`。
- 所有钱包变化通过 `wallet_transactions + wallet_entries`，禁止直接改余额。
- 支付、合成、领取、转赠、佣金、提现均有唯一幂等键。
- 状态变化保留事件或时间线，不物理覆盖审计历史。
- 私有配置只以环境变量或服务器秘密文件注入。

## 账号与用户

- `users`
- `user_profiles`
- `user_identifiers`
- `password_credentials`
- `user_sessions`
- `email_verification_codes`
- `login_attempts`
- `user_restrictions`
- `account_deletion_requests`

## 邀请会员

- `referral_relations`
- `referral_closure`
- `membership_plans`
- `user_memberships`

## 游戏

- `miner_level_configs`
- `user_game_profiles`
- `user_miners`
- `user_board_slots`
- `user_warehouse_slots`
- `miner_purchase_daily_counters`
- `miner_events`
- `production_settlements`
- `production_claims`
- `user_atlas_entries`
- `task_templates`
- `user_task_progress`
- `sign_in_configs`
- `user_sign_in_records`
- `supply_box_configs`
- `supply_box_drop_items`
- `user_supply_boxes`
- `supply_box_openings`
- `ranking_snapshots`
- `game_resource_versions`

## 资产

- `wallet_accounts`
- `wallet_transactions`
- `wallet_entries`
- `point_exchange_orders`
- `point_transfer_orders`
- `transfer_password_credentials`
- `asset_adjustment_orders`

## 价格市场

- `point_price_rules`
- `point_price_history`
- `market_buy_orders`
- `market_order_contacts`
- `market_order_reports`
- `market_order_audits`

## 项目

- `project_categories`
- `projects`
- `project_images`
- `project_contacts`
- `project_review_records`
- `project_favorites`
- `project_reports`
- `promotion_service_configs`
- `project_promotion_usages`
- `project_task_campaigns`
- `project_task_sessions`
- `project_task_heartbeats`
- `project_task_rewards`

## 商城订单

- `mall_categories`
- `mall_products`
- `mall_product_payment_methods`
- `orders`
- `order_items`
- `order_price_snapshots`
- `user_entitlements`
- `promotion_card_inventory`
- `promotion_card_ledger`
- `red_packet_card_records`

## 支付

- `payment_method_configs`
- `payment_orders`
- `payment_attempts`
- `payment_events`
- `xapay_requests`
- `xapay_callbacks`
- `manual_qr_codes`
- `manual_qr_sessions`
- `manual_payment_submissions`
- `manual_payment_reviews`
- `payment_reconciliation_records`
- `payment_settlement_records`

## 佣金

- `point_commission_rules`
- `cash_commission_rules`
- `commission_records`
- `commission_reversals`
- `commission_risk_holds`

## 实名

- `identity_configs`
- `identity_sessions`
- `identity_captures`
- `identity_provider_requests`
- `identity_results`
- `identity_manual_actions`
- `identity_bindings`

## 提现

- `withdrawal_configs`
- `withdrawal_tiers`
- `user_payment_accounts`
- `withdrawal_orders`
- `withdrawal_state_histories`
- `withdrawal_review_records`
- `withdrawal_payout_attempts`
- `withdrawal_provider_queries`
- `withdrawal_reconciliation_records`

## 平台

- `file_objects`
- `file_bindings`
- `file_operation_logs`
- `email_templates`
- `email_send_jobs`
- `email_send_logs`
- `captcha_challenges`
- `captcha_tickets`
- `notifications`
- `notification_reads`
- `announcements`
- `feedback_tickets`
- `admin_users`
- `admin_roles`
- `admin_permissions`
- `admin_role_permissions`
- `admin_operation_audits`
- `runtime_configs`
- `app_releases`
- `scheduled_job_runs`
- `outbox_events`
- `service_health_records`

