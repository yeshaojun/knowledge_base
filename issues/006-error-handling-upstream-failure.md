# 错误处理策略 - 上游失败处理

## Parent

基于 `speces/agent-prd.md` 开放问题拆分

## What to build

设计并实现上游失败时下游的处理策略：
- Collector 失败 → Analyzer 如何处理
- Analyzer 失败 → Organizer 如何处理
- 重试机制和降级策略

## Acceptance criteria

- [ ] 设计错误处理策略文档
- [ ] 实现重试机制：指数退避，最多 3 次
- [ ] 实现降级策略：部分数据失败时继续处理成功的部分
- [ ] 实现告警通知：失败时发送通知
- [ ] 错误日志记录：结构化日志，便于排查
- [ ] 单元测试覆盖错误处理逻辑

## Blocked by

- Issue #004 (调度器每日定时触发) - 需要调度器框架

## Technical Notes

**错误类型分类**：
1. **网络错误**：重试
2. **解析错误**：跳过当前条目，记录日志
3. **配置错误**：立即失败，发送告警

**降级策略示例**：
- Collector 部分失败 → 返回成功采集的数据
- Analyzer 失败 → Organizer 保留未分析的原始数据

**通知渠道**：
- Telegram Bot
- 飞书 Bot

---

**Type: HITL** - 需要人工审核策略
