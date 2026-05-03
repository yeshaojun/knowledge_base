# 数据传递机制设计

## Parent

基于 `speces/agent-prd.md` 开放问题拆分

## What to build

设计并决策 Agent 间数据传递方式：
- 评估文件传递 vs 消息队列
- 编写 ADR (Architecture Decision Record)
- 实现选定的传递机制

## Acceptance criteria

- [ ] 评估方案：文件传递 vs 消息队列（Redis/RabbitMQ）
- [ ] 编写 ADR 文档：`docs/adr/0001-data-transfer-mechanism.md`
- [ ] 决策因素：可靠性、性能、复杂度
- [ ] 实现选定的传递机制
- [ ] 更新相关 Agent 定义文档

## Blocked by

None - can start immediately (设计决策)

## Technical Notes

**文件传递方案**：
- 优点：简单、可调试、无额外依赖
- 缺点：需要文件锁、跨机器部署受限

**消息队列方案**：
- 优点：可靠、支持重试、跨机器
- 缺点：增加依赖、复杂度高

当前实现：文件传递（`knowledge/raw/` 和 `knowledge/articles/`）

---

**Type: HITL** - 需要人工审核和决策
