# 进度追踪与监控

## Parent

基于 `speces/agent-prd.md` 开放问题拆分

## What to build

实现进度追踪和监控系统：
- 每阶段状态记录
- 执行日志记录
- 失败告警
- 可视化监控面板（可选）

## Acceptance criteria

- [ ] 实现阶段状态记录：
  - `collector_started` / `collector_completed`
  - `analyzer_started` / `analyzer_completed`
  - `organizer_started` / `organizer_completed`
- [ ] 实现结构化日志记录（JSON 格式）
- [ ] 实现失败告警：Telegram/飞书通知
- [ ] 实现执行报告：每日摘要
- [ ] 可选：Grafana 监控面板
- [ ] 文档：监控指标说明

## Blocked by

- Issue #004 (调度器每日定时触发)

## Technical Notes

**状态文件格式**：

```json
{
  "run_id": "20260503_000000",
  "status": "running",
  "stages": {
    "collector": {
      "status": "completed",
      "started_at": "2026-05-03T00:00:00Z",
      "completed_at": "2026-05-03T00:02:30Z",
      "items_collected": 25
    },
    "analyzer": {
      "status": "running",
      "started_at": "2026-05-03T00:02:31Z"
    },
    "organizer": {
      "status": "pending"
    }
  }
}
```

**告警消息示例**：
```
🚨 [知识库] 采集任务失败
日期: 2026-05-03
阶段: collector
错误: GitHub API rate limit exceeded
影响: 无法采集今日数据
```

**监控指标**：
- 采集成功率
- 分析成功率
- 平均执行时间
- 错误类型分布
